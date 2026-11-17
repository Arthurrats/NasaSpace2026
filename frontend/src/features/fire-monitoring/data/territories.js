import { geoArea, geoBounds } from 'd3-geo';
import { feature } from 'topojson-client';
import codes from 'i18n-iso-countries/codes.json';

const names = new Intl.DisplayNames('pt-BR', { type: 'region' });
const englishNames = new Intl.DisplayNames('en', { type: 'region' });
const labels = { country: 'País', state: 'Estado', city: 'Cidade' };
const earthRadiusKm = 6371.0088;
const mercatorLimit = 85.05112878;

export function normalizePlaceQuery(value) {
  return value.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim().replace(/\s+/g, ' ');
}

const countries = codes.map(([code, , numericId]) => {
  const name = names.of(code);
  const englishName = englishNames.of(code);
  return { id: 'country-' + code, kind: 'country', code, numericId, name, englishName, label: labels.country,
    searchNames: [name, englishName, code].map(normalizePlaceQuery) };
});

export function matchCountries(query) {
  const term = normalizePlaceQuery(query);
  return countries.filter(({ searchNames: [local, english, code] }) =>
    local.startsWith(term) || english.startsWith(term) || code === term,
  );
}

const suggestionCache = new Map();
const boundaryCache = new Map();

function remember(cache, key, value, limit) {
  cache.delete(key);
  cache.set(key, value);
  if (cache.size > limit) cache.delete(cache.keys().next().value);
}

export function cachedSuggestions(query) {
  return suggestionCache.get(normalizePlaceQuery(query));
}

export async function autocompleteTerritories(query, signal) {
  const matches = await searchTerritories(query, signal);
  signal.throwIfAborted();
  remember(suggestionCache, normalizePlaceQuery(query), matches, 80);
  return matches;
}

export function rankTerritories(query, remote) {
  const term = normalizePlaceQuery(query);
  const matches = new Map([...remote, ...matchCountries(query)].map(place => [place.id, place]));
  const rank = ({ name, searchNames = [normalizePlaceQuery(name)] }) => {
    if (searchNames.includes(term)) return 2;
    return Number(searchNames.some(name => name.startsWith(term)));
  };
  const ranked = [...matches.values()].sort((a, b) => rank(b) - rank(a));
  const firstByType = new Set(Object.keys(labels).map(kind => ranked.find(place => place.kind === kind)));
  firstByType.delete(undefined);
  const visible = new Set([...firstByType, ...ranked].slice(0, 8));
  return ranked.filter(place => visible.has(place));
}

async function fetchJson(url, signal) {
  const response = await fetch(url, { signal: AbortSignal.any([signal, AbortSignal.timeout(12000)]) });
  if (!response.ok) throw new Error('Serviço geográfico indisponível.');
  return response.json();
}

export async function searchTerritories(query, signal, layers = Object.keys(labels), code) {
  const params = new URLSearchParams({ q: query, limit: '12' });
  if (code) params.set('countrycode', code);
  for (const layer of layers) params.append('layer', layer);
  const data = await fetchJson('https://photon.komoot.io/api?' + params, signal);
  const matches = new Map();

  for (const { properties: place } of data.features ?? []) {
    if (!place?.name || !Object.hasOwn(labels, place.type) || place.osm_type !== 'R' ||
      !Number.isSafeInteger(place.osm_id) || !place.extent) continue;
    const country = place.countrycode ? names.of(place.countrycode) : place.country;
    const name = place.type === 'country' ? country || place.name : place.name;
    const context = place.type === 'country' ? '' :
      [...new Set([place.type === 'city' ? place.state : '', country])].filter(Boolean).join(', ');
    const id = place.type === 'country' && place.countrycode ? 'country-' + place.countrycode : 'osm-' + place.osm_id;
    if (!matches.has(id)) {
      matches.set(id, { id, kind: place.type, name, label: labels[place.type], context, osmId: place.osm_id });
    }
  }
  return [...matches.values()];
}

function polygonCoordinates(geometry) {
  switch (geometry?.type) {
    case 'Polygon': return [geometry.coordinates];
    case 'MultiPolygon': return geometry.coordinates;
    case 'GeometryCollection': return geometry.geometries.flatMap(polygonCoordinates);
    default: return [];
  }
}

export function describeTerritory(geometry) {
  // D3 uses clockwise exterior rings for polygons smaller than a hemisphere.
  const coordinates = polygonCoordinates(geometry).map(polygon => polygon.map((ring, index) => {
    const clockwise = geoArea({ type: 'Polygon', coordinates: [ring] }) < 2 * Math.PI;
    return clockwise === (index === 0) ? ring : [...ring].reverse();
  }));
  if (!coordinates.length) throw new Error('Contorno administrativo indisponível.');

  const polygon = { type: 'MultiPolygon', coordinates };
  const area = geoArea(polygon) * earthRadiusKm ** 2;
  let [[west, south], [east, north]] = geoBounds(polygon);
  if (west === -180 && east === 180 && south > -90 && north < 90) {
    // Natural Earth splits some islands at the date line. Measure them away from that seam.
    const turn = longitude => longitude < 0 ? longitude + 180 : longitude - 180;
    const rotated = coordinates.map(part => part.map(ring => ring.map(([lon, lat]) => [turn(lon), lat])));
    const [[rotatedWest], [rotatedEast]] = geoBounds({ ...polygon, coordinates: rotated });
    if (rotatedWest !== -180 || rotatedEast !== 180) {
      west = turn(rotatedWest);
      east = turn(rotatedEast);
    }
  }
  const bounds = [[west, Math.max(south, -mercatorLimit)], [east, Math.min(north, mercatorLimit)]];
  if (!Number.isFinite(area) || area <= 0 || bounds[0][1] >= bounds[1][1] || west === east) {
    throw new Error('Contorno administrativo inválido.');
  }
  return { geometry: polygon, outline: { type: 'MultiLineString', coordinates: coordinates.flat() }, bounds, area };
}

async function loadOsmBoundary(id, signal) {
  const geometry = await fetchJson('https://polygons.openstreetmap.fr/get_geojson.py?id=' + id, signal);
  return { ...describeTerritory(geometry), source: 'osm' };
}

export async function loadTerritory(place, signal) {
  const cached = boundaryCache.get(place.id);
  if (cached) return cached;
  const boundary = await fetchTerritory(place, signal);
  signal.throwIfAborted();
  remember(boundaryCache, place.id, boundary, 12);
  return boundary;
}

async function fetchTerritory(place, signal) {
  if (place.numericId) {
    const { default: atlas } = await import('world-atlas/countries-50m.json');
    signal.throwIfAborted();
    const shape = atlas.objects.countries.geometries.find(({ id }) => id === place.numericId);
    if (shape) {
      return { ...describeTerritory(feature(atlas, shape).geometry), source: 'natural-earth' };
    }
    const results = await searchTerritories(place.englishName, signal, ['country'], place.code);
    const match = results.find(({ id }) => id === place.id);
    if (match) return loadOsmBoundary(match.osmId, signal);
  }
  if (place.osmId) return loadOsmBoundary(place.osmId, signal);
  throw new Error('Contorno administrativo indisponível.');
}

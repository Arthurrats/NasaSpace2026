export const quadrants = [
  { id: 'nw', name: 'Noroeste', bounds: [[-180, 0], [0, 85]] },
  { id: 'ne', name: 'Nordeste', bounds: [[0, 0], [180, 85]] },
  { id: 'sw', name: 'Sudoeste', bounds: [[-180, -85], [0, 0]] },
  { id: 'se', name: 'Sudeste', bounds: [[0, -85], [180, 0]] },
];

const registeredTerritories = new WeakMap();

async function registerTerritory({ geometry, bounds }, signal) {
  const [[west], [east]] = bounds;
  const response = await fetch('/api/map/territories', {
    method: 'POST', signal, headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ geometry, seam: west > east ? (west + east) / 2 : null }),
  });
  if (!response.ok) throw new Error('Não foi possível usar o contorno do território.');
  const { id } = await response.json();
  registeredTerritories.set(geometry, id);
  return id;
}

export async function loadTileLayer(viewport, { sensor, country, startDate, endDate, layer, metric, clip, territory }, signal) {
  const search = new URLSearchParams({ sensor, country, start_date: startDate, end_date: endDate });
  if (layer === 'heat') {
    search.set('layer', 'heat');
    search.set('metric', metric ?? 'detections');
  }
  if (clip) search.set('clip', clip.flat().join(','));
  search.set('format', 'count');
  if (viewport) search.set('bbox', viewport.flat().join(','));
  if (territory) {
    const id = registeredTerritories.get(territory.geometry) ?? await registerTerritory(territory, signal);
    search.set('territory', id);
  }
  const requestCount = () => fetch('/api/map/foci?' + search, { signal, cache: 'no-cache' });
  let response = await requestCount();
  if (territory && response.status === 404) {
    search.set('territory', await registerTerritory(territory, signal));
    response = await requestCount();
  }
  if (!response.ok) throw new Error('Não foi possível consultar os focos na API.');
  const payload = await response.json();
  if (!Number.isInteger(payload.total) || typeof payload.revision !== 'string') throw new Error('A API retornou um formato de dados inválido.');
  search.delete('format');
  search.delete('bbox');
  search.set('v', payload.revision);
  return { version: response.headers.get('ETag'), total: payload.total, points: { tileQuery: search.toString() } };
}

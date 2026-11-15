export const quadrants = [
  { id: 'nw', name: 'Noroeste', bounds: [[-180, 0], [0, 85]] },
  { id: 'ne', name: 'Nordeste', bounds: [[0, 0], [180, 85]] },
  { id: 'sw', name: 'Sudoeste', bounds: [[-180, -85], [0, 0]] },
  { id: 'se', name: 'Sudeste', bounds: [[0, -85], [180, 0]] },
];

export async function loadTileLayer(viewport, { sensor, country, startDate, endDate, layer, metric, clip }, signal) {
  const search = new URLSearchParams({ sensor, country, start_date: startDate, end_date: endDate });
  if (layer === 'heat') {
    search.set('layer', 'heat');
    search.set('metric', metric ?? 'detections');
  }
  if (clip) search.set('clip', clip.flat().join(','));
  const tileParams = new URLSearchParams(search);
  search.set('format', 'count');
  if (viewport) search.set('bbox', viewport.flat().join(','));
  const response = await fetch('/api/map/foci?' + search, { signal, cache: 'no-cache' });
  if (!response.ok) throw new Error('Não foi possível consultar os focos na API.');
  const payload = await response.json();
  if (!Number.isInteger(payload.total) || typeof payload.revision !== 'string') throw new Error('A API retornou um formato de dados inválido.');
  tileParams.set('v', payload.revision);
  return { version: response.headers.get('ETag'), total: payload.total, points: { tileQuery: tileParams.toString() } };
}

import nwUrl from './quadrants/nw.json?url&no-inline';
import neUrl from './quadrants/ne.json?url&no-inline';
import swUrl from './quadrants/sw.json?url&no-inline';
import seUrl from './quadrants/se.json?url&no-inline';

export const quadrants = [
  { id: 'nw', name: 'Noroeste', bounds: [[-180, 0], [0, 85]], url: nwUrl },
  { id: 'ne', name: 'Nordeste', bounds: [[0, 0], [180, 85]], url: neUrl },
  { id: 'sw', name: 'Sudoeste', bounds: [[-180, -85], [0, 0]], url: swUrl },
  { id: 'se', name: 'Sudeste', bounds: [[0, -85], [180, 0]], url: seUrl },
];

const cache = new Map();

function load({ id, url }) {
  if (!cache.has(id)) {
    cache.set(id, fetch(url).then(response => {
      if (!response.ok) throw new Error('Quadrant request failed');
      return response.json();
    }).catch(error => {
      cache.delete(id);
      throw error;
    }));
  }
  return cache.get(id);
}

export async function loadVisiblePoints(viewport) {
  if (!viewport) return (await Promise.all(quadrants.map(load))).flat();

  const [[west, south], [east, north]] = viewport;
  const longitudeRanges = west <= east ? [[west, east]] : [[west, 180], [-180, east]];
  const visible = quadrants.filter(({ bounds: [[left, bottom], [right, top]] }) =>
    south < top && north > bottom && longitudeRanges.some(([start, end]) => start < right && end > left));
  return (await Promise.all(visible.map(load))).flat().filter(({ coordinates: [lng, lat] }) =>
    lat >= south && lat <= north && longitudeRanges.some(([start, end]) => lng >= start && lng <= end));
}

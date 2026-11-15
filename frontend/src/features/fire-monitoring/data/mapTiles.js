export const TILE_SIZE = 256;
const MAX_LATITUDE = 85.0511287798066;
const MAX_ACTIVE_TILES = 4;
const queued = new Set();
let active = 0;
let scheduled = false;

function scheduleTiles() {
  if (scheduled) return;
  scheduled = true;
  queueMicrotask(() => {
    scheduled = false;
    for (const job of queued) {
      if (active >= MAX_ACTIVE_TILES) break;
      queued.delete(job);
      active++;
      job().finally(() => {
        active--;
        scheduleTiles();
      });
    }
  });
}

export function queueTile(url, show, fail, changePending) {
  const controller = new AbortController();
  let objectUrl;
  let pending = true;
  changePending?.(1);
  function settle() {
    if (!pending) return;
    pending = false;
    changePending?.(-1);
  }
  const job = async () => {
    try {
      for (let attempt = 0; attempt < 2 && !controller.signal.aborted; attempt++) {
        try {
          const response = await fetch(url, { signal: controller.signal });
          if (!response.ok) {
            if (response.status < 500) break;
            continue;
          }
          const blob = await response.blob();
          if (controller.signal.aborted) return;
          objectUrl = URL.createObjectURL(blob);
          show(objectUrl);
          return;
        } catch {
          if (controller.signal.aborted) return;
        }
      }
      if (!controller.signal.aborted) fail?.();
    } finally {
      settle();
    }
  };
  queued.add(job);
  scheduleTiles();
  return () => {
    queued.delete(job);
    controller.abort();
    if (objectUrl) URL.revokeObjectURL(objectUrl);
    settle();
  };
}

export function tileUrl(mode, zoom, column, row, query) {
  const size = 2 ** zoom;
  if (row < 0 || row >= size) return '';
  const wrappedColumn = (column % size + size) % size;
  return '/api/map/tiles/' + [mode, zoom, wrappedColumn, row].join('/') + '.png?' + query;
}

const longitude = (column, size) => column / size * 360 - 180;
const latitude = (row, size) => Math.atan(Math.sinh(Math.PI * (1 - 2 * row / size))) * 180 / Math.PI;

function rowAt(lat, size) {
  const radians = Math.max(-MAX_LATITUDE, Math.min(MAX_LATITUDE, lat)) * Math.PI / 180;
  return Math.min(size - 1, Math.max(0, Math.floor((1 - Math.asinh(Math.tan(radians)) / Math.PI) * size / 2)));
}

export function positionedTiles(bounds, project, mode, query) {
  const [[west, south], [east, north]] = bounds;
  const zoom = Math.max(0, Math.min(22, Math.round(Math.log2(project.scale() * 2 * Math.PI / TILE_SIZE))));
  const size = 2 ** zoom;
  const left = Math.max(0, Math.floor((west + 180) / 360 * size));
  const right = Math.min(size - 1, Math.ceil((east + 180) / 360 * size) - 1);
  const top = rowAt(north, size);
  const bottom = rowAt(south, size);
  const middleColumn = (left + right) / 2;
  const middleRow = (top + bottom) / 2;
  const tiles = [];
  for (let row = top; row <= bottom; row++) {
    for (let column = left; column <= right; column++) {
      const [x, y] = project([longitude(column, size), latitude(row, size)]);
      const [endX, endY] = project([longitude(column + 1, size), latitude(row + 1, size)]);
      const distance = Math.hypot(column - middleColumn, row - middleRow);
      tiles.push({ x, y, width: endX - x, height: endY - y, url: tileUrl(mode, zoom, column, row, query), distance });
    }
  }
  return tiles.sort((first, second) => first.distance - second.distance);
}

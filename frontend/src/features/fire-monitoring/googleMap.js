import { queueTile, TILE_SIZE, tileUrl } from './data/mapTiles.js';

let loading;

function loadGoogle(key) {
  if (window.google?.maps?.importLibrary) return Promise.resolve(window.google.maps);
  loading ??= new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const callback = 'previaGoogleMapsReady';
    const params = new URLSearchParams({ key, callback, loading: 'async' });
    const timeout = setTimeout(fail, 12000);
    function fail() {
      clearTimeout(timeout);
      delete window[callback];
      script.remove();
      reject(new Error('Google Maps unavailable'));
    }
    window[callback] = () => {
      clearTimeout(timeout);
      delete window[callback];
      resolve(window.google.maps);
    };
    script.onerror = fail;
    script.src = 'https://maps.googleapis.com/maps/api/js?' + params;
    document.head.append(script);
  }).catch(error => {
    loading = undefined;
    throw error;
  });
  return loading;
}

export async function createGoogleMap(element, key, onViewport, onError, onTileError, onTilePending) {
  const previousAuthFailure = window.gm_authFailure;
  const authFailure = () => { previousAuthFailure?.(); onError(); };
  window.gm_authFailure = authFailure;
  const restoreAuthFailure = () => {
    if (window.gm_authFailure === authFailure) window.gm_authFailure = previousAuthFailure;
  };
  try {
    const google = await loadGoogle(key);
    const [{ Map: GoogleMap, Polyline }, { Size }, { AdvancedMarkerElement }] = await Promise.all([
      google.importLibrary('maps'), google.importLibrary('core'), google.importLibrary('marker'),
    ]);
    const map = new GoogleMap(element, {
      mapId: import.meta.env.VITE_GOOGLE_MAP_ID || 'DEMO_MAP_ID',
      center: { lat: -15, lng: -57 }, zoom: 3, minZoom: 2, maxZoom: 22, streetViewControl: false,
      mapTypeControl: false, fullscreenControl: false, rotateControl: false, gestureHandling: 'greedy',
    });
    let tileKey;
    let clearTiles;
    let territoryLines = [];
    let marker;
    let pickListener;
    function showLocation(position, title) {
      if (marker) marker.map = null;
      marker = undefined;
      if (!position) return;
      const [lng, lat] = position;
      const icon = document.createElement('img');
      icon.src = '/previa-icon.png';
      icon.alt = '';
      icon.style.cssText = 'width:34px;height:34px;padding:5px;box-sizing:border-box;background:#101b19;border:2px solid #ffee78;border-radius:50%;';
      marker = new AdvancedMarkerElement({ map, position: { lat, lng }, title, anchorTop: '-50%' });
      marker.append(icon);
    }
    function setLocationPicker(pick) {
      pickListener?.remove();
      pickListener = undefined;
      map.setOptions({ draggableCursor: pick ? 'crosshair' : null });
      if (pick) {
        pickListener = map.addListener('click', event => {
          if (event.latLng) pick([event.latLng.lng(), event.latLng.lat()]);
        });
      }
    }
    function drawTerritory(outline) {
      for (const line of territoryLines) line.setMap(null);
      territoryLines = (outline?.coordinates ?? []).map(ring => new Polyline({
        map,
        path: ring.map(([lng, lat]) => ({ lng, lat })),
        clickable: false,
        strokeColor: '#101b19',
        strokeWeight: 4,
        strokeOpacity: 0.85,
        icons: [{
          icon: { path: 'M 0,-1 0,1', strokeColor: '#ffee78', strokeOpacity: 1, strokeWeight: 2.5, scale: 3 },
          offset: '0',
          repeat: '10px',
        }],
      }));
    }
    function updateTiles(query, displayMode) {
      const signature = query ? displayMode + '?' + query : undefined;
      if (signature === tileKey) return;
      if (tileKey) {
        map.overlayMapTypes.removeAt(0);
        clearTiles();
      }
      tileKey = signature;
      if (!query) return;
      const releases = new Map();
      clearTiles = () => {
        for (const release of releases.values()) release();
        releases.clear();
      };
      map.overlayMapTypes.insertAt(0, {
        tileSize: new Size(TILE_SIZE, TILE_SIZE),
        maxZoom: 22,
        getTile({ x, y }, zoom, ownerDocument) {
          const tile = ownerDocument.createElement('img');
          tile.width = TILE_SIZE;
          tile.height = TILE_SIZE;
          tile.alt = '';
          tile.draggable = false;
          const url = tileUrl(displayMode, zoom, x, y, query);
          if (url) releases.set(tile, queueTile(url, source => { tile.src = source; }, onTileError, onTilePending));
          return tile;
        },
        releaseTile(tile) {
          releases.get(tile)?.();
          releases.delete(tile);
        },
      });
    }
    function viewport() {
      const bounds = map.getBounds()?.toJSON();
      if (bounds) return [[bounds.west, bounds.south], [bounds.east, bounds.north]];
    }
    const idle = map.addListener('idle', () => {
      const bounds = viewport();
      if (bounds) onViewport(bounds);
    });
    return {
      show(points, mode) {
        updateTiles(points.tileQuery, mode);
      },
      viewport,
      drawTerritory,
      showLocation,
      setLocationPicker,
      fit(bounds, close = false) {
        if (!bounds) {
          map.setCenter({ lat: 0, lng: 0 });
          map.setZoom(2);
          return;
        }
        const [[west, south], [east, north]] = bounds;
        map.fitBounds({ west, south, east, north }, close ? 10 : undefined);
      },
      destroy() {
        restoreAuthFailure();
        idle.remove();
        updateTiles();
        drawTerritory();
        showLocation();
        setLocationPicker();
        element.replaceChildren();
      },
    };
  } catch (error) {
    restoreAuthFailure();
    throw error;
  }
}

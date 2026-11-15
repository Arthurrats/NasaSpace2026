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

export async function createGoogleMap(element, key, onViewport, onError) {
  const previousAuthFailure = window.gm_authFailure;
  const authFailure = () => { previousAuthFailure?.(); onError(); };
  window.gm_authFailure = authFailure;
  const restoreAuthFailure = () => {
    if (window.gm_authFailure === authFailure) window.gm_authFailure = previousAuthFailure;
  };
  try {
    const google = await loadGoogle(key);
    const [{ Map }, { AdvancedMarkerElement }] = await Promise.all([
      google.importLibrary('maps'), google.importLibrary('marker'),
    ]);
    const map = new Map(element, {
      mapId: import.meta.env.VITE_GOOGLE_MAP_ID || 'DEMO_MAP_ID',
      center: { lat: 0, lng: 0 }, zoom: 2, minZoom: 2, streetViewControl: false,
    });
    let markers = [];
    const idle = map.addListener('idle', () => {
      const bounds = map.getBounds()?.toJSON();
      if (bounds) onViewport([[bounds.west, bounds.south], [bounds.east, bounds.north]]);
    });
    function clearMarkers() {
      markers.forEach(marker => { marker.map = null; });
      markers = [];
    }
    return {
      show(points) {
        clearMarkers();
        markers = points.map(({ coordinates: [lng, lat], name, intensity }) => {
          const marker = document.createElement('span');
          marker.className = 'map-provider-marker intensity-' + intensity;
          return new AdvancedMarkerElement({ map, position: { lat, lng }, title: name, content: marker });
        });
      },
      fit(bounds) {
        if (!bounds) {
          map.setCenter({ lat: 0, lng: 0 });
          map.setZoom(2);
          return;
        }
        const [[west, south], [east, north]] = bounds;
        map.fitBounds({ west, south, east, north });
      },
      destroy() { restoreAuthFailure(); idle.remove(); clearMarkers(); element.replaceChildren(); },
    };
  } catch (error) {
    restoreAuthFailure();
    throw error;
  }
}

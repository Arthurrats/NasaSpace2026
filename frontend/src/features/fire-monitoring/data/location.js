import { geoCircle } from 'd3-geo';
import { describeTerritory } from './territories.js';

export const locationRadiusKm = 20;
const earthRadiusKm = 6371.0088;
let initialPosition;

export function getPosition(refresh = false) {
  if (refresh || !initialPosition) {
    initialPosition = new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocalização indisponível.'));
        return;
      }
      navigator.geolocation.getCurrentPosition(({ coords }) => resolve([coords.longitude, coords.latitude]), reject, {
        timeout: 8000,
        maximumAge: 60000,
      });
    });
  }
  return initialPosition;
}

export function locationTerritory(center, name) {
  const radius = locationRadiusKm / earthRadiusKm * 180 / Math.PI;
  const circle = geoCircle().center(center).radius(radius).precision(1)();
  const [ring] = circle.coordinates;
  ring[ring.length - 1] = ring[0];
  return { ...describeTerritory(circle), center, name, id: 'location-' + center.join(',') };
}

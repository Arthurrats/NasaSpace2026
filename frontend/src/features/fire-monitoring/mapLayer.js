export const confidenceColors = { low: '#b6e36b', medium: '#ff8a32', high: '#e84b32' };

const originalHeatStops = [[0, '#78c850'], [0.28, '#b6e36b'], [0.54, '#ff8a32'], [1, '#e84b32']];

// Cividis stops sampled from Matplotlib. Nuñez et al. (2018), doi:10.1371/journal.pone.0199239.
export const accessibleHeatStops = [
  [0, '#00224e'], [0.125, '#1a386f'], [0.25, '#434e6c'], [0.375, '#61656f'], [0.5, '#7d7c78'],
  [0.625, '#9a9376'], [0.75, '#bbad6d'], [0.875, '#ddc858'], [1, '#fee838'],
];

const heatStops = (palette) => palette === 'accessible' ? accessibleHeatStops : originalHeatStops;

export function heatGradient(palette) {
  const stops = heatStops(palette).map(([offset, color]) => `${color} ${offset * 100}%`);
  return `linear-gradient(90deg in srgb, ${stops.join(', ')})`;
}

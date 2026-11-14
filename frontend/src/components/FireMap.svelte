<script>
  import { geoGraticule10, geoMercator, geoNaturalEarth1, geoPath } from 'd3-geo';
  import { mesh, feature } from 'topojson-client';
  import world from 'world-atlas/countries-110m.json';
  import { hotspots, regions } from '../lib/demo.js';

  let { region = 'world', id = 'fire-map' } = $props();

  const width = 800;
  const height = 380;
  const land = feature(world, world.objects.land);
  const borders = mesh(world, world.objects.countries, (a, b) => a !== b);
  const grid = geoGraticule10();
  const radii = { high: 4.4, medium: 3.7, low: 3 };

  function makeProjection(bounds) {
    if (!bounds) {
      return geoNaturalEarth1().scale(142).translate([width / 2, height * 0.52]);
    }

    const [[west, south], [east, north]] = bounds;
    return geoMercator()
      .fitExtent([[25, 18], [width - 25, height - 18]], {
        type: 'MultiPoint',
        coordinates: [[west, south], [east, north]],
      })
      .clipExtent([[0, 0], [width, height]]);
  }

  const projection = $derived(makeProjection(regions[region].bounds));
  const path = $derived(geoPath(projection));
</script>

<svg class="fire-map" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{id}-title">
  <title id="{id}-title">Focos de incêndio ilustrativos · {regions[region].name}</title>
  <defs>
    <radialGradient id="{id}-sea">
      <stop stop-color="#172a29" />
      <stop offset="1" stop-color="#101c1c" />
    </radialGradient>
    <clipPath id="{id}-clip"><rect {width} {height} /></clipPath>
  </defs>
  <rect {width} {height} fill="url(#{id}-sea)" />
  <g clip-path="url(#{id}-clip)">
    <path d={path(grid)} class="grid" />
    <path d={path(land)} class="land" />
    <path d={path(borders)} class="borders" />
    {#each hotspots as hotspot (hotspot.name)}
      {@const [x, y] = projection(hotspot.coordinates)}
      {@const radius = radii[hotspot.intensity] * (region === 'world' ? 1 : 1.25)}
      <g class="hotspot {hotspot.intensity}" transform="translate({x} {y})">
        <title>{hotspot.name} (exemplo)</title>
        <circle r={radius * 2.4} opacity=".12" />
        <circle r={radius * 1.65} opacity=".22" />
        <circle r={radius} />
      </g>
    {/each}
  </g>
</svg>

<style>
  .fire-map { display: block; width: 100%; height: auto; overflow: hidden; }
  .grid { fill: none; stroke: #344946; stroke-width: .65; opacity: .55; }
  .land { fill: #304541; stroke: #4a5d55; stroke-width: .8; }
  .borders { fill: none; stroke: #495e55; stroke-width: .65; }
  .high { fill: var(--accent); }
  .medium { fill: #ffc478; }
  .low { fill: #f1d9a1; }
</style>

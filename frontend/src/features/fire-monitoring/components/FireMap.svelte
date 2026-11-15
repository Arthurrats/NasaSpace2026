<script>
  import { geoGraticule10, geoMercator, geoNaturalEarth1, geoPath } from 'd3-geo';
  import { mesh, feature } from 'topojson-client';
  import world from 'world-atlas/countries-110m.json';
  import { hotspots, regions } from '../data/demo.js';

  let { region = 'southAmerica', id = 'fire-map', bounds, points, title } = $props();

  const width = 800;
  const height = 380;
  const land = feature(world, world.objects.land);
  const borders = mesh(world, world.objects.countries, (a, b) => a !== b);
  const grid = geoGraticule10();
  const radii = { high: 5.4, medium: 4.6, low: 3.8 };

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

  const projection = $derived(makeProjection(bounds ?? regions[region]?.bounds));
  const path = $derived(geoPath(projection));
  const visibleHotspots = $derived(points ?? (region === 'world' || region === 'southAmerica'
    ? hotspots
    : hotspots.filter(({ country }) => country === region)));
</script>

<svg class="fire-map" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{id}-title">
  <title id="{id}-title">{title ?? ('Focos de calor ilustrativos · ' + (regions[region]?.name ?? 'Visão global da América do Sul'))}</title>
  <defs>
    <radialGradient id="{id}-sea">
      <stop stop-color="var(--map-glow)" />
      <stop offset="1" stop-color="var(--map-water)" />
    </radialGradient>
    <clipPath id="{id}-clip"><rect {width} {height} /></clipPath>
  </defs>
  <rect {width} {height} fill="url(#{id}-sea)" />
  <g clip-path="url(#{id}-clip)">
    <path d={path(grid)} class="grid" />
    <path d={path(land)} class="land" />
    <path d={path(borders)} class="borders" />
    {#each visibleHotspots as hotspot (hotspot.name)}
      {@const [x, y] = projection(hotspot.coordinates)}
      {@const radius = radii[hotspot.intensity] * (region === 'world' ? 1 : 1.25)}
      <g class="hotspot intensity-{hotspot.intensity}" transform="translate({x} {y})">
        <title>{hotspot.name} (exemplo)</title>
        <circle r={radius * 2.4} opacity=".15" />
        <circle r={radius * 1.65} opacity=".34" />
        <circle class="hotspot-core" r={radius} />
      </g>
    {/each}
  </g>
</svg>

<style>
  .fire-map { display: block; width: 100%; height: auto; overflow: hidden; }
  .grid { fill: none; stroke: var(--map-stroke); stroke-width: .65; opacity: .48; }
  .land { fill: var(--map-land); stroke: var(--map-stroke); stroke-width: .85; }
  .borders { fill: none; stroke: var(--map-stroke); stroke-width: .75; }
  .hotspot { fill: var(--intensity-color); }
  .hotspot-core { stroke: var(--map-marker-outline); stroke-width: 1.1; }
</style>

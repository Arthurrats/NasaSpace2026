<script>
  import { geoGraticule10, geoMercator, geoNaturalEarth1, geoPath } from 'd3-geo';
  import { mesh, feature } from 'topojson-client';
  import world from 'world-atlas/countries-110m.json';
  import { hotspots, regions } from '../data/demo.js';
  import { positionedTiles, queueTile } from '../data/mapTiles.js';

  let {
    region = 'southAmerica', id = 'fire-map', bounds, points, title, mode = 'cluster', fill = false,
    onAreaSelect, selectionBounds, selectableBounds, onTileError, onTilePending,
  } = $props();
  let measuredWidth = $state(0);
  let measuredHeight = $state(0);
  let dragOrigin = $state();
  let dragBounds = $state();
  let pointerId;
  let pointerOrigin;

  const width = $derived(fill ? Math.max(200, measuredWidth) : 800);
  const height = $derived(fill ? Math.max(140, measuredHeight) : 380);
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

  const viewBounds = $derived(bounds ?? (onAreaSelect ? selectableBounds : undefined) ?? regions[region]?.bounds
    ?? (onAreaSelect || selectionBounds ? regions.southAmerica.bounds : undefined));
  const limits = $derived(selectableBounds ?? viewBounds ?? regions.southAmerica.bounds);
  const projection = $derived(makeProjection(viewBounds));
  const path = $derived(geoPath(projection));
  const tiles = $derived(points?.tileQuery && bounds ? positionedTiles(bounds, projection, mode, points.tileQuery) : []);
  const visibleArea = $derived(projectArea((onAreaSelect && dragBounds) || selectionBounds));
  const visibleHotspots = $derived(region === 'world' || region === 'southAmerica'
    ? hotspots
    : hotspots.filter(({ country }) => country === region));

  function eventCoordinates(event) {
    const matrix = event.currentTarget.ownerSVGElement.getScreenCTM();
    if (!matrix) return;
    const { x, y } = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
    const [longitude, latitude] = projection.invert([x, y]);
    if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) return;
    const [[west, south], [east, north]] = limits;
    return [Math.max(west, Math.min(east, longitude)), Math.max(south, Math.min(north, latitude))];
  }

  function areaTo(event) {
    const end = eventCoordinates(event);
    if (!end) return;
    const [startX, startY] = dragOrigin;
    const [endX, endY] = end;
    return [[Math.min(startX, endX), Math.min(startY, endY)], [Math.max(startX, endX), Math.max(startY, endY)]];
  }

  function projectArea(area) {
    if (!area) return;
    const [[west, south], [east, north]] = area;
    if (!(west < east && south < north)) return;
    const [left, top] = projection([west, north]);
    const [right, bottom] = projection([east, south]);
    return { x: left, y: top, width: right - left, height: bottom - top };
  }

  function startSelection(event) {
    if (!event.isPrimary || event.button !== 0 || pointerId !== undefined) return;
    const start = eventCoordinates(event);
    if (!start) return;
    pointerId = event.pointerId;
    pointerOrigin = [event.clientX, event.clientY];
    dragOrigin = start;
    dragBounds = [start, start];
    event.currentTarget.setPointerCapture(pointerId);
  }

  function moveSelection(event) {
    if (event.pointerId === pointerId) dragBounds = areaTo(event);
  }

  function clearSelection(event) {
    if (event.pointerId === pointerId) resetSelection();
  }

  function resetSelection() {
    pointerId = undefined;
    pointerOrigin = undefined;
    dragOrigin = undefined;
    dragBounds = undefined;
  }

  function finishSelection(event) {
    if (event.pointerId !== pointerId) return;
    const area = areaTo(event);
    const [startX, startY] = pointerOrigin;
    const largeEnough = Math.abs(event.clientX - startX) >= 4 && Math.abs(event.clientY - startY) >= 4;
    resetSelection();
    if (!area || !largeEnough) return;
    const [[west, south], [east, north]] = area;
    if (west < east && south < north) onAreaSelect(area);
  }

  function loadTile(node, url) {
    const dispose = queueTile(url, source => node.setAttribute('href', source), () => onTileError?.(), onTilePending);
    return { destroy: dispose };
  }

  $effect(() => {
    if (!onAreaSelect) resetSelection();
  });
</script>

<div class:fill bind:clientWidth={measuredWidth} bind:clientHeight={measuredHeight}>
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
    {#if points?.tileQuery}
      {#each tiles as tile (tile.url)}
        <image use:loadTile={tile.url} x={tile.x} y={tile.y} width={tile.width} height={tile.height} preserveAspectRatio="none" />
      {/each}
    {:else if !points}
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
    {/if}
    {#if visibleArea}
      <rect {...visibleArea} class="area-outline" vector-effect="non-scaling-stroke" aria-hidden="true" />
      <rect {...visibleArea} class="area-highlight" vector-effect="non-scaling-stroke" aria-hidden="true" />
    {/if}
  </g>
  {#if onAreaSelect}
    <rect class="draw-surface" {width} {height} role="presentation"
      onpointerdown={startSelection} onpointermove={moveSelection} onpointerup={finishSelection}
      onpointercancel={clearSelection} onlostpointercapture={clearSelection} />
  {/if}
</svg>
</div>

<style>
  .fill, .fill .fire-map { width: 100%; height: 100%; }
  .fire-map { display: block; width: 100%; height: auto; overflow: hidden; }
  .grid { fill: none; stroke: var(--map-stroke); stroke-width: .65; opacity: .48; }
  .land { fill: var(--map-land); stroke: var(--map-stroke); stroke-width: .85; }
  .borders { fill: none; stroke: var(--map-stroke); stroke-width: .75; }
  .hotspot { fill: var(--intensity-color); }
  .hotspot-core { stroke: var(--map-marker-outline); stroke-width: 1.1; }
  .area-outline, .area-highlight { pointer-events: none; }
  .area-outline { fill: none; stroke: #101b19; stroke-width: 4.5; }
  .area-highlight { fill: #ffee78; fill-opacity: .12; stroke: #ffee78; stroke-width: 2; stroke-dasharray: 6 3; }
  .draw-surface { fill: transparent; cursor: crosshair; touch-action: none; }
</style>

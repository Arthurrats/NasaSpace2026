<script>
  import { onMount } from 'svelte';
  import { Globe, SlidersHorizontal } from '@lucide/svelte';
  import FireMap from '../features/fire-monitoring/components/FireMap.svelte';
  import MapLegend from '../features/fire-monitoring/components/MapLegend.svelte';
  import PeriodFields from '../features/fire-monitoring/components/PeriodFields.svelte';
  import { createGoogleMap } from '../features/fire-monitoring/googleMap.js';
  import { loadTileLayer, quadrants } from '../features/fire-monitoring/data/quadrants.js';
  import { loadTimeline } from '../features/fire-monitoring/data/timeline.js';
  import { countries, regions } from '../features/fire-monitoring/data/demo.js';
  import { mapCopy as copy } from '../content/platform.js';

  let { timelineOnly = false } = $props();
  const key = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  let host = $state();
  let provider;
  let active = true;
  let pending;
  let timer;
  let lastQuery;
  let lastLoadedAt = 0;
  let displayedVersion;
  let googleActive = $state(false);
  let providerError = $state(false);
  let selected = $state('world');
  let sensor = $state('all');
  let mode = $state('heat');
  let heatMetric = $state('detections');
  const heatLabel = $derived(copy.heatMetrics.find(item => item.id === heatMetric)?.legend);
  const firstDate = '2025-01-01';
  const lastDate = '2025-12-31';
  let draftStart = $state(firstDate);
  let draftEnd = $state(lastDate);
  let startDate = $state(firstDate);
  let endDate = $state(lastDate);
  let step = $state('month');
  let frameIndex = $state(null);
  let playing = $state(false);
  let frames = $state([]);
  let timelineLoading = $state(false);
  let timelineError = $state(false);
  let timelineAttempt = $state(0);
  const currentFrame = $derived(frameIndex === null ? null : frames[frameIndex]);
  let viewport;
  let points = $state([]);
  let total = $state(0);
  let loading = $state(true);
  let dataError = $state(false);
  let tileError = $state(false);
  let pendingTiles = $state(0);
  const selectedBounds = $derived(countries[selected]?.bounds ?? quadrants.find(({ id }) => id === selected)?.bounds ?? regions.southAmerica.bounds);

  $effect(() => {
    if (!playing || loading || pendingTiles || !currentFrame || dataError || tileError) return;
    const next = frameIndex + 1;
    const advance = setTimeout(() => {
      if (next >= frames.length) playing = false;
      else seek(next);
    }, 650);
    return () => clearTimeout(advance);
  });

  $effect(() => {
    if (!timelineOnly) return;
    void timelineAttempt;
    const controller = new AbortController();
    frames = [];
    timelineLoading = true;
    timelineError = false;
    loadTimeline(startDate, endDate, step, controller.signal)
      .then(result => {
        if (controller.signal.aborted) return;
        frames = result;
        if (frameIndex !== null) seek(0);
      })
      .catch(() => { if (!controller.signal.aborted) timelineError = true; })
      .finally(() => { if (!controller.signal.aborted) timelineLoading = false; });
    return () => controller.abort();
  });

  function trackTile(delta) {
    pendingTiles += delta;
  }

  function reportTileError() {
    playing = false;
    tileError = true;
  }

  function layerFor(displayMode) {
    if (displayMode === 'heat') return 'heat';
    return displayMode === 'cluster' ? 'markers' : 'points';
  }

  function update(bounds, delay = 0, background = false) {
    viewport = bounds;
    const layer = layerFor(mode);
    const filters = {
      sensor, country: countries[selected] ? selected : 'all', layer,
      clip: selected === 'world' ? selectedBounds : undefined,
      metric: layer === 'heat' ? heatMetric : undefined,
      startDate: currentFrame?.startDate ?? startDate,
      endDate: currentFrame?.endDate ?? endDate,
    };
    const query = JSON.stringify([bounds, filters]);
    if (query === pending?.query) return;
    cancelUpdate();
    if (!background && query === lastQuery && performance.now() - lastLoadedAt < 500) {
      loading = false;
      return;
    }
    const controller = new AbortController();
    pending = { query, controller };
    if (!background) {
      loading = true;
      dataError = false;
    }
    const run = () => fetchPoints(bounds, filters, query, controller, background);
    if (delay) timer = setTimeout(run, delay);
    else run();
  }

  function cancelUpdate() {
    clearTimeout(timer);
    pending?.controller.abort();
    pending = undefined;
  }

  async function fetchPoints(bounds, filters, query, controller, background) {
    try {
      const result = await loadTileLayer(bounds, filters, controller.signal);
      if (controller.signal.aborted) return;
      if (!result.version || result.version !== displayedVersion) {
        if (points.tileQuery !== result.points.tileQuery) tileError = false;
        points = result.points;
        total = result.total;
        provider?.show(result.points, mode);
        displayedVersion = result.version;
      }
      lastQuery = query;
      lastLoadedAt = performance.now();
    } catch {
      if (controller.signal.aborted) return;
      if (background) return;
      playing = false;
      lastQuery = undefined;
      points = [];
      total = 0;
      displayedVersion = undefined;
      provider?.show([], mode);
      dataError = true;
    } finally {
      if (pending?.controller === controller) {
        pending = undefined;
        loading = false;
      }
    }
  }

  function fallback() {
    if (!active) return;
    provider?.destroy();
    provider = undefined;
    googleActive = false;
    providerError = true;
    update(selectedBounds);
  }

  function changeView(event) {
    selected = event.currentTarget.value;
    resetPoints();
    provider?.fit(selectedBounds);
    update(selectedBounds, provider ? 200 : 0);
  }

  function changeSensor(event) {
    sensor = event.currentTarget.value;
    resetPoints();
    update(provider?.viewport() ?? viewport);
  }

  function changeMode(event) {
    const previousLayer = layerFor(mode);
    mode = event.currentTarget.value;
    if (previousLayer !== layerFor(mode)) {
      resetPoints();
      update(provider?.viewport() ?? viewport);
    } else {
      provider?.show(points, mode);
    }
  }

  function changeHeatMetric(event) {
    heatMetric = event.currentTarget.value;
    resetPoints();
    update(provider?.viewport() ?? viewport);
  }

  function applyPeriod(event) {
    event.preventDefault();
    if (draftStart === startDate && draftEnd === endDate) return;
    startDate = draftStart;
    endDate = draftEnd;
    playing = false;
    if (frameIndex !== null) frames = [];
    resetPoints();
    update(provider?.viewport() ?? viewport);
  }

  function resetPoints() {
    cancelUpdate();
    lastQuery = undefined;
    displayedVersion = undefined;
    points = [];
    total = 0;
    tileError = false;
    provider?.show([], mode);
  }

  function retryMap() {
    resetPoints();
    update(viewport);
  }

  function seek(index) {
    frameIndex = index;
    tileError = false;
    update(provider?.viewport() ?? viewport);
  }

  function changeStep(event) {
    step = event.currentTarget.value;
    playing = false;
  }

  function togglePlayback() {
    if (playing) {
      playing = false;
      return;
    }
    if (frameIndex === null || frameIndex === frames.length - 1) seek(0);
    playing = true;
  }

  function exitTimeline() {
    playing = false;
    seek(null);
  }

  onMount(() => {
    update(selectedBounds);
    if (key) {
      createGoogleMap(host, key, bounds => {
        if (active && !providerError) update(bounds, 150);
      }, fallback, reportTileError, trackTile).then(map => {
        if (!active || providerError) { map.destroy(); return; }
        provider = map;
        googleActive = true;
        provider.show(points, mode);
        if (selectedBounds) provider.fit(selectedBounds);
      }).catch(fallback);
    }
    const refresh = setInterval(() => {
      if (!pending && !playing && !dataError && document.visibilityState === 'visible') update(viewport, 0, true);
    }, 30000);
    return () => {
      active = false;
      clearInterval(refresh);
      cancelUpdate();
      provider?.destroy();
    };
  });
</script>

<section class="workspace" aria-labelledby="workspace-title">
  <header>
    <h1 id="workspace-title">{timelineOnly ? 'Timelapse' : 'Mapa'}</h1>
  </header>
  <div class="card map-scale">
    <MapLegend {mode} {heatLabel} />
  </div>
  <div class="card map">
    <div class="map-area">
      {#if key}<div class="google-host" class:ready={googleActive} aria-label={copy.google} bind:this={host}></div>{/if}
      {#if !googleActive}
        <FireMap region="world" id="workspace-map" bounds={selectedBounds} {points} {mode} title={copy.title} onTileError={reportTileError} onTilePending={trackTile} fill />
      {/if}
    </div>
    <details class="filter-layer">
      <summary><SlidersHorizontal size={17} aria-hidden="true" /> Filtros do mapa</summary>
      <div class="filter-body">
    <div class="toolbar">
      <label>
        <Globe size={18} aria-hidden="true" /> {copy.view}
        <select class="data-control" value={selected} onchange={changeView}>
          <option value="world">América do Sul</option>
          {#each quadrants as quadrant (quadrant.id)}
            <option value={quadrant.id}>{quadrant.name}</option>
          {/each}
          <optgroup label={copy.countries}>
            {#each Object.entries(countries) as [id, country] (id)}
              <option value={id}>{country.name}</option>
            {/each}
          </optgroup>
        </select>
      </label>
      <label>Sensor
        <select class="data-control" value={sensor} onchange={changeSensor}>
          <option value="all">MODIS + VIIRS</option>
          <option value="modis">MODIS</option>
          <option value="viirs">VIIRS</option>
        </select>
      </label>
      <label>{copy.displayMode}
        <select class="data-control" value={mode} onchange={changeMode}>
          {#each copy.modes as option (option.id)}
            <option value={option.id}>{option.label}</option>
          {/each}
        </select>
      </label>
      {#if mode === 'heat'}
        <label>{copy.heatMetric}
          <select class="data-control" value={heatMetric} onchange={changeHeatMetric}>
            {#each copy.heatMetrics as item (item.id)}<option value={item.id}>{item.label}</option>{/each}
          </select>
        </label>
      {/if}
    </div>
    <form class="period" aria-label={copy.period} onsubmit={applyPeriod}>
      <PeriodFields bind:start={draftStart} bind:end={draftEnd} first={firstDate} last={lastDate} />
      <button type="submit" class="button button-outline">{copy.applyPeriod}</button>
    </form>
      </div>
    </details>
    <div class="status">
      <p role="status">{loading ? copy.loading : dataError ? copy.error : copy.heatTotal(total)}</p>
      {#if !loading && !dataError && pendingTiles}<span>{copy.tilesLoading}</span>{/if}
      {#if tileError && !dataError}<span>{copy.tileError}</span>{/if}
      {#if dataError || tileError}<button type="button" class="button button-outline" onclick={retryMap}>{copy.retry}</button>{/if}
      {#if providerError}<span>{copy.fallback}</span>{/if}
    </div>
  </div>
  {#if timelineOnly}
    <div class="timeline" role="group" aria-label={copy.timeline}>
      <div class="timeline-controls">
        <label>{copy.timelineStep}
          <select class="data-control" value={step} onchange={changeStep}>
            {#each copy.timelineSteps as item (item.id)}<option value={item.id}>{item.label}</option>{/each}
          </select>
        </label>
        <button type="button" class="button button-primary" disabled={timelineLoading || !frames.length} onclick={togglePlayback}>{playing ? copy.pauseTimeline : copy.playTimeline}</button>
        {#if currentFrame}
          <button type="button" class="button button-outline" onclick={exitTimeline}>{copy.exitTimeline}</button>
        {/if}
      </div>
      {#if timelineError}<button type="button" class="button button-outline" onclick={() => timelineAttempt++}>{copy.timelineRetry}</button>{/if}
      <label class="timeline-track">
        <span>{currentFrame?.label ?? (timelineLoading ? copy.timelineLoading : copy.timelineReady)}</span>
        <input type="range" min="0" max={Math.max(0, frames.length - 1)} value={frameIndex ?? 0}
          aria-label={copy.timelinePosition} aria-valuetext={currentFrame?.label ?? frames[0]?.label}
          disabled={frames.length < 2}
          oninput={(event) => { playing = false; seek(Number(event.currentTarget.value)); }} />
      </label>
    </div>
  {/if}
</section>

<style>
  .workspace { height: 100%; min-height: 0; display: flex; flex-direction: column; gap: 10px; padding: 10px clamp(8px, 2vw, 24px); }
  h1 { font: 700 clamp(2.1rem, 4vw, 3.25rem)/1 var(--heading); }
  .map-scale { flex: none; border-color: var(--accent-border); }
  .map-scale :global(.map-legend) { padding: 7px 12px; border-top: 0; }
  .map { position: relative; flex: 1; min-height: 0; overflow: hidden; border-color: var(--accent-border); isolation: isolate; }
  .filter-layer { position: absolute; z-index: 2; top: 8px; left: 8px; max-width: min(430px, calc(100% - 16px)); }
  .filter-layer summary { display: flex; align-items: center; gap: 7px; width: fit-content; padding: 8px 10px; list-style: none; cursor: pointer; border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--background); font-size: .76rem; font-weight: 650; }
  .filter-body { margin-top: 5px; max-height: min(52svh, 355px); overflow: auto; overscroll-behavior: contain; border: 1px solid var(--border); border-radius: var(--control-radius); background: var(--background); }
  .toolbar, .status { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 8px 10px; }
  .toolbar { background: var(--accent-surface); }
  label { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
  label :global(svg) { color: var(--accent); }
  .period { display: flex; flex-wrap: wrap; align-items: end; gap: 8px 14px; padding: 9px 16px; border-block: 1px solid var(--border); }
  .timeline { flex: none; padding: 8px 10px; border-radius: var(--control-radius); background: var(--accent-surface); }
  .timeline-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 9px 14px; }
  .timeline-track { display: grid; margin-top: 8px; color: var(--muted); font-size: .8rem; }
  .timeline-track input { width: 100%; min-height: 20px; padding: 0; accent-color: var(--accent); }
  .map-area { position: absolute; inset: 0; }
  .google-host { position: absolute; inset: 0; visibility: hidden; }
  .google-host.ready { visibility: visible; }
  .status { position: absolute; bottom: 20px; left: 8px; max-width: calc(100% - 65px); color: var(--text); background: var(--background); border: 1px solid var(--border); border-radius: var(--control-radius); font-size: .72rem; }
</style>

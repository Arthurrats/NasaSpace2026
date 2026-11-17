<script>
  import { onMount, untrack } from 'svelte';
  import { ArrowDown, ChevronDown, Crosshair, MapPin, SlidersHorizontal, X } from '@lucide/svelte';
  import Skeleton from '../components/Skeleton.svelte';
  import FireMap from '../features/fire-monitoring/components/FireMap.svelte';
  import MapLegend from '../features/fire-monitoring/components/MapLegend.svelte';
  import PeriodFields from '../features/fire-monitoring/components/PeriodFields.svelte';
  import TerritorySearch from '../features/fire-monitoring/components/TerritorySearch.svelte';
  import { createGoogleMap } from '../features/fire-monitoring/googleMap.js';
  import { loadTileLayer, quadrants } from '../features/fire-monitoring/data/quadrants.js';
  import { getPosition, locationRadiusKm, locationTerritory } from '../features/fire-monitoring/data/location.js';
  import { timelineQuery } from '../features/fire-monitoring/data/timeline.js';
  import { countries, regions } from '../features/fire-monitoring/data/demo.js';
  import { mapCopy as copy } from '../content/platform.js';

  let { timelineOnly = false, embedded = false, onViewIndicators } = $props();
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
  let territory = $state.raw(null);
  let locating = $state(false);
  let pickingLocation = $state(false);
  let locationError = $state(false);
  let positionAttempt = 0;
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
  const timelineRequest = $derived(timelineOnly ? timelineQuery(startDate, endDate, step) : null);
  const frames = $derived($timelineRequest?.data ?? []);
  const timelineLoading = $derived($timelineRequest?.status === 'loading');
  const timelineError = $derived($timelineRequest?.status === 'error');
  const currentFrame = $derived(frameIndex === null ? null : frames[frameIndex]);
  let viewport;
  let points = $state([]);
  let total = $state(0);
  let loading = $state(true);
  let dataError = $state(false);
  let tileError = $state(false);
  let pendingTiles = $state(0);
  const mapLoading = $derived(loading || pendingTiles > 0);
  const selectedBounds = $derived(territory?.bounds ?? countries[selected]?.bounds ??
    quadrants.find(({ id }) => id === selected)?.bounds ?? regions.southAmerica.bounds);

  $effect(() => {
    if (!playing || mapLoading || !currentFrame || dataError || tileError) return;
    const next = frameIndex + 1;
    const advance = setTimeout(() => {
      if (next >= frames.length) playing = false;
      else seek(next);
    }, 650);
    return () => clearTimeout(advance);
  });

  $effect(() => {
    if (!frames.length) return;
    untrack(() => {
      if (frameIndex !== null) seek(0);
    });
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
    bounds = territory?.bounds ?? bounds;
    const layer = layerFor(mode);
    const filters = {
      sensor, country: !territory && countries[selected] ? selected : 'all', layer,
      clip: !territory && selected === 'world' ? selectedBounds : undefined,
      territory,
      metric: layer === 'heat' ? heatMetric : undefined,
      startDate: currentFrame?.startDate ?? startDate,
      endDate: currentFrame?.endDate ?? endDate,
    };
    const query = JSON.stringify([bounds, { ...filters, territory: territory?.id }]);
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
    selectTerritory(null);
  }

  function selectTerritory(place) {
    positionAttempt++;
    locating = false;
    locationError = false;
    setPickingLocation(false);
    territory = place;
    resetPoints();
    provider?.drawTerritory(place?.outline);
    provider?.showLocation(place?.center, place?.name);
    provider?.fit(selectedBounds, Boolean(territory));
    update(selectedBounds, provider ? 200 : 0);
  }

  async function locate(refresh = true) {
    const attempt = ++positionAttempt;
    locating = true;
    locationError = false;
    setPickingLocation(false);
    try {
      const center = await getPosition(refresh);
      if (active && attempt === positionAttempt) selectTerritory(locationTerritory(center, 'Minha localização'));
    } catch {
      if (active && attempt === positionAttempt) locationError = refresh;
    } finally {
      if (active && attempt === positionAttempt) locating = false;
    }
  }

  function setPickingLocation(enabled) {
    pickingLocation = enabled;
    provider?.setLocationPicker(enabled ? pickLocation : undefined);
  }

  function toggleLocationPicker() {
    positionAttempt++;
    locating = false;
    locationError = false;
    setPickingLocation(!pickingLocation);
  }

  function pickLocation(center) {
    try {
      selectTerritory(locationTerritory(center, 'Local escolhido'));
    } catch {
      locationError = true;
    }
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
    if (frameIndex !== null) frameIndex = 0;
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
    if (!timelineOnly) locate(false);
    if (key) {
      createGoogleMap(host, key, bounds => {
        if (active && !providerError && !territory) update(bounds, 150);
      }, fallback, reportTileError, trackTile).then(map => {
        if (!active || providerError) { map.destroy(); return; }
        provider = map;
        googleActive = true;
        provider.show(points, mode);
        provider.drawTerritory(territory?.outline);
        provider.showLocation(territory?.center, territory?.name);
        if (pickingLocation) provider.setLocationPicker(pickLocation);
        if (selectedBounds) provider.fit(selectedBounds, Boolean(territory));
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

<section class="workspace" class:embedded aria-labelledby="workspace-title">
  <header class="workspace-heading">
    {#if embedded}
      <h2 id="workspace-title">Mapa de focos</h2>
    {:else}
      <h1 id="workspace-title">{timelineOnly ? 'Timelapse' : 'Mapa de focos'}</h1>
    {/if}
    {#if onViewIndicators}
      <button type="button" class="button button-outline" onclick={onViewIndicators}>Ver indicadores <ArrowDown size={17} aria-hidden="true" /></button>
    {/if}
  </header>
  {#if !timelineOnly}
    <div class="map-controls">
      <div class="map-search">
        <TerritorySearch territory={territory?.center ? null : territory} onSelect={selectTerritory} onClear={() => selectTerritory(null)} />
      </div>
      <div class="location-controls">
        <button type="button" class="button button-outline" onclick={() => locate()} disabled={locating}>
          <Crosshair size={16} aria-hidden="true" /> {locating ? 'Localizando…' : 'Minha localização'}
        </button>
        <button type="button" class="button button-outline" onclick={toggleLocationPicker} aria-pressed={pickingLocation}>
          <MapPin size={16} aria-hidden="true" /> {territory?.center ? 'Mudar localização' : 'Escolher no mapa'}
        </button>
      </div>
    </div>
    {#if territory?.center}
      <div class="location-radius">
        <p><strong>{territory.name}</strong> · Raio de {locationRadiusKm} km</p>
        <button type="button" class="button button-outline" aria-label="Limpar localização" onclick={() => selectTerritory(null)}>
          <X size={17} aria-hidden="true" />
        </button>
      </div>
    {/if}
    {#if pickingLocation}<p class="location-message" role="status">Clique no mapa para definir o centro do raio de {locationRadiusKm} km.</p>
    {:else if locationError}<p class="location-message" role="status">Não foi possível usar essa localização. Escolha outro ponto no mapa.</p>{/if}
  {/if}
  <div class="card map-scale">
    <MapLegend {mode} {heatLabel} />
  </div>
  <div class="card map">
    <div class="map-area" aria-busy={mapLoading}>
      {#if key}<div class="google-host" class:ready={googleActive} aria-label={copy.google} bind:this={host}></div>{/if}
      {#if !googleActive}
        <FireMap region="world" id="workspace-map" bounds={selectedBounds} {points} {mode}
          title={territory ? copy.title + ' · ' + territory.name : copy.title} territoryOutline={territory?.outline}
          territoryGeometry={territory?.geometry}
          location={territory?.center} locationLabel={territory?.name} onLocationPick={pickingLocation ? pickLocation : undefined}
          onTileError={reportTileError} onTilePending={trackTile} fill />
      {/if}
    </div>
    <details class="filter-layer">
      <summary><SlidersHorizontal size={18} aria-hidden="true" /> Filtros do mapa <ChevronDown size={16} class="filter-chevron" aria-hidden="true" /></summary>
      <div class="filter-body">
        <div class="toolbar">
          <label>
            Área exibida
            <select class="data-control" value={territory ? 'territory' : selected} onchange={changeView}>
              {#if territory}<option value="territory" disabled>{territory.name}</option>{/if}
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
  </div>
  <div class="map-footer">
    <div class="status">
      <p role="status">
        {loading ? copy.loading : dataError ? copy.error :
          territory ? total.toLocaleString('pt-BR') + (territory.center ? ' detecções em até ' + locationRadiusKm + ' km' : ' detecções no território') : copy.heatTotal(total)}
      </p>
      {#if !loading && !dataError && pendingTiles}<span>{copy.tilesLoading}</span>{/if}
      {#if tileError && !dataError}<span>{copy.tileError}</span>{/if}
      {#if dataError || tileError}<button type="button" class="button button-outline" onclick={retryMap}>{copy.retry}</button>{/if}
      {#if providerError}<span>{copy.fallback}</span>{/if}
    </div>
    {#if !timelineOnly}
      <p class="map-meta">
        <span>Detecções históricas na América do Sul</span>
        <span>
          <a href="https://www.openstreetmap.org/copyright">© OpenStreetMap</a>
          {#if territory?.source === 'natural-earth'} · <a href="https://www.naturalearthdata.com/">Natural Earth</a>{/if}
        </span>
      </p>
    {/if}
  </div>
  {#if timelineOnly}
    <div class="card timeline" role="group" aria-label={copy.timeline}>
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
      {#if timelineError}<button type="button" class="button button-outline" onclick={() => timelineRequest.refresh()}>{copy.timelineRetry}</button>{/if}
      {#if timelineLoading}
        <div class="timeline-track">
          <span role="status">{copy.timelineLoading}</span>
          <Skeleton height="20px" />
        </div>
      {:else}
        <label class="timeline-track">
          <span>{currentFrame?.label ?? copy.timelineReady}</span>
          <input type="range" min="0" max={Math.max(0, frames.length - 1)} value={frameIndex ?? 0}
            aria-label={copy.timelinePosition} aria-valuetext={currentFrame?.label ?? frames[0]?.label}
            disabled={frames.length < 2}
            oninput={(event) => { playing = false; seek(Number(event.currentTarget.value)); }} />
        </label>
      {/if}
    </div>
  {/if}
</section>

<style>
  .workspace { min-height: 100%; display: flex; flex-direction: column; gap: 12px; padding: var(--workspace-inset); }
  .workspace-heading { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; }
  h1, .embedded h2 { font: 700 var(--workspace-heading)/1 var(--heading); }
  .workspace.embedded { min-height: 0; padding: var(--workspace-inset) 0 0; }
  .map-controls { display: flex; flex-wrap: wrap; align-items: start; gap: 10px; }
  .map-search { flex: 1 1 18rem; min-width: 0; }
  .map-scale { flex: none; border-color: var(--accent-border); }
  .map-scale :global(.map-legend) { padding: 10px 14px; border-top: 0; font-size: .86rem; }
  .map { position: relative; flex: 1; min-height: clamp(340px, 53svh, 580px); overflow: hidden; border-color: var(--accent-border); isolation: isolate; }
  .embedded .map { flex: none; height: clamp(350px, 56svh, 640px); }
  .map-footer { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 7px 18px; }
  .map-meta { display: flex; flex-wrap: wrap; gap: 4px 12px; color: var(--muted); font-size: .8rem; }
  .map-meta a { text-decoration: underline; text-underline-offset: 2px; }
  .location-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
  .location-radius { display: flex; align-items: center; gap: 8px; }
  .location-radius .button { width: var(--control-height); padding-inline: 0; }
  .location-radius p, .location-message { color: var(--muted); font-size: .89rem; }
  .location-message { padding-left: 10px; border-left: 3px solid var(--accent); }
  .filter-layer { position: absolute; z-index: 2; inset: 12px auto auto 12px; max-width: min(485px, calc(100% - 24px)); }
  .filter-layer summary { display: flex; align-items: center; gap: 9px; width: fit-content; min-height: var(--control-height); padding: 8px 12px; list-style: none; cursor: pointer; border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--background); font-size: .9rem; font-weight: 650; }
  .filter-layer[open] :global(.filter-chevron) { transform: rotate(180deg); }
  .filter-body { margin-top: 7px; max-height: min(48svh, 390px); overflow: auto; overscroll-behavior: contain; border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--background); }
  .toolbar { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr)); gap: 12px; padding: 14px; }
  .toolbar label { display: grid; min-width: 0; gap: 6px; color: var(--muted); font-size: .86rem; }
  .period { display: flex; flex-wrap: wrap; align-items: end; gap: 10px 14px; padding: 14px; border-top: 1px solid var(--border); }
  .timeline { flex: none; padding: var(--panel-padding); background: var(--accent-surface); }
  .timeline-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 9px 14px; }
  .timeline-track { display: grid; margin-top: 12px; color: var(--muted); font-size: .92rem; }
  .timeline-track input { width: 100%; min-height: 36px; padding: 0; accent-color: var(--accent); }
  .map-area { position: absolute; inset: 0; }
  .google-host { position: absolute; inset: 0; visibility: hidden; }
  .google-host.ready { visibility: visible; }
  .status { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; color: var(--text); font-size: .88rem; font-weight: 600; }
  .status span { color: var(--muted); font-weight: 400; }
  @media (max-width: 540px) {
    .map { min-height: 320px; }
    .embedded .map { height: 350px; }
    .workspace-heading :global(.button) { padding-inline: 10px; }
  }
</style>

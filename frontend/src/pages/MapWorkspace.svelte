<script>
  import { onMount } from 'svelte';
  import { Globe } from '@lucide/svelte';
  import FireMap from '../features/fire-monitoring/components/FireMap.svelte';
  import MapLegend from '../features/fire-monitoring/components/MapLegend.svelte';
  import { createGoogleMap } from '../features/fire-monitoring/googleMap.js';
  import { loadVisiblePoints, quadrants } from '../features/fire-monitoring/data/quadrants.js';
  import { countries } from '../features/fire-monitoring/data/demo.js';
  import { mapCopy as copy } from '../content/platform.js';

  const key = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
  let host = $state();
  let provider;
  let active = true;
  let request = 0;
  let googleActive = $state(false);
  let providerError = $state(false);
  let selected = $state('world');
  let viewport;
  let points = $state([]);
  let loading = $state(true);
  let dataError = $state(false);
  const selectedBounds = $derived(countries[selected]?.bounds ?? quadrants.find(({ id }) => id === selected)?.bounds);

  async function update(bounds) {
    viewport = bounds;
    const id = ++request;
    loading = true;
    dataError = false;
    try {
      const result = await loadVisiblePoints(bounds);
      if (!active || id !== request) return;
      points = result;
      provider?.show(result);
    } catch {
      if (!active || id !== request) return;
      points = [];
      provider?.show([]);
      dataError = true;
    } finally {
      if (active && id === request) loading = false;
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
    if (provider) provider.fit(selectedBounds);
    else update(selectedBounds);
  }

  onMount(() => {
    update();
    if (key) {
      createGoogleMap(host, key, bounds => {
        if (active && !providerError) update(bounds);
      }, fallback).then(map => {
        if (!active || providerError) { map.destroy(); return; }
        provider = map;
        googleActive = true;
        provider.show(points);
        if (selectedBounds) provider.fit(selectedBounds);
      }).catch(fallback);
    }
    return () => {
      active = false;
      provider?.destroy();
    };
  });
</script>

<section class="workspace" aria-labelledby="workspace-title">
  <header>
    <p class="eyebrow">{copy.eyebrow}</p>
    <h1 id="workspace-title">{copy.title}</h1>
    <p>{copy.description}</p>
  </header>
  <div class="card map">
    <div class="toolbar">
      <label>
        <Globe size={18} aria-hidden="true" /> {copy.view}
        <select value={selected} onchange={changeView}>
          <option value="world">{copy.world}</option>
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
      <span class="demo-label">{copy.sample}</span>
    </div>
    <div class="map-area">
      {#if key}<div class="google-host" class:ready={googleActive} aria-label={copy.google} bind:this={host}></div>{/if}
      {#if !googleActive}
        <FireMap region="world" id="workspace-map" bounds={selectedBounds} {points} title={copy.title} />
      {/if}
    </div>
    <MapLegend />
    <div class="status">
      <p role="status">{loading ? copy.loading : dataError ? copy.error : copy.points(points.length)}</p>
      {#if dataError}<button type="button" class="button button-outline" onclick={() => update(viewport)}>{copy.retry}</button>{/if}
      {#if providerError}<span>{copy.fallback}</span>{/if}
    </div>
  </div>
</section>

<style>
  .workspace { padding: clamp(26px, 5vw, 58px) var(--page-inset); }
  h1 { margin-block: 6px 10px; font: 700 clamp(3rem, 7vw, 5rem)/1 var(--heading); }
  header > p:last-child { color: var(--muted); line-height: 1.5; }
  .map { margin-top: 20px; overflow: hidden; border-color: var(--accent-border); }
  .toolbar, .status { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 16px; }
  .toolbar { background: var(--accent-surface); }
  label { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
  label :global(svg) { color: var(--accent); }
  select { min-height: 40px; padding: 6px; border: 1px solid var(--border-strong); border-radius: var(--control-radius); color: var(--text); background: var(--background); }
  .map-area { position: relative; min-height: 0; }
  .google-host { position: absolute; inset: 0; visibility: hidden; }
  .google-host.ready { position: relative; width: 100%; height: clamp(360px, 66svh, 800px); visibility: visible; }
  .status { border-top: 1px solid var(--border); color: var(--muted); font-size: .84rem; }
</style>

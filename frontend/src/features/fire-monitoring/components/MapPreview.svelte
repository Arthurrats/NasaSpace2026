<script>
  import { Globe, ScanLine } from '@lucide/svelte';
  import { landingMapCopy as copy } from '../../../content/landing.js';
  import { hotspots, regions } from '../data/demo.js';
  import FireMap from './FireMap.svelte';
  import MapLegend from './MapLegend.svelte';

  let { active = false } = $props();
  let region = $state('southAmerica');
  const viewId = $props.id();
  const choices = Object.entries(regions);
  const shown = $derived(region === 'southAmerica' ? hotspots : hotspots.filter(point => point.country === region));
  const high = $derived(shown.filter(point => point.intensity === 'high').length);
</script>

<figure class="analysis-map" class:motion={active} aria-labelledby="{viewId}-title">
  <figcaption>
    <span class="map-title" id="{viewId}-title"><Globe size={18} aria-hidden="true" /> {copy.title}</span>
    <span class="sample"><span></span>{copy.sample}</span>
  </figcaption>

  <div class="map-frame">
    <FireMap {region} id="{viewId}-map" fill />
    <span class="scan" aria-hidden="true"></span>
    <span class="reticle top" aria-hidden="true"></span>
    <span class="reticle bottom" aria-hidden="true"></span>
    <div class="selected-area"><ScanLine size={15} aria-hidden="true" /> {regions[region].name}</div>
  </div>

  <div class="map-controls" role="group" aria-label={copy.area}>
    {#each choices as [id, { name }] (id)}
      <button type="button" aria-pressed={region === id} onclick={() => { region = id; }}>{name}</button>
    {/each}
  </div>
  <div class="map-footer">
    <MapLegend />
    <dl class="map-summary" aria-live="polite" aria-atomic="true">
      <div><dt>{copy.points}</dt><dd>{shown.length}</dd></div>
      <div><dt>{copy.high}</dt><dd class="hot">{high}</dd></div>
    </dl>
  </div>
</figure>

<style>
  .analysis-map {
    --background: #101b19;
    --surface: #172621;
    --border: #2a4038;
    --border-strong: #426052;
    --text: #f2f5f0;
    --muted: #a4b7ab;
    --indicator: #b6e36b;
    --map-water: #0b1614;
    --map-glow: #1c3027;
    --map-land: #2e503f;
    --map-stroke: #647f6f;
    color-scheme: dark;
    position: relative;
    min-width: 0;
    margin: 0;
    overflow: hidden;
    border: 1px solid var(--border-strong);
    border-radius: var(--card-radius);
    background: var(--background);
    color: var(--text);
    box-shadow: 0 20px 50px #07100eb5;
  }

  figcaption {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 8px 12px;
    padding: 11px 14px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
  }

  .map-title { display: flex; align-items: center; gap: 9px; font-size: .84rem; font-weight: 670; }
  .map-title :global(svg) { color: var(--indicator); flex: none; }
  .sample {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 8px;
    border: 1px solid var(--border);
    border-radius: 99px;
    color: var(--muted);
    font-size: .7rem;
    line-height: 1;
    white-space: nowrap;
  }
  .sample span { width: 6px; height: 6px; border-radius: 50%; background: #ff8a32; }

  .map-frame {
    position: relative;
    height: clamp(224px, 33vw, 429px);
    overflow: hidden;
    isolation: isolate;
    background: var(--map-water);
  }
  .selected-area {
    position: absolute;
    inset: auto auto 12px 12px;
    z-index: 1;
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 6px 8px;
    border: 1px solid var(--border-strong);
    border-radius: 5px;
    background: #101b19e8;
    color: var(--text);
    font-size: .72rem;
    font-weight: 650;
    pointer-events: none;
  }
  .selected-area :global(svg) { color: var(--indicator); flex: none; }
  .reticle {
    position: absolute;
    z-index: 1;
    width: 14px;
    height: 14px;
    border: 1px solid #b6e36b91;
    pointer-events: none;
  }
  .reticle.top { top: 12px; left: 12px; border-right: 0; border-bottom: 0; }
  .reticle.bottom { bottom: 12px; right: 12px; border-top: 0; border-left: 0; }
  .scan {
    position: absolute;
    inset: 0;
    opacity: 0;
    background: linear-gradient(180deg, transparent 47%, #b6e36b09 49%, #b6e36b4a 50%, transparent 51%);
    pointer-events: none;
    animation: scan-map 12s linear infinite paused;
  }
  .motion .scan { opacity: .7; animation-play-state: running; }
  @keyframes scan-map { from { transform: translateY(-51%); } to { transform: translateY(51%); } }

  .map-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 6px;
    padding: 7px 12px;
    border-block: 1px solid var(--border);
    background: var(--surface);
  }
  .map-controls button {
    min-height: 36px;
    padding: 5px 8px;
    border: 1px solid transparent;
    border-radius: 6px;
    background: transparent;
    color: var(--muted);
    font: 600 .72rem var(--body);
    cursor: pointer;
  }
  .map-controls button:hover { border-color: var(--border-strong); color: var(--text); }
  .map-controls button[aria-pressed='true'] { border-color: #597d4b; background: #283c26; color: var(--indicator); }
  .map-controls button:focus-visible { outline: 2px solid var(--indicator); outline-offset: 2px; }

  .map-footer {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0 12px;
    padding: 0 12px;
  }
  .map-footer :global(.map-legend) { gap: 6px 9px; padding: 7px 0; border: 0; font-size: .71rem; }
  .map-summary { display: flex; flex-wrap: wrap; gap: 6px 16px; margin: 0; padding: 7px 0; }
  .map-summary div { display: flex; align-items: baseline; gap: 6px; }
  dt { color: var(--muted); font-size: .71rem; }
  dd { order: -1; margin: 0; color: var(--text); font: 700 1.2rem/1 var(--heading); font-variant-numeric: tabular-nums; }
  dd.hot { color: #ff9d54; }

  @media (max-width: 460px) {
    .map-controls { padding-inline: 8px; }
    .map-controls button { min-height: 40px; }
  }
  @media (prefers-reduced-motion: reduce) {
    .scan, .motion .scan { animation: none; opacity: 0; }
  }
</style>

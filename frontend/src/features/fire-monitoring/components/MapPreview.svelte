<script>
  import { Globe } from '@lucide/svelte';
  import { hotspots, regionalActivity } from '../data/demo.js';
  import FireMap from './FireMap.svelte';
  import MapLegend from './MapLegend.svelte';
</script>

<figure class="card analysis-map" aria-labelledby="preview-map-title">
  <figcaption>
    <span id="preview-map-title"><Globe size={19} aria-hidden="true" /> Mapa global de focos</span>
    <span class="demo-label">Dados simulados</span>
  </figcaption>
  <FireMap id="landing-map" />
  <MapLegend />
  <dl class="map-summary">
    <div><dt>Pontos de exemplo no mapa</dt><dd>{hotspots.length}</dd></div>
    <div><dt>Regiões no comparativo</dt><dd>{regionalActivity.length}</dd></div>
  </dl>
</figure>

<style>
  .analysis-map {
    --map-land: color-mix(in srgb, var(--surface) 84%, var(--accent));
    margin: 0;
    overflow: hidden;
    border-color: var(--border-strong);
    background: var(--background);
    box-shadow: 0 18px 44px color-mix(in srgb, black 24%, transparent);
  }

  figcaption {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
    font-size: .9rem;
    font-weight: 650;
  }

  #preview-map-title { display: flex; align-items: center; gap: 8px; }
  #preview-map-title :global(svg) { color: var(--indicator); }

  .map-summary {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin: 0;
    border-top: 1px solid var(--border);
    background: var(--surface);
  }

  .map-summary div { display: flex; align-items: center; gap: 8px 12px; padding: 10px 18px; }
  .map-summary div + div { border-left: 1px solid var(--border); }
  dt { color: var(--muted); font-size: .75rem; line-height: 1.4; }
  dd { order: -1; margin: 0; color: var(--text); font: 700 1.9rem/1 var(--heading); }

  @media (max-width: 460px) {
    .map-summary div { align-items: flex-start; flex-direction: column; }
  }
</style>

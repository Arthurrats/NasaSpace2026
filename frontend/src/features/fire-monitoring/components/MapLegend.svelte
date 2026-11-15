<script>
  import { confidenceColors, heatGradient } from '../mapLayer.js';
  let { mode, heatLabel = 'Concentração no recorte', palette } = $props();
  const intensity = [
    { level: 'low', label: 'Baixa' },
    { level: 'medium', label: 'Média' },
    { level: 'high', label: 'Alta' },
  ];
</script>

<div class="map-legend">
  {#if mode === 'heat'}
    <span>{heatLabel}</span>
    <span class="legend-key">Menor <span class="heat-scale" style:background={heatGradient(palette)} aria-hidden="true"></span> Maior</span>
  {:else if mode}
    <span>Confiança da detecção</span>
    <div class="confidence-scale">
      {#each intensity as { level, label } (level)}
        <span class="confidence-step">
          <span class="confidence-color" style:background={confidenceColors[level]} aria-hidden="true"></span>
          {label}
        </span>
      {/each}
    </div>
    {#if mode === 'cluster'}<span>Detecções próximas compartilham um marcador.</span>{/if}
  {:else}
    <span>Intensidade</span>
    {#each [...intensity].reverse() as { level, label } (level)}
      <span class="legend-key"><span class="legend-dot intensity-{level}" aria-hidden="true"></span>{label}</span>
    {/each}
  {/if}
</div>

<style>
  .map-legend {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 9px 15px;
    padding: 14px 18px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: .75rem;
  }

  .legend-key { display: inline-flex; align-items: center; gap: 6px; color: var(--text); }
  .heat-scale { width: 100px; height: 9px; border-radius: 99px; }
  .confidence-scale { display: grid; grid-template-columns: repeat(3, 1fr); width: min(100%, 12rem); }
  .confidence-step { display: grid; gap: 3px; text-align: center; color: var(--text); }
  .confidence-color { height: 8px; }
  .confidence-step:first-child .confidence-color { border-radius: 99px 0 0 99px; }
  .confidence-step:last-child .confidence-color { border-radius: 0 99px 99px 0; }
  .legend-dot {
    width: 10px;
    height: 10px;
    border: 1px solid var(--map-marker-outline);
    border-radius: 50%;
    background: var(--intensity-color);
  }
</style>

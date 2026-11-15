<script>
  const intensity = [
    { level: 'high', label: 'Alta' },
    { level: 'medium', label: 'Média' },
    { level: 'low', label: 'Baixa' },
  ];
</script>

<div class="map-legend">
  <span>Intensidade</span>
  {#each intensity as { level, label }}
    <span class="legend-key"><span class="legend-dot intensity-{level}" aria-hidden="true"></span>{label}</span>
  {/each}
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
  .legend-dot {
    width: 10px;
    height: 10px;
    border: 1px solid var(--map-marker-outline);
    border-radius: 50%;
    background: var(--intensity-color);
  }
</style>

<script>
  let { data: suppliedData = [] } = $props();
  const data = $derived(Array.isArray(suppliedData) ? suppliedData : []);
  const maxValue = $derived(Math.max(1, ...data.map(({ value }) => value)));
</script>

{#if data.length}
  <ul class="metric-bars">
    {#each data as { id, label, value, display = value.toLocaleString('pt-BR') } (id ?? label)}
      <li>
        <div class="bar-label"><span>{label}</span><strong>{display}</strong></div>
        <div class="bar-track" role="img" aria-label="{label}: {display}"><div style:width={(value / maxValue * 100) + '%'}></div></div>
      </li>
    {/each}
  </ul>
{:else}
  <p class="empty-state">Nenhuma detecção no período e filtros selecionados.</p>
{/if}

<style>
  .metric-bars { display: grid; gap: 10px; margin: 0; padding: 6px 14px 12px; list-style: none; }
  .bar-label { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 7px; font-size: .8rem; }
  .bar-label span { overflow: hidden; color: var(--muted); text-overflow: ellipsis; white-space: nowrap; }
  .bar-label strong { flex: none; font-variant-numeric: tabular-nums; }
  .bar-track { height: 8px; overflow: hidden; border-radius: 999px; background: var(--background); }
  .bar-track div { height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--accent), var(--indicator)); transition: width 420ms ease; }
</style>

<script>
  let { rows } = $props();
  const formatMonth = new Intl.DateTimeFormat('pt-BR', { month: 'short', timeZone: 'UTC' });
  const formatAxis = new Intl.NumberFormat('pt-BR', { notation: 'compact', maximumFractionDigits: 1 });
  const formatCount = new Intl.NumberFormat('pt-BR');
  const sensors = [
    { id: 'MODIS', color: 'var(--heat)' },
    { id: 'VIIRS', color: 'var(--accent)' },
  ];

  const monthly = $derived.by(() => {
    const months = new Map();
    for (const { month, sensor, detections } of rows) {
      if (!months.has(month)) months.set(month, { MODIS: 0, VIIRS: 0 });
      months.get(month)[sensor] = detections;
    }
    return [...months].sort(([a], [b]) => a.localeCompare(b)).map(([month, counts]) => ({
      month,
      label: formatMonth.format(new Date(month + '-01T00:00:00Z')).replace('.', ''),
      counts,
      total: counts.MODIS + counts.VIIRS,
    }));
  });
  const peak = $derived(Math.max(0, ...monthly.map(row => row.total)));
  const ticks = $derived([...new Set([0, Math.round(peak / 3), Math.round(peak * 2 / 3), peak])]);
  const left = 47;
  const right = 352;
  const top = 14;
  const bottom = 158;
  const step = $derived((right - left) / Math.max(1, monthly.length));
  const barWidth = $derived(Math.min(30, step * .72));
  const y = value => bottom - value / peak * (bottom - top);
</script>

{#if peak > 0}
  <svg class="chart" viewBox="0 0 360 184" role="img" aria-label="Detecções mensais empilhadas por sensor">
    <desc>{monthly.map(({ month, counts }) => month + ' · ' + sensors.map(({ id }) => id + ' ' + formatCount.format(counts[id])).join(', ')).join('. ')}</desc>
    {#each ticks as tick (tick)}
      <line x1={left} x2={right} y1={y(tick)} y2={y(tick)} />
      <text x={left - 7} y={y(tick) + 3} text-anchor="end">{formatAxis.format(tick)}</text>
    {/each}
    {#each monthly as { month, label, counts, total }, index (month)}
      {@const center = left + step * (index + .5)}
      <g>
        <title>{month} · {sensors.map(({ id }) => id + ' ' + formatCount.format(counts[id])).join(' · ')}</title>
        <rect x={center - barWidth / 2} y={y(counts.MODIS)} width={barWidth} height={bottom - y(counts.MODIS)} fill={sensors[0].color} />
        <rect x={center - barWidth / 2} y={y(total)} width={barWidth} height={y(counts.MODIS) - y(total)} fill={sensors[1].color} />
      </g>
      <text x={center} y={bottom + 17} text-anchor="middle">{label}</text>
    {/each}
  </svg>
  <ul class="legend" aria-label="Sensores">
    {#each sensors as { id, color } (id)}
      <li><span style:background={color}></span>{id}</li>
    {/each}
  </ul>
{:else}
  <p class="empty-state">Sem detecções no período selecionado.</p>
{/if}

<style>
  line { stroke: var(--border-strong); stroke-dasharray: 3 4; }
  .legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 0; padding: 0; color: var(--muted); font-size: .75rem; list-style: none; }
  .legend li { display: flex; align-items: center; gap: 5px; }
  .legend span { width: 8px; height: 8px; border-radius: 2px; }
</style>

<script>
  let { days } = $props();
  const formatAxis = new Intl.NumberFormat('pt-BR', { notation: 'compact', maximumFractionDigits: 1 });
  const formatValue = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
  const formatDate = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium', timeZone: 'UTC' });
  const data = $derived(days.filter(row => row.detections > 0));
  const maxCount = $derived(Math.max(1, ...data.map(row => row.detections)));
  const maxFrp = $derived(Math.max(1, ...data.map(row => row.frp_mw)));
  const left = 50;
  const right = 336;
  const top = 20;
  const bottom = 162;
  const x = count => left + count / maxCount * (right - left);
  const y = frp => bottom - frp / maxFrp * (bottom - top);
  const countTicks = $derived([...new Set([0, Math.round(maxCount / 2), maxCount])]);
  const frpTicks = $derived([0, maxFrp / 2, maxFrp]);
</script>

{#if data.length}
  <svg class="chart" viewBox="0 0 360 203" role="img" aria-label="Dispersão entre detecções e FRP acumulada por dia">
    <desc>{data.length} dias com detecções. As escalas vão de zero a {formatValue.format(maxCount)} detecções e de zero a {formatValue.format(maxFrp)} MW.</desc>
    <text x={left} y="12">FRP (MW)</text>
    {#each frpTicks as tick (tick)}
      <line x1={left} x2={right} y1={y(tick)} y2={y(tick)} />
      <text x={left - 7} y={y(tick) + 3} text-anchor="end">{formatAxis.format(tick)}</text>
    {/each}
    {#each countTicks as tick (tick)}
      <line x1={x(tick)} x2={x(tick)} y1={top} y2={bottom} />
      <text x={x(tick)} y={bottom + 15} text-anchor="middle">{formatAxis.format(tick)}</text>
    {/each}
    {#each data as { start_date, detections, frp_mw } (start_date)}
      <circle cx={x(detections)} cy={y(frp_mw)} r="3" class:peak={frp_mw === maxFrp}>
        <title>{formatDate.format(new Date(start_date + 'T00:00:00Z'))} · {formatValue.format(detections)} focos · {formatValue.format(frp_mw)} MW</title>
      </circle>
    {/each}
    <text x={(left + right) / 2} y="196" text-anchor="middle">Detecções por dia</text>
  </svg>
{:else}
  <p class="empty-state">Sem dias com detecções no período selecionado.</p>
{/if}

<style>
  line { stroke: var(--border-strong); stroke-dasharray: 3 4; }
  circle { fill: var(--accent); fill-opacity: .76; stroke: var(--surface); stroke-width: .6; }
  circle.peak, circle:hover { fill: var(--heat); fill-opacity: 1; }
</style>

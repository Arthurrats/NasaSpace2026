<script>
  let { data: suppliedData = [], title = 'Focos de incêndio por dia', unit = 'focos', wide = false, forecastFrom, referenceLabel } = $props();
  const chartId = $props.id();
  const data = $derived(Array.isArray(suppliedData) ? suppliedData : []);
  let measuredWidth = $state(0);
  let activeIndex = $state(null);
  const width = $derived(wide ? Math.max(265, measuredWidth) : 438);
  const height = $derived(wide ? 240 : 190);
  const left = $derived(wide ? 51 : 42);
  const right = $derived(width - 22);
  const axisFormat = new Intl.NumberFormat('pt-BR', { notation: 'compact', maximumFractionDigits: 1 });
  const valueFormat = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });

  const chartBottom = $derived(height - 32);
  const chartTop = 14;
  const maxValue = $derived(Math.max(1, ...data.map(({ value, upper, reference }) => Math.max(upper ?? value, reference ?? 0))));
  const ticks = $derived([...new Set([1, 0.75, 0.5, 0.25, 0].map(ratio => Math.round(maxValue * ratio)))]);
  const x = (index) => data.length === 1 ? (left + right) / 2 : left + index * ((right - left) / Math.max(data.length - 1, 1));
  const y = (value) => chartBottom - value / maxValue * (chartBottom - chartTop);
  const points = $derived(data.map(({ value }, index) => [x(index), y(value)]));
  const path = (positions) => positions.map(([left, top], index) => (index ? 'L' : 'M') + left + ',' + top).join(' ');
  const observed = $derived(points.slice(0, forecastFrom ?? points.length));
  const line = $derived(path(observed));
  const referenceLine = $derived.by(() => {
    if (!referenceLabel) return '';
    let hasPrevious = false;
    return data.map(({ reference }, index) => {
      if (reference == null) {
        hasPrevious = false;
        return '';
      }
      const command = hasPrevious ? 'L' : 'M';
      hasPrevious = true;
      return command + x(index) + ',' + y(reference);
    }).join(' ');
  });
  const area = $derived(line ? line + ' L' + x(observed.length - 1) + ',' + chartBottom + ' L' + x(0) + ',' + chartBottom + ' Z' : '');
  const forecastLine = $derived(forecastFrom == null ? '' : path(points.slice(Math.max(0, forecastFrom - 1))));
  const forecastArea = $derived.by(() => {
    if (forecastFrom == null || forecastFrom >= data.length) return '';
    const forecast = data.slice(forecastFrom);
    const upper = forecast.map((row, index) => [x(forecastFrom + index), y(row.upper)]);
    const lower = forecast.map((row, index) => [x(forecastFrom + index), y(row.lower)]).reverse();
    return path([...upper, ...lower]) + ' Z';
  });
  const labels = $derived.by(() => {
    const count = Math.min(data.length, Math.max(2, Math.floor((right - left) / 62)));
    return Array.from({ length: count }, (_, index) => Math.round(index * (data.length - 1) / Math.max(count - 1, 1)));
  });
  const active = $derived(activeIndex === null ? null : data[activeIndex]);
  function inspect(event) {
    if (!wide || !data.length) return;
    const rectangle = event.currentTarget.getBoundingClientRect();
    const position = (event.clientX - rectangle.left) / rectangle.width * width;
    activeIndex = Math.round(Math.min(1, Math.max(0, (position - left) / (right - left))) * (data.length - 1));
  }
</script>

<div class="trend-wrap" class:wide bind:clientWidth={measuredWidth}>
<svg class="chart trend-chart" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{chartId}-title {chartId}-desc"
  onpointermove={inspect} onpointerleave={() => { activeIndex = null; }}>
  <title id="{chartId}-title">{title}</title>
  <desc id="{chartId}-desc">{data.length <= 24 ? data.map(({ label, value, reference }) => label + ': ' + value + ' ' + unit + (referenceLabel && reference != null ? ' · ' + referenceLabel + ': ' + valueFormat.format(reference) : '')).join(', ') : data.length + ' observações. Escala até ' + valueFormat.format(maxValue) + ' ' + unit}.</desc>
  <defs>
    <linearGradient id="{chartId}-fill" x2="0%" y2="100%">
      <stop stop-color="var(--heat)" stop-opacity=".36" />
      <stop offset="1" stop-color="var(--heat)" stop-opacity="0" />
    </linearGradient>
  </defs>
  {#each ticks as tick}
    <line x1={left} x2={right} y1={y(tick)} y2={y(tick)} class="chart-grid" />
    <text x={left - 8} y={y(tick) + 4} text-anchor="end">{axisFormat.format(tick)}</text>
  {/each}
  <path d={area} fill="url(#{chartId}-fill)" />
  <path d={line} class="trend-line" />
  {#if referenceLine}<path d={referenceLine} class="forecast-line" />{/if}
  {#if forecastLine}
    <path d={forecastArea} class="forecast-area" />
    <path d={forecastLine} class="forecast-line" />
  {/if}
  {#if data.length <= 24}
    {#each data as { label, detail, value }, index}
      <circle cx={x(index)} cy={y(value)} r="3" class="trend-point"><title>{detail ?? label} · {valueFormat.format(value)} {unit}</title></circle>
    {/each}
  {/if}
  {#each labels as index (index)}
    <text x={x(index)} y={height - 10} text-anchor="middle">{data[index].label}</text>
  {/each}
  {#if active}
    <line x1={x(activeIndex)} x2={x(activeIndex)} y1={chartTop} y2={chartBottom} class="chart-cursor" />
    <circle cx={x(activeIndex)} cy={y(active.value)} r="4" class="trend-point" />
  {/if}
</svg>
{#if active}
  <output class="trend-tooltip">{active.detail ?? active.label} · {valueFormat.format(active.value)} {unit}{#if active.lower != null} · faixa de {valueFormat.format(active.lower)} a {valueFormat.format(active.upper)}{/if}{#if referenceLabel && active.reference != null} · {referenceLabel} {valueFormat.format(active.reference)}{/if}</output>
{/if}
</div>

<style>
  .trend-line { fill: none; stroke: var(--heat); stroke-width: 2.5; stroke-linejoin: round; }
  .forecast-line { fill: none; stroke: var(--accent); stroke-width: 2.5; stroke-dasharray: 5 4; }
  .forecast-area { fill: var(--accent); opacity: .18; }
  .trend-point { fill: var(--heat); stroke: var(--surface); stroke-width: 1.5; }
  .chart-grid { stroke: var(--border-strong); stroke-dasharray: 3 4; }
  .trend-wrap { min-width: 0; position: relative; }
  .wide { margin-inline: 10px; }
  .wide .chart { width: 100%; margin: 0; }
  .chart-cursor { stroke: var(--indicator); opacity: .7; }
  .trend-tooltip { position: absolute; right: 22px; top: 3px; padding: 5px 8px; border: 1px solid var(--border); border-radius: var(--control-radius); background: var(--background); color: var(--text); font-size: .74rem; pointer-events: none; }
</style>

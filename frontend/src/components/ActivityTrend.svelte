<script>
  import { dailyActivity } from '../lib/demo.js';

  const ticks = [300, 250, 200, 150, 100, 50, 0];
  const chartBottom = 157;
  const chartTop = 14;
  const x = (index) => 42 + index * 63;
  const y = (value) => chartBottom - value / ticks[0] * (chartBottom - chartTop);
  const points = dailyActivity.map(({ value }, index) => [x(index), y(value)]);
  const line = points.map(([left, top], index) => (index ? 'L' : 'M') + left + ',' + top).join(' ');
  const area = line + ' L' + x(points.length - 1) + ',' + chartBottom + ' L' + x(0) + ',' + chartBottom + ' Z';
</script>

<svg class="chart trend-chart" viewBox="0 0 438 190" role="img" aria-labelledby="trend-title trend-desc">
  <title id="trend-title">Focos de incêndio por dia</title>
  <desc id="trend-desc">{dailyActivity.map(({ label, value }) => label + ': ' + value).join(', ')}. Dados de exemplo.</desc>
  <defs>
    <linearGradient id="trend-fill" x2="0%" y2="100%">
      <stop stop-color="#ff895c" stop-opacity=".35" />
      <stop offset="1" stop-color="#ff895c" stop-opacity=".02" />
    </linearGradient>
  </defs>
  {#each ticks as tick}
    <line x1="36" x2="424" y1={y(tick)} y2={y(tick)} class="chart-grid" />
    <text x="0" y={y(tick) + 4}>{tick}</text>
  {/each}
  <path d={area} fill="url(#trend-fill)" />
  <path d={line} class="trend-line" />
  {#each dailyActivity as { label, value }, index}
    <circle cx={x(index)} cy={y(value)} r="3.5" class="trend-point"><title>{label} · {value} focos</title></circle>
    <text x={x(index)} y="180" text-anchor="middle">{label}</text>
  {/each}
</svg>

<style>
  .trend-line { fill: none; stroke: var(--accent); stroke-width: 2.5; stroke-linejoin: round; }
  .trend-point { fill: var(--accent); stroke: #192321; stroke-width: 1.5; }
  .chart-grid { stroke: #32423d; stroke-dasharray: 3 4; }
</style>

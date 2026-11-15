<script>
  let { data: suppliedData = [], title = 'Comparação de focos por país em 3D' } = $props();
  const chartId = $props.id();
  const data = $derived(Array.isArray(suppliedData) ? suppliedData : []);

  const maxValue = $derived(Math.max(1, ...data.map(({ value }) => value)));
  const axis = $derived([0, 0.2, 0.4, 0.6, 0.8, 1].map(ratio => Math.round(maxValue * ratio)));
  const scale = $derived(120 / maxValue);
  const gridTop = 157;
  const barDepth = 13;
  const barWidth = $derived(Math.min(42, 220 / Math.max(data.length, 1)));

  function barFaces(value, index) {
    const left = 77 + index * (300 / Math.max(data.length, 1));
    const right = left + barWidth;
    const top = gridTop - value * scale;
    const front = [[left, top], [right, top], [right, gridTop], [left, gridTop]];
    const upper = [[left, top], [left + barDepth, top - 8], [right + barDepth, top - 8], [right, top]];
    const side = [[right, top], [right + barDepth, top - 8], [right + barDepth, gridTop - 8], [right, gridTop]];
    return { left, top, front: front.join(' '), upper: upper.join(' '), side: side.join(' ') };
  }
</script>

<svg class="chart depth-chart" viewBox="0 0 438 191" role="img" aria-labelledby="{chartId}-title {chartId}-desc">
  <title id="{chartId}-title">{title}</title>
  <desc id="{chartId}-desc">{data.map(({ label, value }) => label + ': ' + value).join(', ')}.</desc>
  <path d="M48 168 L88 143 H418 L379 168 Z" fill="var(--surface-raised)" stroke="var(--border-strong)" />
  <path d="M48 168 L88 143 V23" fill="none" stroke="var(--border-strong)" />
  {#each axis as tick}
    {@const y = gridTop - tick * scale}
    <path d="M48 {y + 11} L88 {y - 14} H418" fill="none" stroke="var(--border-strong)" stroke-dasharray="3 4" opacity=".8" />
    <text x="8" y={y + 14}>{tick}</text>
  {/each}
  {#each data as { label, value, emphasized }, index}
    {@const bar = barFaces(value, index)}
    <g class:muted-bar={emphasized === false}>
      <title>{label} · {value} focos</title>
      <polygon points={bar.front} fill="var(--accent)" />
      <polygon points={bar.side} class="bar-side" />
      <polygon points={bar.upper} fill="var(--indicator)" />
      <text x={bar.left + barWidth / 2} y={bar.top - 15} text-anchor="middle" class="value">{value}</text>
      <text x={bar.left + barWidth / 2} y="184" text-anchor="middle">{label.length > 8 ? label.slice(0, 7) + '…' : label}</text>
    </g>
  {/each}
</svg>

<style>
  .bar-side { fill: color-mix(in srgb, var(--accent) 55%, var(--surface)); }
  .muted-bar polygon { opacity: .38; }
  .value { fill: var(--text); font-weight: 650; }
</style>

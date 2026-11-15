<script>
  import { regionalActivity } from '../data/demo.js';

  const axis = [0, 100, 200, 300, 400, 500];
  const scale = 0.24;
  const gridTop = 157;
  const barDepth = 13;
  const barWidth = 29;

  function barFaces(value, index) {
    const left = 77 + index * 67;
    const right = left + barWidth;
    const top = gridTop - value * scale;
    const front = [[left, top], [right, top], [right, gridTop], [left, gridTop]];
    const upper = [[left, top], [left + barDepth, top - 8], [right + barDepth, top - 8], [right, top]];
    const side = [[right, top], [right + barDepth, top - 8], [right + barDepth, gridTop - 8], [right, gridTop]];
    return { left, top, front: front.join(' '), upper: upper.join(' '), side: side.join(' ') };
  }
</script>

<svg class="chart depth-chart" viewBox="0 0 438 191" role="img" aria-labelledby="depth-title depth-desc">
  <title id="depth-title">Comparação de focos por país em 3D</title>
  <desc id="depth-desc">{regionalActivity.map(({ label, value }) => label + ': ' + value).join(', ')}. Dados de exemplo.</desc>
  <path d="M48 168 L88 143 H418 L379 168 Z" fill="var(--surface-raised)" stroke="var(--border-strong)" />
  <path d="M48 168 L88 143 V23" fill="none" stroke="var(--border-strong)" />
  {#each axis as tick}
    {@const y = gridTop - tick * scale}
    <path d="M48 {y + 11} L88 {y - 14} H418" fill="none" stroke="var(--border-strong)" stroke-dasharray="3 4" opacity=".8" />
    <text x="8" y={y + 14}>{tick}</text>
  {/each}
  {#each regionalActivity as { label, value }, index}
    {@const bar = barFaces(value, index)}
    <g>
      <title>{label} · {value} focos</title>
      <polygon points={bar.front} fill="var(--accent)" />
      <polygon points={bar.side} class="bar-side" />
      <polygon points={bar.upper} fill="var(--indicator)" />
      <text x={bar.left + barWidth / 2} y={bar.top - 15} text-anchor="middle" class="value">{value}</text>
      <text x={bar.left + barWidth / 2} y="184" text-anchor="middle">{label}</text>
    </g>
  {/each}
</svg>

<style>
  .bar-side { fill: color-mix(in srgb, var(--accent) 55%, var(--surface)); }
  .value { fill: var(--text); font-weight: 650; }
</style>

<script>
  import { regionalActivity } from '../lib/demo.js';

  const axis = [0, 100, 200, 300, 400, 500];
  const scale = 0.24;
  const gridTop = 157;
  const barDepth = 13;
  const barWidth = 29;
  const shortLabels = ['A. Sul', 'África', 'Ásia', 'Oceania', 'Europa'];
  const colors = [
    { front: '#f77d52', top: '#ffaa7e', side: '#a7442f' },
    { front: '#e9a264', top: '#ffc492', side: '#9c693f' },
    { front: '#d0b97c', top: '#e8d39c', side: '#907d4c' },
    { front: '#82ad92', top: '#a7cbb4', side: '#53765f' },
    { front: '#639b91', top: '#8dbeb4', side: '#3b6860' },
  ];

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
  <title id="depth-title">Comparação de focos por região em 3D</title>
  <desc id="depth-desc">{regionalActivity.map(({ label, value }) => label + ': ' + value).join(', ')}. Dados de exemplo.</desc>
  <path d="M48 168 L88 143 H418 L379 168 Z" fill="#233531" stroke="#344d43" />
  <path d="M48 168 L88 143 V23" fill="none" stroke="#3b5046" />
  {#each axis as tick}
    {@const y = gridTop - tick * scale}
    <path d="M48 {y + 11} L88 {y - 14} H418" fill="none" stroke="#3c5149" stroke-dasharray="3 4" opacity=".8" />
    <text x="8" y={y + 14}>{tick}</text>
  {/each}
  {#each regionalActivity as { label, value }, index}
    {@const bar = barFaces(value, index)}
    {@const color = colors[index]}
    <g>
      <title>{label} · {value} focos</title>
      <polygon points={bar.front} fill={color.front} />
      <polygon points={bar.side} fill={color.side} />
      <polygon points={bar.upper} fill={color.top} />
      <text x={bar.left + barWidth / 2} y={bar.top - 15} text-anchor="middle" class="value">{value}</text>
      <text x={bar.left + barWidth / 2} y="184" text-anchor="middle">{shortLabels[index]}</text>
    </g>
  {/each}
</svg>

<style>
  .value { fill: var(--text); font-weight: 650; }
</style>

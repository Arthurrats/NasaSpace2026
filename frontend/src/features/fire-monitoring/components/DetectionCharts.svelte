<script>
  import { BarChart3, CalendarDays, ChartScatter, PieChart } from '@lucide/svelte';
  import Skeleton from '../../../components/Skeleton.svelte';
  import DetectionHeatmap from './DetectionHeatmap.svelte';
  import FrpScatterChart from './FrpScatterChart.svelte';
  import MonthlySensorChart from './MonthlySensorChart.svelte';

  let { summary, loading } = $props();
  const daily = $derived(summary?.series?.day ?? []);
  const total = $derived(summary?.total_detections ?? 0);
  const samples = $derived(summary?.frp_distribution?.samples);
  const coverage = $derived(total > 0 && Number.isInteger(samples) && samples >= 0 && samples <= total ? samples / total : null);
  const formatCount = new Intl.NumberFormat('pt-BR');
  const formatPercent = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 });
</script>

<section class="detection-charts" aria-labelledby="detection-charts-title" aria-busy={loading}>
  <h2 id="detection-charts-title">Perfil das detecções</h2>
  <div class="chart-grid">
    {#if loading}
      {#each Array(4) as _}
        <article class="card placeholder" aria-hidden="true">
          <Skeleton width="min(60%, 16rem)" />
          <Skeleton width="min(82%, 21rem)" height=".8rem" />
          <Skeleton height="clamp(140px, 20vw, 235px)" />
        </article>
      {/each}
    {:else}
      <article class="card" aria-labelledby="sensor-month-title">
        <header>
          <h3 id="sensor-month-title"><BarChart3 size={17} aria-hidden="true" /> Detecções mensais por sensor</h3>
          <p>Cada coluna soma os focos detectados por MODIS e VIIRS no mês.</p>
        </header>
        <MonthlySensorChart rows={summary.monthly_comparison.sensor} />
      </article>

      <article class="card" aria-labelledby="frp-coverage-title">
        <header>
          <h3 id="frp-coverage-title"><PieChart size={17} aria-hidden="true" /> Cobertura de FRP</h3>
          <p>Proporção de detecções com uma medição válida de potência radiativa.</p>
        </header>
        {#if coverage !== null}
          <div class="coverage">
            <div class="coverage-ring" style:--coverage={coverage * 100 + '%'} aria-hidden="true">
              <div><strong>{formatPercent.format(coverage)}</strong><span>com FRP válida</span></div>
            </div>
            <ul aria-label="Cobertura de potência radiativa">
              <li><span class="swatch valid" aria-hidden="true"></span><span>Com FRP válida</span><strong>{formatCount.format(samples)}</strong><small>{formatPercent.format(coverage)}</small></li>
              <li><span class="swatch missing" aria-hidden="true"></span><span>Sem FRP válida</span><strong>{formatCount.format(total - samples)}</strong><small>{formatPercent.format(1 - coverage)}</small></li>
            </ul>
          </div>
        {:else}
          <p class="empty-state">Sem dados de cobertura de FRP no período selecionado.</p>
        {/if}
      </article>

      <article class="card" aria-labelledby="weekday-month-title">
        <header>
          <h3 id="weekday-month-title"><CalendarDays size={17} aria-hidden="true" /> Atividade por dia da semana</h3>
          <p>Média diária de focos em cada mês, incluindo os dias sem detecções.</p>
        </header>
        <DetectionHeatmap days={daily} />
      </article>

      <article class="card" aria-labelledby="frp-scatter-title">
        <header>
          <h3 id="frp-scatter-title"><ChartScatter size={17} aria-hidden="true" /> Detecções × potência radiativa</h3>
          <p>Cada ponto é um dia com focos. O eixo vertical mostra a soma da FRP válida.</p>
        </header>
        <FrpScatterChart days={daily} />
      </article>
    {/if}
  </div>
</section>

<style>
  .detection-charts { display: grid; gap: 14px; margin: 30px 0; }
  h2 { font: 700 1.8rem/1.1 var(--heading); }
  .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 375px), 1fr)); gap: var(--workspace-gap); }
  .chart-grid > article { padding-bottom: 12px; }
  .chart-grid > .placeholder { display: grid; gap: 8px; padding: 12px 14px; }
  header { display: grid; gap: 5px; padding: var(--panel-padding); padding-bottom: 12px; }
  h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 1.08rem; font-weight: 670; }
  h3 :global(svg) { color: var(--indicator); }
  header p { color: var(--muted); font-size: .875rem; line-height: 1.5; }
  article :global(.empty-state) { padding: 18px 14px; color: var(--muted); font-size: .85rem; }
  .coverage { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 14px; padding: 10px 14px; }
  .coverage-ring {
    display: grid;
    place-items: center;
    flex: none;
    width: clamp(160px, 16vw, 208px);
    aspect-ratio: 1;
    border-radius: 50%;
    background: conic-gradient(var(--accent) 0 var(--coverage), var(--heat) var(--coverage) 100%);
  }
  .coverage-ring > div {
    display: grid;
    place-content: center;
    gap: 3px;
    width: 76%;
    aspect-ratio: 1;
    border-radius: 50%;
    background: var(--surface);
    text-align: center;
  }
  .coverage-ring strong { font: 700 clamp(1.65rem, 3vw, 2.6rem)/1 var(--heading); }
  .coverage-ring span { color: var(--muted); font-size: .7rem; }
  ul { display: grid; flex: 1 1 180px; gap: 10px; max-width: 290px; margin: 0; padding: 0; list-style: none; }
  li { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 2px 6px; font-size: .85rem; }
  li strong, li small { font-variant-numeric: tabular-nums; }
  li small { grid-column: 3; text-align: right; color: var(--muted); font-size: .7rem; }
  .swatch { width: 8px; height: 8px; border-radius: 2px; }
  .valid { background: var(--accent); }
  .missing { background: var(--heat); }

  @media (max-width: 760px) { .chart-grid { grid-template-columns: minmax(0, 1fr); } }
</style>

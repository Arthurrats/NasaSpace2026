<script>
  import { untrack } from 'svelte';
  import { Activity, Box, Flame, Globe, SlidersHorizontal, TrendingUp } from '@lucide/svelte';
  import Skeleton from '../components/Skeleton.svelte';
  import ActivityTrend from '../features/fire-monitoring/components/ActivityTrend.svelte';
  import DetectionCharts from '../features/fire-monitoring/components/DetectionCharts.svelte';
  import MetricBars from '../features/fire-monitoring/components/MetricBars.svelte';
  import ThreeCountryChart from '../features/fire-monitoring/components/ThreeCountryChart.svelte';
  import SectorBubbleChart from '../features/fire-monitoring/components/SectorBubbleChart.svelte';
  import PeriodFields from '../features/fire-monitoring/components/PeriodFields.svelte';
  import WorldGridMap from '../features/fire-monitoring/components/WorldGridMap.svelte';
  import MapWorkspace from './MapWorkspace.svelte';
  import { periodLabel } from '../features/fire-monitoring/data/timeline.js';
  import { countriesQuery, summaryQuery } from '../features/fire-monitoring/data/summary.js';

  import { dashboardCopy as copy, sectorNames, sectorMetrics } from '../content/platform.js';
  let { countryOnly = false } = $props();
  let dashboardTitle;
  let country = $state(untrack(() => countryOnly ? 'brasil' : 'all'));
  let sensor = $state('all');
  let sector = $state('all');
  let sectorMetric = $state('detections');
  let startDate = $state('2025-01-01');
  let endDate = $state('2025-12-31');
  let timeStep = $state('day');
  let summaryRequest = $state.raw(untrack(filtersQuery));
  const availableCountries = $derived($countriesQuery.data ?? []);
  const countriesLoading = $derived($countriesQuery.status === 'loading');
  const countriesError = $derived($countriesQuery.status === 'error');
  const summary = $derived($summaryRequest.data);
  const loading = $derived($summaryRequest.status === 'loading');
  const apiError = $derived($summaryRequest.error?.message);
  const visibleCountries = $derived(summary?.by_country ?? []);
  const selectedMetric = $derived(sectorMetrics.find(metric => metric.key === sectorMetric));
  const sectorValues = $derived.by(() => {
    const totals = new Map(summary?.by_sector?.map(row => [row.sector, row]) ?? []);
    return sectorNames.map((label, index) => ({ label, value: totals.get(index)?.[sectorMetric] ?? null }));
  });
  const regionalRanking = $derived((summary?.sector_rankings?.[sectorMetric] ?? []).map(index => sectorValues[index]).map(({ label, value }) => ({
    label, value, display: value.toLocaleString('pt-BR', { maximumFractionDigits: 2 }) + (selectedMetric.unit ? ' ' + selectedMetric.unit : ''),
  })));
  const monthLabels = new Intl.DateTimeFormat('pt-BR', { month: 'short', timeZone: 'UTC' });
  const matrix = $derived(countryOnly ? [] : (summary?.monthly_comparison?.country ?? []).map(row => ({ ...row, series: row.country })));
  const charts3d = $derived([
    { title: 'Detecções por mês', unit: 'focos', rows: matrix.map(row => ({ ...row, value: row.detections })) },
    { title: 'FRP por mês', unit: 'MW', rows: matrix.map(row => ({ ...row, value: row.frp_mw })) },
  ]);
  const shortDate = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', timeZone: 'UTC' });
  const timeSeries = $derived((summary?.series?.[timeStep] ?? []).map(row => {
    const start = Date.parse(row.start_date);
    const label = timeStep === 'month' ? monthLabels.format(start).replace('.', '') : shortDate.format(start);
    return { label, detail: periodLabel(row.start_date, row.end_date), detections: row.detections, frp: row.frp_mw };
  }));
  const chartActivity = $derived(timeSeries.map(row => ({ ...row, value: row.detections })));
  const chartFrp = $derived(timeSeries.map(row => ({ ...row, value: row.frp })));
  const byHour = $derived((summary?.by_hour ?? []).map(row => ({
    label: String(row.hour).padStart(2, '0') + 'h', value: row.detections,
  })));
  const frpBands = ['0 a <10 MW', '10 a <50 MW', '50 a <100 MW', '100 a <500 MW', '500 MW ou mais'];
  const frpStats = $derived(summary?.frp_distribution);
  const units = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
  const asMw = value => value == null ? '–' : units.format(value) + ' MW';
  const sensorActivity = $derived((summary?.by_sensor ?? []).map(({ sensor }) => {
    const rows = summary.monthly_comparison.sensor.filter(row => row.sensor === sensor);
    return {
      sensor,
      data: rows.map(row => ({
        label: monthLabels.format(new Date(row.month + '-01T00:00:00Z')).replace('.', ''),
        value: row.detections,
      })),
    };
  }));
  const sensorComparison = $derived(summary?.by_sensor?.map(({ sensor, detections }) => ({ id: sensor, label: sensor, value: detections })) ?? []);
  const intensityComparison = $derived(summary?.by_intensity?.map(({ intensity, detections }) => ({ id: intensity, label: ({ high: 'Alta', medium: 'Média', low: 'Baixa' })[intensity] ?? intensity, value: detections })) ?? []);
  const daylight = { day: 'Dia', night: 'Noite', unknown: 'Sem classificação' };
  const frpBars = (rows, field) => rows.map(row => ({
    label: row[field],
    value: row.frp_mw,
    display: row.frp_mw.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' MW',
  })).sort((a, b) => b.value - a.value);
  const charts2d = $derived([
    { title: 'Focos por sensor', rows: sensorComparison },
    { title: 'FRP por sensor', rows: frpBars(summary?.by_sensor ?? [], 'sensor') },
    { title: 'Detecções por confiança', rows: intensityComparison },
    { title: 'Detecções por dia e noite', rows: (summary?.by_daynight ?? []).map(row => ({ label: daylight[row.period], value: row.detections })) },
    { title: 'Detecções por satélite', rows: (summary?.by_satellite ?? []).map(row => ({ label: row.satellite === 'unknown' ? 'Sem identificação' : row.satellite, value: row.detections })) },
    { title: 'Detecções por faixa de FRP', rows: (summary?.by_frp_band ?? []).map(row => ({ label: frpBands[row.band], value: row.detections })) },
    ...(!countryOnly ? [{ title: 'FRP por país', rows: frpBars(visibleCountries, 'country') }] : []),
  ]);
  const visibleTotal = $derived(summary?.total_detections ?? 0);
  const peakCount = $derived(summary?.peak_day?.detections ?? 0);
  const observedMetrics = $derived([
    { id: 'hotspots', label: 'Focos de calor', value: visibleTotal.toLocaleString('pt-BR'), detail: 'Detecções observadas' },
    { id: 'frp', label: 'Potência radiativa', value: (summary?.total_frp_mw ?? 0).toLocaleString('pt-BR', { maximumFractionDigits: 1 }), detail: 'Soma de FRP · MW' },
    { id: 'regions', label: countryOnly ? 'Sensores com detecções' : 'Países com detecções', value: countryOnly ? sensorComparison.length : visibleCountries.length, detail: 'No recorte filtrado' },
    { id: 'average', label: 'Média diária', value: (summary?.average_daily_detections ?? 0).toLocaleString('pt-BR'), detail: 'Focos por dia observado' },
    { id: 'peak', label: 'Dia de maior atividade', value: peakCount.toLocaleString('pt-BR'), detail: summary?.peak_day?.date ?? 'Sem dados no período' },
    { id: 'median', label: 'FRP mediana', value: asMw(frpStats?.median_mw), detail: 'Entre detecções com FRP válida' },
  ]);
  const metricIcons = { hotspots: Flame, regions: Globe, frp: Activity, average: TrendingUp, peak: Box, median: Activity };

  function filtersQuery() {
    return summaryQuery({ sensor, country, startDate, endDate, sector, countryOnly });
  }

  function applyFilters(event) {
    event.preventDefault();
    const next = filtersQuery();
    if (next.key === summaryRequest.key) summaryRequest.refresh();
    else summaryRequest = next;
  }

  function showIndicators() {
    dashboardTitle?.focus({ preventScroll: true });
    dashboardTitle?.scrollIntoView({ block: 'start' });
  }
</script>

{#snippet chartSkeleton(height)}
  <div class="card chart-card skeleton-chart" aria-hidden="true">
    <Skeleton width="min(55%, 16rem)" />
    <Skeleton {height} />
  </div>
{/snippet}

<div class="dashboard-content">
  {#if !countryOnly}<MapWorkspace embedded onViewIndicators={showIndicators} />{/if}
  <section class="dashboard-intro" aria-labelledby="dashboard-title">
    <div>
      <p class="eyebrow"><span class="status-dot"></span> {copy.label}</p>
      <h1 id="dashboard-title" tabindex="-1" bind:this={dashboardTitle}>{countryOnly ? 'Análise por país' : copy.title}</h1>
      <p>{countryOnly ? 'Compare focos, potência radiativa e cobertura dos sensores por setor do país.' : copy.description}</p>
    </div>
    <span class="demo-label">Dados observados · 2025</span>
  </section>

  <form class="filter-panel card" aria-label="Filtros dos dados observados" onsubmit={applyFilters}>
    <h2 class="filter-heading"><SlidersHorizontal size={19} aria-hidden="true" /> Filtrar dados</h2>
    <label>País
      {#if countriesLoading}
        <span class="sr-only" role="status">Carregando países…</span>
        <Skeleton width="14rem" height="42px" />
      {:else}
        <select class="data-control" bind:value={country} disabled={loading} onchange={() => { sector = 'all'; }}>
          {#if !countryOnly}<option value="all">América do Sul · todos os países</option>{/if}
          {#if countryOnly && !availableCountries.length}<option value="brasil">Brasil</option>{/if}
          {#each availableCountries as item (item.id)}
            <option value={item.id}>{item.name}</option>
          {/each}
        </select>
      {/if}
    </label>
    {#if countryOnly}
      <label>Setor
        <select class="data-control" bind:value={sector} disabled={loading}>
          <option value="all">Todos os setores</option>
          {#each sectorNames as name, index (name)}<option value={String(index)}>{name}</option>{/each}
        </select>
      </label>
    {/if}
    <label>Sensor
      <select class="data-control" bind:value={sensor}><option value="all">MODIS + VIIRS</option><option value="modis">MODIS</option><option value="viirs">VIIRS</option></select>
    </label>
    <PeriodFields bind:start={startDate} bind:end={endDate} />
    <button type="submit" class="button button-primary" disabled={loading}>{loading ? 'Consultando…' : 'Aplicar filtros'}</button>
    {#if countriesError}
      <p role="alert">Não foi possível carregar a lista de países. <button type="button" class="retry-link" onclick={() => countriesQuery.refresh()}>Tentar novamente</button></p>
    {/if}
    {#if apiError}<p role="alert">{apiError}</p>{:else}<p>Dados históricos observados · sem previsões. FRP em MW; classes de confiança por sensor.</p>{/if}
  </form>

  {#if loading}<p class="sr-only" role="status">Carregando dados observados…</p>{/if}
  {#if loading || summary}
  <div class="metric-grid" aria-label={copy.metrics} aria-busy={loading}>
    {#each observedMetrics as metric (metric.id)}
      {@const Icon = metricIcons[metric.id]}
      <section class="card metric" data-metric={metric.id}>
        <h2>{metric.label}</h2>
        <span class="metric-icon"><Icon size={18} /></span>
        {#if loading}
          <strong><Skeleton width="5rem" height="1em" /></strong>
          <span class="metric-detail"><Skeleton width="9rem" height=".85em" /></span>
        {:else}
          <strong>{metric.value}</strong>
          <span class="metric-detail">{metric.detail}</span>
        {/if}
      </section>
    {/each}
  </div>
  {/if}

  {#if loading}
    {#if countryOnly}
      {@render chartSkeleton('var(--chart-height)')}
    {:else}
      <div class="overview-grid">
        {#each charts3d as chart (chart.title)}
          {@render chartSkeleton('var(--chart-height)')}
        {/each}
      </div>
      <DetectionCharts {summary} {loading} />
    {/if}
    <div class="series-panel">
      {#each Array(3) as _}{@render chartSkeleton('clamp(248px, 28vw, 304px)')}{/each}
    </div>
    <div class="overview-grid charts-2d">
      {#each charts2d as chart (chart.title)}{@render chartSkeleton('8rem')}{/each}
    </div>
  {:else if summary}

  {#if countryOnly}
  <section class="card chart-card sector-panel" aria-label="Comparativo dos setores do país">
    <header class="card-header">
      <div><h2><Globe size={17} /> Setores do país · Bolhas 3D</h2><p>Setores traçados a partir das coordenadas. O volume da bolha indica o valor da métrica.</p></div>
      <label>Métrica <select class="data-control" bind:value={sectorMetric}>
        {#each sectorMetrics as metric (metric.key)}<option value={metric.key}>{metric.label}</option>{/each}
      </select></label>
    </header>
    <div class="sector-layout">
      <div>
        <SectorBubbleChart rows={sectorValues} selected={summary.filters?.sector ?? 'all'} />
        <div class="compass" aria-label="Orientação original da grade">
          {#each sectorNames as name (name)}<span>{name}</span>{/each}
        </div>
      </div>
      <div class="bar-list"><MetricBars data={regionalRanking} /></div>
    </div>
  </section>
  {:else}
  <section class="card chart-card sector-panel" aria-labelledby="global-grid-title">
    <header class="card-header">
      <h2 id="global-grid-title"><Globe size={17} /> Distribuição geográfica</h2>
    </header>
    <WorldGridMap cells={summary.grid ?? []} rankings={summary.grid_rankings} countries={visibleCountries} />
  </section>
  <div class="overview-grid">
    {#each charts3d as chart (chart.title)}
      <section class="card chart-card" aria-label={chart.title + ' em 3D'}>
        <header class="card-header">
          <div><h2><Box size={17} /> {chart.title} · 3D</h2><p>Países × meses. Arraste para girar. Use a roda ou a pinça para aproximar.</p></div>
        </header>
        {#if chart.rows.some(row => row.value > 0)}
          <ThreeCountryChart data={chart.rows} unit={chart.unit} />
        {:else}<p class="empty-state">Sem valores no recorte.</p>{/if}
      </section>
    {/each}
  </div>
  <DetectionCharts {summary} {loading} />
  {/if}
  <section class="series-panel" aria-labelledby="series-title">
    <header class="series-header">
      <h2 id="series-title">Séries temporais</h2>
      <label>Intervalo
        <select class="data-control" bind:value={timeStep}>
          <option value="day">Diário</option><option value="week">Semanal</option><option value="month">Mensal</option>
        </select>
      </label>
    </header>
    <section class="card chart-card" aria-labelledby="daily-title">
      <header class="card-header"><h2 id="daily-title"><Activity size={17} /> Detecções ao longo do período</h2></header>
      {#if chartActivity.length}<ActivityTrend roomy data={chartActivity} title="Detecções ao longo do período" wide />{:else}<p class="empty-state">Sem detecções no recorte.</p>{/if}
    </section>
    <section class="card chart-card" aria-labelledby="total-frp-title">
      <header class="card-header"><h2 id="total-frp-title"><TrendingUp size={17} /> FRP acumulada ao longo do período · MW</h2></header>
      {#if chartFrp.length}<ActivityTrend roomy data={chartFrp} title="FRP acumulada ao longo do período" unit="MW" wide />{:else}<p class="empty-state">Sem detecções no recorte.</p>{/if}
    </section>
    <section class="card chart-card" aria-labelledby="hourly-title">
      <header class="card-header"><h2 id="hourly-title"><Activity size={17} /> Horário de detecção · UTC</h2></header>
      {#if byHour.some(row => row.value > 0)}<ActivityTrend roomy data={byHour} title="Detecções por hora UTC" wide />{:else}<p class="empty-state">Sem horários de detecção no recorte.</p>{/if}
    </section>
  </section>

  <div class="overview-grid charts-2d">
    {#if countryOnly}
      {#each sensorActivity as chart (chart.sensor)}
        <section class="card chart-card" aria-label={chart.sensor + ' por mês'}>
          <header class="card-header"><h2>{chart.sensor} por mês</h2></header>
          <ActivityTrend roomy data={chart.data} title={chart.sensor + ' por mês'} />
        </section>
      {/each}
    {/if}
    {#each charts2d as chart (chart.title)}
      <section class="card chart-card" aria-label={chart.title}>
        <header class="card-header"><h2>{chart.title}</h2></header>
        <div class="bar-list"><MetricBars data={chart.rows} /></div>
      </section>
    {/each}
  </div>
  {/if}
</div>

<style>
  .dashboard-content { padding-inline: var(--workspace-inset); }

  .dashboard-intro {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 16px;
    margin-block: clamp(26px, 4vw, 52px) var(--workspace-gap);
  }

  .dashboard-intro h1 {
    margin-block: 7px 8px;
    font-family: var(--heading);
    font-weight: 700;
    letter-spacing: -.015em;
    font-size: var(--workspace-heading);
    line-height: 1;
    scroll-margin-top: 18px;
  }

  .dashboard-intro p:not(.eyebrow) { color: var(--muted); font-size: .95rem; line-height: 1.6; }
  .dashboard-intro .demo-label { flex: none; }

  .metric-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--workspace-gap);
    margin-bottom: var(--workspace-gap);
  }

  .metric {
    --metric-color: var(--indicator);
    background: var(--accent-surface);
    border-color: var(--accent-border);
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 7px 10px;
    padding: var(--panel-padding);
  }

  .metric[data-metric='hotspots'] { --metric-color: var(--heat); }
  .metric[data-metric='peak'] { --metric-color: var(--heat); }
  .metric h2 { color: var(--muted); font-size: .9rem; font-weight: 650; }
  .metric-icon {
    display: grid;
    grid-column: 2;
    grid-row: 1;
    place-items: center;
    width: 38px;
    height: 38px;
    border: 1px solid var(--border);
    border-radius: var(--control-radius);
    background: var(--background);
    color: var(--metric-color);
  }

  .metric strong { grid-column: 1 / -1; font-family: var(--heading); font-size: clamp(1.9rem, 3.2vw, 2.65rem); line-height: 1; }
  .metric-detail { grid-column: 1 / -1; color: var(--muted); font-size: .82rem; }

  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 375px), 1fr));
    margin-bottom: var(--workspace-gap);
    gap: var(--workspace-gap);
  }
  .charts-2d { grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); margin-bottom: 32px; }
  .series-panel { display: grid; gap: var(--workspace-gap); margin: 28px 0; }
  .series-header { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; }
  .series-header h2 { font: 700 1.8rem/1.1 var(--heading); }
  .series-header label { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: .75rem; }
  .bar-list { max-height: 240px; overflow: auto; }
  .sector-panel { margin-bottom: 12px; }
  .sector-panel label { display: flex; gap: 8px; align-items: center; color: var(--muted); font-size: .75rem; }
  .sector-layout { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); align-items: center; gap: 10px; }
  .sector-layout .bar-list { max-height: 255px; }
  .compass { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; max-width: 300px; margin: 0 auto 8px; color: var(--muted); font-size: .68rem; text-align: center; }
  .compass span { padding: 3px; border: 1px solid var(--border); border-radius: var(--control-radius); }

  .filter-panel {
    display: flex;
    flex-wrap: wrap;
    align-items: end;
    gap: 12px 18px;
    margin-bottom: var(--workspace-gap);
    padding: var(--panel-padding);
    background: var(--accent-surface);
    border-color: var(--accent-border);
  }

  .filter-heading { display: flex; align-items: center; gap: 9px; flex-basis: 100%; font-size: 1.06rem; }
  .filter-heading :global(svg) { color: var(--indicator); }
  .filter-panel label { display: grid; gap: 6px; color: var(--muted); font-size: .86rem; font-weight: 650; }
  .filter-panel > p { flex-basis: 100%; margin: 0; color: var(--muted); font-size: .75rem; }
  .filter-panel button:disabled { opacity: .65; cursor: wait; }
  .retry-link { border: 0; padding: 0; color: var(--accent); background: none; text-decoration: underline; }
  .empty-state { padding: 18px; color: var(--muted); font-size: .85rem; }

  .card-header { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; padding: var(--panel-padding); padding-bottom: 12px; }
  .card-header h2 { display: flex; align-items: center; gap: 9px; font-size: 1.12rem; font-weight: 670; }
  .card-header h2 :global(svg) { color: var(--indicator); }
  .card-header p { margin-top: 5px; color: var(--muted); font-size: .875rem; line-height: 1.5; }

  .chart-card { min-width: 0; padding-bottom: 8px; }
  .skeleton-chart { display: grid; gap: 12px; margin-bottom: 12px; padding: 14px; }
  .overview-grid .skeleton-chart, .series-panel .skeleton-chart { margin-bottom: 0; }

  @media (max-width: 760px) {
    .overview-grid { grid-template-columns: 1fr; }
    .sector-layout { grid-template-columns: 1fr; }
    .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }

  @media (max-width: 560px) {
    .dashboard-intro { flex-direction: column; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
    .metric-grid { gap: 10px; }
    .metric { padding: 12px 14px; }
    .metric strong { font-size: 2.2rem; }
    .metric-icon { display: none; }
  }
</style>

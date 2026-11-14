<script>
  import { Activity, Box, ChevronDown, Flame, Globe, MapPin, TrendingUp } from '@lucide/svelte';
  import { metrics, regions, regionalActivity } from '../features/fire-monitoring/data/demo.js';
  import FireMap from '../features/fire-monitoring/components/FireMap.svelte';
  import MapLegend from '../features/fire-monitoring/components/MapLegend.svelte';
  import ActivityTrend from '../features/fire-monitoring/components/ActivityTrend.svelte';
  import RegionalDepth from '../features/fire-monitoring/components/RegionalDepth.svelte';

  let region = $state('world');
  const metricIcons = { hotspots: Flame, regions: Globe, critical: Activity };
</script>

<div class="dashboard-content">
  <section class="dashboard-intro" aria-labelledby="dashboard-title">
    <div>
      <p class="eyebrow"><span class="status-dot"></span> OBSERVATÓRIO DE INCÊNDIOS FLORESTAIS</p>
      <h1 id="dashboard-title">Painel de focos<span>.</span></h1>
      <p>Visualize a distribuição e a intensidade dos focos em um cenário de exemplo.</p>
    </div>
    <span class="demo-label">Dados simulados</span>
  </section>

  <div class="metric-grid" aria-label="Indicadores de exemplo">
    {#each metrics as metric (metric.id)}
      {@const Icon = metricIcons[metric.id]}
      <section class="card metric" data-metric={metric.id}>
        <h2>{metric.label}</h2>
        <span class="metric-icon"><Icon size={18} /></span>
        <strong>{metric.value}</strong>
        <span class="metric-detail">{metric.detail}</span>
      </section>
    {/each}
  </div>

  <div class="overview-grid">
    <section class="card map-card" aria-labelledby="map-title">
      <header class="card-header">
        <div>
          <h2 id="map-title"><Globe size={19} /> Mapa de focos</h2>
          <p>Distribuição geográfica dos pontos de exemplo</p>
        </div>
        <div class="select-wrap">
          <MapPin size={16} />
          <label class="sr-only" for="region">Região do mapa</label>
          <select id="region" bind:value={region}>
            {#each Object.entries(regions) as [value, { name }]}
              <option {value}>{name}</option>
            {/each}
          </select>
          <ChevronDown size={15} />
        </div>
      </header>
      <FireMap {region} id="dashboard-map" />
      <MapLegend />
    </section>

    <section class="card ranking-card" aria-labelledby="ranking-title">
      <header class="card-header">
        <div><h2 id="ranking-title"><TrendingUp size={19} /> Focos por região</h2><p>Comparativo no período</p></div>
      </header>
      <ul class="ranking-list">
        {#each regionalActivity as { label, value }}
          <li>
            <div class="ranking-label"><span>{label}</span><strong>{value}</strong></div>
            <div class="bar-track" aria-hidden="true"><div style:width={(value / regionalActivity[0].value * 100) + '%'}></div></div>
          </li>
        {/each}
      </ul>
    </section>
  </div>

  <div class="chart-grid-layout">
    <section class="card chart-card" aria-labelledby="daily-title">
      <header class="card-header">
        <div><h2 id="daily-title"><Activity size={19} /> Evolução diária</h2><p>Focos ao longo de uma semana de exemplo</p></div>
      </header>
      <ActivityTrend />
    </section>
    <section class="card chart-card" aria-labelledby="regional-title">
      <header class="card-header">
        <div><h2 id="regional-title"><Box size={19} /> Comparativo 3D</h2><p>Focos por região em perspectiva</p></div>
      </header>
      <RegionalDepth />
    </section>
  </div>
</div>

<style>
  .dashboard-content { padding-inline: clamp(12px, 2.5vw, 40px); }

  .dashboard-intro {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 16px;
    margin-block: clamp(24px, 4vw, 46px) 24px;
  }

  .dashboard-intro h1 {
    margin-block: 7px 8px;
    font-family: var(--heading);
    font-weight: 700;
    letter-spacing: -.015em;
    font-size: clamp(3.2rem, 7vw, 6rem);
    line-height: .94;
  }

  .dashboard-intro h1 span { color: var(--accent); }
  .dashboard-intro p:not(.eyebrow) { color: var(--muted); font-size: .95rem; line-height: 1.6; }
  .dashboard-intro .demo-label { flex: none; }

  .metric-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 16px;
  }

  .metric {
    --metric-color: var(--indicator);
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: 5px 8px;
    padding: 16px 18px;
  }

  .metric[data-metric='hotspots'] { --metric-color: var(--heat); }
  .metric[data-metric='critical'] { --metric-color: var(--critical); }
  .metric h2 { color: var(--muted); font-size: .8rem; font-weight: 600; }
  .metric-icon {
    display: grid;
    grid-column: 2;
    grid-row: 1 / 4;
    place-items: center;
    width: 38px;
    height: 38px;
    border: 1px solid var(--border);
    border-radius: var(--control-radius);
    background: var(--background);
    color: var(--metric-color);
  }

  .metric strong { grid-column: 1; font-family: var(--heading); font-size: 2.85rem; line-height: 1; }
  .metric-detail { grid-column: 1; color: var(--muted); font-size: .75rem; }

  .overview-grid {
    display: grid;
    grid-template-columns: minmax(0, 2.05fr) minmax(0, 1fr);
    gap: 16px;
  }

  .map-card { overflow: hidden; }
  .card-header { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; padding: 17px 18px; }
  .card-header h2 { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 670; }
  .card-header h2 :global(svg) { color: var(--indicator); }
  .card-header p { margin-top: 5px; color: var(--muted); font-size: .78rem; line-height: 1.45; }

  .select-wrap { position: relative; display: flex; align-items: center; min-width: 0; max-width: 100%; color: var(--indicator); }
  .select-wrap :global(svg) { position: absolute; pointer-events: none; }
  .select-wrap :global(svg:first-child) { left: 9px; }
  .select-wrap :global(svg:last-child) { right: 9px; }
  .select-wrap select {
    appearance: none;
    max-width: 100%;
    min-height: 44px;
    padding-inline: 30px;
    border: 1px solid var(--border-strong);
    border-radius: var(--control-radius);
    background: var(--background);
    color: var(--text);
    font-size: .78rem;
  }

  .select-wrap select:hover { border-color: var(--indicator); }
  .ranking-card { display: flex; flex-direction: column; }
  .ranking-list {
    flex: 1;
    display: grid;
    align-content: space-evenly;
    gap: 16px;
    margin: 0;
    padding: 4px 18px 20px;
    list-style: none;
  }

  .ranking-label { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 8px; font-size: .82rem; }
  .ranking-label strong { font-variant-numeric: tabular-nums; }
  .bar-track { height: 7px; overflow: hidden; border-radius: 6px; background: var(--background); }
  .bar-track div { height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--accent), var(--indicator)); }

  .chart-grid-layout { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-block: 16px 44px; }
  .chart-card { padding-bottom: 14px; }

  @media (max-width: 760px) {
    .overview-grid, .chart-grid-layout { grid-template-columns: 1fr; }
  }

  @media (max-width: 560px) {
    .dashboard-intro { flex-direction: column; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
    .metric-grid { grid-template-columns: 1fr; gap: 8px; }
    .metric { padding: 12px 14px; }
    .metric strong { font-size: 2.2rem; }
    .chart-grid-layout { margin-bottom: 32px; }
  }
</style>

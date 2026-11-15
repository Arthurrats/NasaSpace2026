<script>
  import { Activity, Box, Flame, Globe, TrendingUp } from '@lucide/svelte';
  import { metrics, regionalActivity } from '../features/fire-monitoring/data/demo.js';
  import ActivityTrend from '../features/fire-monitoring/components/ActivityTrend.svelte';
  import RegionalDepth from '../features/fire-monitoring/components/RegionalDepth.svelte';

  import { dashboardCopy as copy } from '../content/platform.js';
  const metricIcons = { hotspots: Flame, regions: Globe, critical: Activity };
</script>

<div class="dashboard-content">
  <section class="dashboard-intro" aria-labelledby="dashboard-title">
    <div>
      <p class="eyebrow"><span class="status-dot"></span> {copy.label}</p>
      <h1 id="dashboard-title">{copy.title}<span>.</span></h1>
      <p>{copy.description}</p>
    </div>
    <span class="demo-label">{copy.sample}</span>
  </section>

  <div class="metric-grid" aria-label={copy.metrics}>
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
    <section class="card ranking-card" aria-labelledby="ranking-title">
      <header class="card-header">
        <div><h2 id="ranking-title"><TrendingUp size={19} /> {copy.ranking}</h2><p>{copy.rankingDetail}</p></div>
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
    <section class="card chart-card" aria-labelledby="daily-title">
      <header class="card-header">
        <div><h2 id="daily-title"><Activity size={19} /> {copy.daily}</h2><p>{copy.dailyDetail}</p></div>
      </header>
      <ActivityTrend />
    </section>
    <section class="card chart-card" aria-labelledby="regional-title">
      <header class="card-header">
        <div><h2 id="regional-title"><Box size={19} /> {copy.depth}</h2><p>{copy.depthDetail}</p></div>
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
    background: var(--accent-surface);
    border-color: var(--accent-border);
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
    grid-template-columns: repeat(3, minmax(0, 1fr));
    margin-bottom: 44px;
    gap: 16px;
  }

  .card-header { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; padding: 17px 18px; }
  .card-header h2 { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 670; }
  .card-header h2 :global(svg) { color: var(--indicator); }
  .card-header p { margin-top: 5px; color: var(--muted); font-size: .78rem; line-height: 1.45; }

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

  .chart-card { padding-bottom: 14px; }

  @media (max-width: 760px) {
    .overview-grid { grid-template-columns: 1fr; }
  }

  @media (max-width: 560px) {
    .dashboard-intro { flex-direction: column; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
    .metric-grid { grid-template-columns: 1fr; gap: 8px; }
    .metric { padding: 12px 14px; }
    .metric strong { font-size: 2.2rem; }
    }
</style>

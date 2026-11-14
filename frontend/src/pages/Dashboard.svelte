<script>
  import { Activity, Box, ChevronDown, Flame, Globe, MapPin, TrendingUp } from '@lucide/svelte';
  import { metrics, regions, regionalActivity } from '../lib/demo.js';
  import FireMap from '../components/FireMap.svelte';
  import ActivityTrend from '../components/ActivityTrend.svelte';
  import RegionalDepth from '../components/RegionalDepth.svelte';

  let region = $state('world');
  const metricIcons = [Flame, Globe, Activity];
  const intensity = [
    { className: 'high', label: 'Alta' },
    { className: 'medium', label: 'Média' },
    { className: 'low', label: 'Baixa' },
  ];
</script>

<section class="dashboard-intro" aria-labelledby="dashboard-title">
  <div>
    <p class="eyebrow"><span class="status-dot"></span> OBSERVATÓRIO DE INCÊNDIOS FLORESTAIS</p>
    <h1 id="dashboard-title">Painel de focos<span>.</span></h1>
    <p>Visualize a distribuição e a intensidade dos focos em um cenário de exemplo.</p>
  </div>
  <span class="demo-label">Dados simulados</span>
</section>

<div class="metric-grid" aria-label="Indicadores de exemplo">
  {#each metrics as metric, index}
    {@const Icon = metricIcons[index]}
    <section class="card metric">
      <div class="metric-heading"><h2>{metric.label}</h2><span class="metric-icon"><Icon size={18} /></span></div>
      <strong>{metric.value}</strong>
      <span class="muted">{metric.detail}</span>
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
    <div class="map-legend"><span>Intensidade</span>
      {#each intensity as { className, label }}
        <span class="legend-key"><span class="legend-dot {className}"></span>{label}</span>
      {/each}
    </div>
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

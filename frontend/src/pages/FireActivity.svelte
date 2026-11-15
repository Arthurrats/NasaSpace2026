<script>
  import { CalendarDays, ChevronLeft, ChevronRight, Flame, MapPin, Scan } from '@lucide/svelte';
  import ActivityTrend from '../features/fire-monitoring/components/ActivityTrend.svelte';
  import FireMap from '../features/fire-monitoring/components/FireMap.svelte';
  import MapLegend from '../features/fire-monitoring/components/MapLegend.svelte';
  import { formatCount, formatMetric, formatDay, formatDate, fromDate, loadActivity, monthName } from '../features/fire-monitoring/data/activity.js';
  import { regions } from '../features/fire-monitoring/data/demo.js';
  import { accessibleHeatStops } from '../features/fire-monitoring/mapLayer.js';
  import { activityCopy as copy, activityCountries } from '../content/fireActivity.js';

  let { view } = $props();
  const page = $derived(copy[view]);
  const isCalendar = $derived(view === 'calendar');
  const defaultBounds = regions.southAmerica.bounds;
  const [[westLimit, southLimit], [eastLimit, northLimit]] = defaultBounds;
  const coordinates = [
    { key: 'west', label: 'Oeste', min: westLimit, max: eastLimit }, { key: 'south', label: 'Sul', min: southLimit, max: northLimit },
    { key: 'east', label: 'Leste', min: westLimit, max: eastLimit }, { key: 'north', label: 'Norte', min: southLimit, max: northLimit },
  ];
  const weekdays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
  const calendarColors = [1, 3, 5, 8].map(index => accessibleHeatStops[index][1]);
  const signed = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1, signDisplay: 'exceptZero' });
  let draft = $state({ country: 'all', sensor: 'all', west: westLimit, south: southLimit, east: eastLimit, north: northLimit });
  let custom = $state(false);
  let filter = $state({ country: 'all', sensor: 'all', bounds: null });
  let areaError = $state(false);
  let activity = $state();
  let month = $state(0);
  let selectedDate = $state('');
  let loading = $state(true);
  let error = $state(false);
  let mapAttempt = $state(0);
  let pendingTiles = $state(0);
  let mapError = $state(false);
  let drawing = $state(false);

  const activeMonth = $derived(month || activity?.months.find(item => item.critical)?.month || 1);
  const monthCode = $derived(String(activeMonth).padStart(2, '0'));
  const monthSummary = $derived(activity?.months[activeMonth - 1]);
  const monthDays = $derived(activity?.days.filter(row => row.date.slice(5, 7) === monthCode) ?? []);
  const seasonalMonth = $derived(activity?.seasonal?.months[activeMonth - 1]);
  const day = $derived(monthDays.find(row => row.date === (selectedDate || monthSummary?.peak_date)) ?? monthDays[0]);
  const leadingDays = $derived(monthDays.length ? (fromDate(monthDays[0].date).getUTCDay() + 6) % 7 : 0);
  const mapStart = $derived(isCalendar ? day?.date : seasonalMonth?.reference_start_date);
  const mapEnd = $derived(isCalendar ? day?.date : seasonalMonth?.reference_end_date);
  const mapTotal = $derived((isCalendar ? day?.detections : seasonalMonth?.estimate) ?? 0);
  const bounds = $derived(filter.bounds ?? (filter.country === 'all' ? defaultBounds : activity?.bounds ?? defaultBounds));
  const mapPoints = $derived.by(() => {
    if (!mapStart || !mapEnd || !mapTotal) return [];
    const query = new URLSearchParams({ country: filter.country, sensor: filter.sensor, start_date: mapStart, end_date: mapEnd });
    query.set(isCalendar ? 'clip' : 'bbox', bounds.flat().join(','));
    if (isCalendar) query.set('palette', 'accessible');
    if (activity.revision) query.set('v', activity.revision);
    if (mapAttempt) query.set('retry', mapAttempt);
    return { tileQuery: query.toString() };
  });
  const years = $derived(activity?.available_years ?? (activity ? [activity.year] : []));
  const baselineYears = $derived(activity?.baseline_years ?? []);
  const annualTotal = $derived(activity?.total_detections ?? 0);
  const historical = $derived(activity?.months.map(row => ({
    label: monthName(row.month).slice(0, 3), detail: monthName(row.month), value: row.detections, reference: row.baseline_average,
  })) ?? []);
  const observedDays = $derived(activity?.forecast?.training_days ?? 0);
  const series = $derived([
    ...(activity?.days.slice(-observedDays).map(row => ({ ...chartDate(row.date), value: row.detections })) ?? []),
    ...(activity?.forecast?.days.map(row => ({ ...chartDate(row.date), value: row.estimate, lower: row.lower, upper: row.upper })) ?? []),
  ]);

  function chartDate(date) {
    return { label: formatDay.format(fromDate(date)).replace('.', ''), detail: formatDate.format(fromDate(date)) };
  }

  function applyFilter(event) {
    event?.preventDefault();
    const { country, sensor, west, south, east, north } = draft;
    areaError = custom && !(west < east && south < north);
    if (areaError) return;
    drawing = false;
    const year = filter.country === country && filter.sensor === sensor ? filter.year : undefined;
    filter = { country, sensor, year, bounds: custom ? [[west, south], [east, north]] : null };
  }

  function selectArea(rectangle) {
    const [[west, south], [east, north]] = rectangle.map(pair => pair.map(value => Number(value.toFixed(5))));
    if (!(west < east && south < north)) return;
    draft = { ...draft, west, south, east, north };
    custom = true;
    applyFilter();
  }

  function clearArea() {
    custom = false;
    areaError = false;
    drawing = false;
    filter = { ...filter, bounds: null };
  }

  function changeYear(event) {
    drawing = false;
    selectedDate = '';
    filter = { ...filter, year: Number(event.currentTarget.value) };
  }

  function pickMonth(value) {
    month = value;
    selectedDate = '';
  }

  function trackTile(delta) {
    pendingTiles += delta;
  }

  $effect(() => {
    const selection = filter;
    const controller = new AbortController();
    loading = true;
    error = false;
    activity = undefined;
    loadActivity(selection, controller.signal)
      .then(result => { if (!controller.signal.aborted) activity = result; })
      .catch(() => { if (!controller.signal.aborted) error = true; })
      .finally(() => { if (!controller.signal.aborted) loading = false; });
    return () => controller.abort();
  });

  $effect(() => {
    void mapPoints;
    mapError = false;
  });
</script>

{#snippet monthNavigation()}
  <div class="month-navigation" role="group" aria-label="Mês de análise">
    <button type="button" class="month-arrow" aria-label="Mês anterior" title="Mês anterior" disabled={activeMonth === 1} onclick={() => pickMonth(activeMonth - 1)}><ChevronLeft size={20} aria-hidden="true" /></button>
    <select class="data-control month-select" aria-label="Selecionar mês" value={activeMonth} onchange={(event) => pickMonth(Number(event.currentTarget.value))}>
      {#each activity.months as item (item.month)}
        <option value={item.month}>{monthName(item.month)}</option>
      {/each}
    </select>
    <button type="button" class="month-arrow" aria-label="Próximo mês" title="Próximo mês" disabled={activeMonth === 12} onclick={() => pickMonth(activeMonth + 1)}><ChevronRight size={20} aria-hidden="true" /></button>
  </div>
{/snippet}

{#snippet mapPanel()}
  <section class="map-panel" aria-label="Mapa de focos">
    <div class="panel-header">
      <h3><MapPin size={19} aria-hidden="true" /> {isCalendar ? formatDate.format(fromDate(day.date)) : monthName(activeMonth) + ' de ' + activity.seasonal.year}</h3>
      <button type="button" class="button button-outline draw-button" aria-pressed={drawing} onclick={() => { drawing = !drawing; }}>
        <Scan size={16} aria-hidden="true" /> {drawing ? copy.cancelDraw : copy.drawArea}
      </button>
    </div>
    <p aria-live="polite"><strong>{formatCount.format(mapTotal)}</strong> {isCalendar ? 'focos detectados (UTC)' : 'focos projetados · referência de ' + activity.seasonal.reference_year}
      {#if isCalendar} · {formatMetric.format(day.frp_mw)} MW de FRP acumulada{day.unusual ? ' · Acima do padrão' : ''}{/if}</p>
    {#if drawing}<p class="draw-hint" role="status">{copy.drawHint}</p>{/if}
    <FireMap region="world" id="activity-map" bounds={drawing ? defaultBounds : bounds} points={mapPoints} mode={isCalendar ? 'heat' : 'dots'}
      title={isCalendar ? 'Detecções do dia selecionado' : 'Distribuição sazonal de focos projetados'} onAreaSelect={drawing ? selectArea : undefined}
      selectableBounds={defaultBounds} selectionBounds={filter.bounds} onTileError={() => { mapError = true; }} onTilePending={trackTile} />
    {#if filter.bounds}
      <div class="area-status"><span>Área delimitada</span><button type="button" class="clear-area" onclick={clearArea}>{copy.clearArea}</button></div>
    {/if}
    {#if pendingTiles}<p role="status">Carregando focos no mapa…</p>
    {:else if mapError}<p role="alert">{copy.mapFailure}</p><button type="button" class="button button-outline" onclick={() => mapAttempt++}>Tentar novamente</button>
    {:else if mapTotal}
      {#if isCalendar}<MapLegend mode="heat" palette="accessible" heatLabel="Concentração de focos no recorte" />
      {:else}<p class="point-key"><span aria-hidden="true"></span> Focos do mês de referência</p>{/if}
    {:else}<p>Sem focos registrados para a data e a área selecionadas.</p>{/if}
  </section>
{/snippet}

<section class="activity" aria-labelledby="activity-title">
  <header>
    <h1 id="activity-title">{page.title}</h1>
    <p>{page.description}</p>
  </header>

  <form class="card filters" onsubmit={applyFilter} aria-label={copy.area}>
    <div class="filter-row">
      <label>{copy.area}
        <select class="data-control" bind:value={draft.country}>
          {#each Object.entries(activityCountries) as [id, name] (id)}<option value={id}>{name}</option>{/each}
        </select>
      </label>
      <label>Sensor
        <select class="data-control" bind:value={draft.sensor}>
          <option value="all">MODIS + VIIRS</option><option value="modis">MODIS</option><option value="viirs">VIIRS</option>
        </select>
      </label>
      <label class="check"><input type="checkbox" bind:checked={custom} /> {copy.customArea}</label>
      <button type="submit" class="button button-primary">Aplicar filtros</button>
    </div>
    {#if custom}
      <div class="filter-row">
        {#each coordinates as { key, label, min, max } (key)}
          <label>{label} (°)<input class="data-control coordinate" type="number" step="any" {min} {max} bind:value={draft[key]} required /></label>
        {/each}
      </div>
    {/if}
    {#if areaError}<p role="alert">{copy.areaError}</p>{/if}
  </form>

  {#if loading}
    <p role="status" class="card panel">{copy.loading}</p>
  {:else if error}
    <div class="card panel"><p role="alert">{copy.failure}</p><button type="button" class="button button-outline" onclick={() => { filter = { ...filter }; }}>Tentar novamente</button></div>
  {:else if activity}
    {#if !isCalendar}
      <section class="card panel">
        <h2>{page.series}</h2>
        {#if activity.forecast}
          <div class="chart-key"><span class="observed">Observado</span><span class="projected">Projetado</span><span class="range">Faixa empírica</span></div>
          <ActivityTrend data={series} forecastFrom={observedDays} title={page.series} wide />
          <p>Erro absoluto médio retrospectivo de <strong>{formatMetric.format(activity.forecast.mae)} focos/dia</strong> em {activity.forecast.evaluation_windows} janelas de 14 dias.</p>
          <details>
            <summary>Ver valores diários da projeção</summary>
            <table>
              <thead><tr><th scope="col">Data (UTC)</th><th scope="col">Focos estimados</th><th scope="col">Faixa empírica</th></tr></thead>
              <tbody>
                {#each activity.forecast.days as row (row.date)}
                  <tr><th scope="row">{formatDate.format(fromDate(row.date))}</th><td>{formatCount.format(row.estimate)}</td><td>{formatCount.format(row.lower)} a {formatCount.format(row.upper)}</td></tr>
                {/each}
              </tbody>
            </table>
          </details>
        {:else}
          <p role="status">{page.empty}</p>
        {/if}
        <p>{page.seriesMethod}</p>
      </section>
    {/if}

    <section class="card panel activity-panel" aria-labelledby="activity-panel-title">
      <div class="panel-header">
        <div class="panel-heading">
          <h2 id="activity-panel-title">
            {#if isCalendar}<Flame size={22} aria-hidden="true" />{:else}<CalendarDays size={22} aria-hidden="true" />{/if}
            {isCalendar ? page.activity : page.season}
          </h2>
          <p>{activityCountries[filter.country]} · {isCalendar ? activity.year : activity.seasonal.year}{filter.bounds ? ' · Área delimitada' : ''}</p>
        </div>
        {#if years.length > 1}
          <label>{isCalendar ? 'Ano observado' : 'Ano de referência'}
            <select class="data-control" value={activity.year} onchange={changeYear}>
              {#each [...years].reverse() as year (year)}<option value={year}>{year}</option>{/each}
            </select>
          </label>
        {/if}
      </div>
      <div class="calendar-toolbar">
        {@render monthNavigation()}
        {#if isCalendar && monthSummary.critical}<span class="critical-label"><Flame size={15} aria-hidden="true" /> Período crítico</span>{/if}
      </div>
      {#if isCalendar}
        <dl class="metrics" aria-live="polite" aria-label="Indicadores do mês">
          <div><dt>Focos detectados</dt><dd>{formatCount.format(monthSummary.detections)}</dd></div>
          <div><dt>Média diária</dt><dd>{formatMetric.format(monthSummary.daily_average)}</dd></div>
          <div><dt>Dias acima do padrão</dt><dd>{monthSummary.unusual_days}</dd></div>
          <div><dt>Incêndios notificados</dt><dd class:unavailable={monthSummary.reported_incidents == null}>{monthSummary.reported_incidents == null ? 'Sem fonte' : formatCount.format(monthSummary.reported_incidents)}</dd></div>
        </dl>
        <div class="calendar-results">
          <section class="day-panel" aria-label="Calendário diário">
            <div class="day-grid" role="group" aria-label="Selecionar dia do mês">
              {#each weekdays as weekday (weekday)}<span class="weekday">{weekday}</span>{/each}
              {#each Array(leadingDays) as _}<span aria-hidden="true"></span>{/each}
              {#each monthDays as row (row.date)}
                {@const level = row.intensity_level}
                {@const label = formatDate.format(fromDate(row.date)) + ' · ' + formatCount.format(row.detections) + ' focos' + (row.unusual ? ' · acima do padrão' : '')}
                <button type="button" class="day" class:unusual={row.unusual} class:empty-cell={level === 0} class:light-cell={level >= 3} style:--day-color={calendarColors[level - 1]}
                  aria-pressed={day.date === row.date} aria-label={label} title={label} onclick={() => { selectedDate = row.date; }}>
                  <span>{Number(row.date.slice(-2))}{#if row.unusual}<span class="flag" aria-hidden="true">!</span>{/if}</span>
                  <small>{formatCount.format(row.detections)}</small>
                </button>
              {/each}
            </div>
            <div class="day-key">
              <span>Menos focos</span>
              <span class="day-ramp" aria-hidden="true">{#each calendarColors as color (color)}<i style:background={color}></i>{/each}</span>
              <span>{page.dayLegend}</span><span><b aria-hidden="true">!</b> Acima do padrão</span>
            </div>
          </section>
          {@render mapPanel()}
        </div>
        <section class="history" aria-labelledby="history-title">
          <div class="panel-header"><h3 id="history-title">{page.history}</h3><span>{formatCount.format(annualTotal)} focos no ano</span></div>
          {#if baselineYears.length}
            <div class="chart-key"><span class="observed">{activity.year} observado</span><span class="projected">{page.reference}</span></div>
            <p>Referência dos mesmos meses em {baselineYears.join(', ')}.</p>
            {#if monthSummary.anomaly != null}
              <p><strong>{signed.format(monthSummary.anomaly)} focos</strong> em {monthName(activeMonth)} frente à média de {formatMetric.format(monthSummary.baseline_average)}{monthSummary.anomaly_pct == null ? '' : ' (' + signed.format(monthSummary.anomaly_pct) + '%)'}.</p>
            {/if}
          {:else}
            <p>{page.historyUnavailable} {years.length === 1 ? 'Ano disponível neste recorte: ' + activity.year + '.' : ''}</p>
          {/if}
          <ActivityTrend data={historical} referenceLabel={baselineYears.length ? page.reference : undefined} title="Detecções mensais" wide />
        </section>
        <details class="method"><summary>Como a atividade é medida</summary><p>{page.method} {page.zero}</p><p>{page.detectionNote}</p></details>
      {:else}
        {@render mapPanel()}
        <p class="method">{page.seasonMethod}</p>
      {/if}
    </section>
    {#if !isCalendar}<p class="limitation">{copy.limitation}</p>{/if}
  {/if}
</section>

<style>
  .activity { display: grid; gap: 14px; padding: clamp(12px, 2.5vw, 32px); }
  header h1 { font: 700 clamp(2.5rem, 5vw, 4rem)/1 var(--heading); }
  h2 { display: flex; gap: 8px; align-items: center; font: 650 clamp(1.35rem, 2.5vw, 1.8rem)/1.05 var(--heading); }
  h3 { display: flex; gap: 7px; align-items: center; font: 650 1.45rem/1.1 var(--heading); }
  h2 :global(svg), h3 :global(svg) { color: var(--accent); flex: none; }
  p, .panel-header > span, .day-key, .area-status { color: var(--muted); font-size: .82rem; }
  header p { margin-top: 6px; }
  .panel, .filters { display: grid; align-content: start; gap: 10px; min-width: 0; padding: clamp(10px, 2vw, 20px); }
  .filters { border-color: var(--accent-border); }
  .filter-row, .panel-header, .chart-key { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: end; }
  .panel-header { justify-content: space-between; align-items: center; }
  .panel-heading { display: grid; gap: 4px; }
  label { display: grid; gap: 4px; min-width: 0; color: var(--muted); font-size: .75rem; }
  .check { display: flex; align-items: center; gap: 5px; min-height: 38px; }
  .check input { accent-color: var(--accent); }
  .coordinate { width: 7rem; }
  .activity-panel { gap: 16px; }
  .calendar-toolbar, .month-navigation, .critical-label, .draw-button, .area-status { display: flex; align-items: center; gap: 8px; }
  .calendar-toolbar, .area-status { flex-wrap: wrap; }
  .month-arrow { display: grid; place-items: center; width: 42px; min-height: 42px; border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--background); color: var(--text); cursor: pointer; }
  .month-arrow:hover:enabled { color: var(--accent); border-color: var(--accent); }
  .month-arrow:disabled { opacity: .45; cursor: default; }
  .month-select { min-height: 42px; min-width: 135px; text-transform: capitalize; }
  .critical-label { color: var(--heat); font-size: .8rem; font-weight: 650; }
  .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 7px; margin: 0; }
  .metrics > div { display: flex; flex-direction: column; gap: 5px; min-width: 0; padding: 9px 11px; border: 1px solid var(--border); border-radius: var(--control-radius); background: var(--background); }
  .metrics dt { color: var(--muted); font-size: .77rem; }
  .metrics dd { margin: auto 0 0; font: 650 clamp(1.45rem, 3vw, 2.35rem)/1 var(--heading); font-variant-numeric: tabular-nums; }
  .metrics .unavailable { color: var(--muted); }
  .calendar-results { display: grid; grid-template-columns: minmax(0, .95fr) minmax(0, 1.05fr); gap: 14px; }
  .day-panel, .map-panel, .history { display: grid; gap: 8px; min-width: 0; align-content: start; }
  .day-panel, .map-panel { padding: 10px; border: 1px solid var(--border); border-radius: var(--control-radius); }
  .map-panel h3::first-letter { text-transform: uppercase; }
  .map-panel :global(.fire-map) { border-radius: var(--control-radius); }
  .map-panel :global(.map-legend) { padding: 9px 0 0; border-top: 0; }
  .point-key { display: flex; align-items: center; gap: 7px; }
  .point-key span { width: 7px; height: 7px; border-radius: 50%; background: #fee838; border: 1px solid #101b19; }
  .draw-button { padding: 6px 9px; font-size: .75rem; }
  .draw-button[aria-pressed='true'] { background: var(--accent-surface); }
  .draw-hint { border-left: 2px solid var(--accent); padding-left: 8px; }
  .clear-area { padding: 4px 2px; border: 0; background: none; color: var(--accent); text-decoration: underline; font: inherit; cursor: pointer; }
  .day-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 4px; }
  .weekday, .chart-key, .day-key { color: var(--muted); font-size: .72rem; }
  .weekday { text-align: center; }
  .day { display: grid; align-content: center; gap: 2px; min-width: 0; min-height: 44px; padding: 4px 0; border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--day-color, var(--background)); color: #fff; font: inherit; font-size: .8rem; text-align: center; cursor: pointer; }
  .empty-cell { color: var(--text); }
  .light-cell { color: #101b19; }
  .day:hover, .day[aria-pressed='true'] { outline: 2px solid currentColor; outline-offset: -3px; }
  .day:focus-visible { outline: 2px solid currentColor; outline-offset: -3px; box-shadow: 0 0 0 2px var(--accent); }
  .day small { color: inherit; font-size: clamp(.58rem, 1.1vw, .73rem); font-variant-numeric: tabular-nums; }
  .unusual { border-style: dashed; border-color: currentColor; }
  .flag { margin-left: 2px; font-weight: 800; }
  .day-key { display: flex; flex-wrap: wrap; align-items: center; gap: 5px 8px; }
  .day-ramp { display: inline-grid; grid-template-columns: repeat(4, 15px); height: 8px; overflow: hidden; border-radius: 5px; }
  .day-key b { font-weight: 800; color: var(--text); }
  .history, .method { border-top: 1px solid var(--border); padding-top: 12px; }
  .method p { margin-top: 6px; }
  .chart-key > span { display: flex; gap: 5px; align-items: center; }
  .chart-key > span::before { content: ''; width: 16px; border-top: 3px solid var(--key, var(--accent)); }
  .chart-key .observed { --key: var(--heat); }
  .chart-key .projected::before { border-top-style: dashed; }
  .chart-key .range::before { border-top-width: 8px; opacity: .35; }
  summary { font-size: .82rem; cursor: pointer; }
  table { margin-top: 8px; width: 100%; border-collapse: collapse; font-size: .8rem; }
  th, td { padding: 5px; border-bottom: 1px solid var(--border); text-align: left; }
  .limitation { border-left: 2px solid var(--accent); padding-left: 10px; }
  @media (max-width: 1040px) { .calendar-results { grid-template-columns: 1fr; } }
  @media (max-width: 550px) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>

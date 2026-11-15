<script>
  import { geoMercator, geoPath } from 'd3-geo';
  import { feature } from 'topojson-client';
  import world from 'world-atlas/countries-110m.json';
  import EarthGlobe from './EarthGlobe.svelte';

  let { cells, rankings, countries = [] } = $props();
  const countryCodes = {
    '032': 'AR', '068': 'BO', '076': 'BR', '152': 'CL', '170': 'CO', '218': 'EC',
    '328': 'GY', '600': 'PY', '604': 'PE', '740': 'SR', '858': 'UY', '862': 'VE',
  };
  const names = new Intl.DisplayNames('pt-BR', { type: 'region' });
  const territory = feature(world, world.objects.countries).features.filter(item => Object.hasOwn(countryCodes, item.id));
  const projection = geoMercator().fitExtent([[12, 12], [388, 398]], { type: 'FeatureCollection', features: territory });
  const path = geoPath(projection);
  const shapes = territory.map(item => ({
    id: countryCodes[item.id],
    name: names.of(countryCodes[item.id]),
    source: item.properties.name,
    path: path(item),
  }));
  const number = new Intl.NumberFormat('pt-BR');
  const totals = $derived(new Map(countries.map(row => [row.country, row.detections])));
  const peak = $derived(Math.max(1, ...totals.values()));
  let activeCountry = $state(null);
  let metric = $state(1);
</script>

<div class="maps">
  <section class="region" aria-labelledby="south-america-title">
    <div class="heading">
      <h3 id="south-america-title">América do Sul</h3>
      <p>Selecione um país no mapa para ver o total no recorte.</p>
    </div>
    <svg class="country-map" viewBox="0 0 400 410" aria-label="Países sul-americanos monitorados" role="group">
      {#each shapes as shape (shape.id)}
        {@const count = totals.get(shape.source)}
        {@const strength = count ? Math.log1p(count) / Math.log1p(peak) : 0}
        <path d={shape.path} role="button" tabindex="0"
          aria-label={shape.name + (count ? ' · ' + number.format(count) + ' detecções' : ' · sem detecções no recorte')}
          aria-pressed={activeCountry === shape.id}
          class:active={activeCountry === shape.id}
          style:--strength={Math.round(strength * 78) + '%'}
          onclick={() => { activeCountry = shape.id; }}
          onkeydown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault();
              activeCountry = shape.id;
            }
          }}>
          <title>{shape.name}</title>
        </path>
      {/each}
    </svg>
    <p class="details" aria-live="polite">
      {#if activeCountry}
        {@const region = shapes.find(shape => shape.id === activeCountry)}
        {@const count = totals.get(region.source)}
        <strong>{region.name}</strong> · {count ? number.format(count) + ' detecções' : 'Sem detecções no recorte'}
      {:else}
        Países coloridos têm detecções no recorte atual.
      {/if}
    </p>
  </section>

  <section class="planet" aria-labelledby="globe-title">
    <div class="heading">
      <div><h3 id="globe-title">Globo de focos · 3D</h3><p>As colunas mais altas indicam valores maiores. Arraste para girar e aproxime com a roda ou a pinça.</p></div>
      <label>Medida das colunas
        <select class="data-control" bind:value={metric}>
          <option value={1}>Detecções</option><option value={2}>FRP acumulada</option>
        </select>
      </label>
    </div>
    <EarthGlobe {cells} {metric} strongest={rankings?.[metric === 1 ? 'detections' : 'frp_mw'] ?? []} />
    <p class="details">
      <span>{number.format(cells.length)} células de 0,25° com detecções</span>
      <a href="https://svs.gsfc.nasa.gov/3615">Blue Marble · NASA/GSFC SVS</a>
    </p>
  </section>
</div>

<style>
  .maps { display: grid; grid-template-columns: minmax(240px, 1fr) minmax(0, 1.35fr); padding: 0 12px 6px; gap: 12px; align-items: stretch; }
  .region, .planet { min-width: 0; overflow: hidden; border: 1px solid var(--border); border-radius: var(--control-radius); background: var(--background); }
  .heading { display: flex; flex-wrap: wrap; align-items: end; justify-content: space-between; gap: 7px 12px; padding: 12px 13px 5px; }
  .heading h3 { margin: 0; font-size: .92rem; }
  .heading p { margin-top: 4px; color: var(--muted); font-size: .75rem; }
  .heading label { display: grid; gap: 4px; color: var(--muted); font-size: .7rem; }
  .country-map { display: block; width: 100%; height: clamp(265px, 31vw, 390px); background: radial-gradient(ellipse, var(--accent-surface), transparent 73%); }
  .country-map path { fill: color-mix(in srgb, var(--accent) var(--strength), var(--surface-raised)); stroke: var(--background); stroke-width: 1.15; cursor: pointer; }
  .country-map path:hover, .country-map path:focus-visible, .country-map path.active { stroke: var(--heat); stroke-width: 2; outline: none; }
  .details { display: flex; flex-wrap: wrap; gap: 4px 10px; padding: 8px 13px 12px; color: var(--muted); font-size: .72rem; }
  .details strong { color: var(--text); }
  .details a { text-decoration: underline; text-underline-offset: 3px; }
  @media (max-width: 760px) { .maps { grid-template-columns: minmax(0, 1fr); } }
</style>

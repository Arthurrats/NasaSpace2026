<script>
  import { Activity, ArrowDown, ArrowRight, Box, Flame, Globe, MapPin, Trees, Wind } from '@lucide/svelte';
  import ActivityTrend from '../features/fire-monitoring/components/ActivityTrend.svelte';
  import MapPreview from '../features/fire-monitoring/components/MapPreview.svelte';
  import RegionalDepth from '../features/fire-monitoring/components/RegionalDepth.svelte';
  import { regions } from '../features/fire-monitoring/data/demo.js';
  import BrandLockup from '../layouts/BrandLockup.svelte';

  const impacts = [
    { icon: Wind, title: 'Fumaça e saúde', detail: 'A fumaça das queimadas pode viajar longas distâncias, piorar a qualidade do ar e afetar a saúde de quem respira esse ar.' },
    { icon: Trees, title: 'Perda de vegetação', detail: 'Incêndios florestais degradam a vegetação e alteram habitats, com consequências para a biodiversidade.' },
    { icon: Flame, title: 'Focos espalhados no território', detail: 'Comparar onde e quando os focos aparecem ajuda a entender sua distribuição. Um mesmo incêndio pode gerar várias detecções por satélite.' },
  ];

  const team = [
    { initials: 'AR', name: 'Arthur Rats' },
    { initials: 'RR', name: 'RaphaelRates' },
    { initials: 'GP', name: 'Guilherme Pinheiro' },
    { initials: 'VH', name: 'Victor Hugo' },
    { initials: 'JS', name: 'José Sergio' },
  ];
</script>

<section id="solucao" class="hero page-section" aria-labelledby="hero-title" tabindex="-1">
  <div class="hero-copy">
    <div class="hero-brand"><BrandLockup /></div>
    <h1 id="hero-title">Queimadas <em>em análise.</em></h1>
    <p>A prevIA reúne focos de calor em um mapa-múndi e mostra como eles se distribuem entre regiões e ao longo do tempo.</p>
    <div class="hero-actions">
      <a href="#/painel" class="button button-primary">Explorar painel <ArrowRight size={18} aria-hidden="true" /></a>
      <a href="#recursos" class="section-link">Ver recursos <ArrowDown size={16} aria-hidden="true" /></a>
    </div>
  </div>

  <MapPreview />
</section>

<section id="problema" class="problem page-section" aria-labelledby="problem-title" tabindex="-1">
  <div class="section-heading">
    <p class="eyebrow">O PROBLEMA</p>
    <h2 id="problem-title">Os impactos das queimadas.</h2>
  </div>
  <div class="impact-grid">
    {#each impacts as { icon: Icon, title, detail }}
      <article class="impact">
        <Icon size={23} aria-hidden="true" />
        <h3>{title}</h3>
        <p>{detail}</p>
      </article>
    {/each}
  </div>
  <p class="references">
    <a href="https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/vigilancia-ambiental/queimadas-e-incencios-florestais-2a-edicao.pdf">Ministério da Saúde</a>
    <span aria-hidden="true">·</span>
    <a href="https://www.gov.br/ibama/pt-br/servicos/consultas/incendios-florestais/monitoramento-de-focos-de-queimadas-em-imagens-de-satelites">Ibama</a>
  </p>
</section>

<section id="recursos" class="features page-section" aria-labelledby="features-title" tabindex="-1">
  <div class="section-heading features-heading">
    <div>
      <p class="eyebrow">RECURSOS</p>
      <h2 id="features-title">O que você pode analisar.</h2>
    </div>
    <a href="#/painel" class="button button-outline">Abrir painel <ArrowRight size={17} aria-hidden="true" /></a>
  </div>

  <div class="feature-grid">
    <article class="card feature">
      <div class="feature-copy">
        <h3><Globe size={20} aria-hidden="true" /> Mapa com filtro regional</h3>
        <p>Explore a distribuição dos focos por intensidade e alterne entre a visão mundial e os recortes do painel.</p>
      </div>
      <ul class="region-list" aria-label="Recortes disponíveis no painel">
        {#each Object.values(regions) as { name }}
          <li><MapPin size={14} aria-hidden="true" /> {name}</li>
        {/each}
      </ul>
    </article>
    <article class="card feature">
      <div class="feature-copy">
        <h3><Activity size={20} aria-hidden="true" /> Evolução diária</h3>
        <p>Acompanhe a quantidade de focos por dia e identifique picos na semana de exemplo.</p>
      </div>
      <div class="feature-chart"><ActivityTrend /></div>
    </article>
    <article class="card feature">
      <div class="feature-copy">
        <h3><Box size={20} aria-hidden="true" /> Comparativo entre regiões</h3>
        <p>Compare os totais de cada região no ranking e explore as diferenças no gráfico 3D.</p>
      </div>
      <div class="feature-chart"><RegionalDepth /></div>
    </article>
  </div>
</section>

<section id="equipe" class="team page-section" aria-labelledby="team-title" tabindex="-1">
  <div class="section-heading">
    <p class="eyebrow">EQUIPE</p>
    <h2 id="team-title">Quem desenvolve a prevIA.</h2>
    <p class="team-description">Programação, matemática aplicada e análise de dados.</p>
  </div>
  <ul class="team-list" aria-label="Equipe de desenvolvimento">
    {#each team as { initials, name } (name)}
      <li><span class="initials" aria-hidden="true">{initials}</span><strong>{name}</strong></li>
    {/each}
  </ul>
</section>

<style>
  .page-section { padding: clamp(42px, 6vw, 90px) var(--page-inset); }
  .page-section:focus { outline: none; }

  .hero {
    display: grid;
    grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr);
    align-items: center;
    gap: clamp(24px, 4.5vw, 72px);
    background: radial-gradient(ellipse at 88% 40%, var(--surface), var(--background) 67%);
  }

  .hero-copy { min-width: 0; }
  .hero-brand { --brand-size: clamp(1.8rem, 3vw, 2.65rem); display: flex; margin-left: -.24em; }
  .hero h1, .section-heading h2 {
    font-family: var(--heading);
    font-weight: 700;
    letter-spacing: -.018em;
  }

  .hero h1 { margin-block: 15px 22px; font-size: clamp(3.15rem, 7vw, 7.7rem); line-height: .9; }
  .hero h1 em { display: block; color: var(--accent); font-style: normal; }
  .hero-copy > p { max-width: 38ch; color: var(--muted); font-size: clamp(.95rem, 1.35vw, 1.125rem); line-height: 1.65; }
  .hero-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 16px 22px; margin-top: 28px; }
  .section-link { display: inline-flex; align-items: center; gap: 7px; min-height: 44px; color: var(--indicator); font-size: .88rem; font-weight: 650; }
  .section-link:hover { text-decoration: underline; }

  .problem, .team {
    border-block: 1px solid var(--border);
    background: var(--surface);
  }

  .section-heading { margin-bottom: clamp(22px, 3vw, 36px); }
  .section-heading h2 { margin-top: 8px; font-size: clamp(2.55rem, 4.8vw, 5rem); line-height: .98; }

  .impact-grid, .feature-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .impact-grid { border-block: 1px solid var(--border-strong); }
  .impact { padding: 24px clamp(16px, 3vw, 42px); }
  .impact:first-child { padding-left: 0; }
  .impact + .impact { border-left: 1px solid var(--border-strong); }
  .impact > :global(svg) { color: var(--heat); }
  .impact h3, .feature h3 { margin: 12px 0 7px; font-size: 1rem; font-weight: 700; }
  .impact p, .feature p, .team-description { color: var(--muted); font-size: .9rem; line-height: 1.6; }
  .impact p { max-width: 38ch; }

  .references { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 14px; color: var(--muted); font-size: .75rem; }
  .references a { text-decoration: underline; text-underline-offset: 3px; }
  .references a:hover { color: var(--text); }

  .features-heading { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 16px; }
  .feature-grid { gap: 16px; }
  .feature { display: flex; flex-direction: column; padding: 18px 0; }
  .feature-copy { padding-inline: 18px; }
  .feature h3 { display: flex; align-items: center; gap: 8px; margin-top: 0; }
  .feature h3 :global(svg), .region-list :global(svg) { color: var(--indicator); }
  .feature-chart { margin-top: auto; padding-top: 24px; }

  .region-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 18px;
    padding: 0;
    list-style: none;
  }

  .region-list li {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 7px 9px;
    border: 1px solid var(--border);
    border-radius: var(--control-radius);
    background: var(--background);
    font-size: .75rem;
    line-height: 1.35;
  }

  .team-description { margin-top: 10px; }
  .team-list {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .team-list li {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 16px;
    border: 1px solid var(--border);
    border-radius: var(--card-radius);
    background: var(--background);
    font-size: .95rem;
    overflow-wrap: anywhere;
  }

  .initials {
    display: grid;
    place-items: center;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: var(--surface);
    color: var(--indicator);
    font-size: .78rem;
    font-weight: 700;
  }

  @media (max-width: 1050px) {
    .team-list { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  }

  @media (max-width: 860px) {
    .hero { grid-template-columns: minmax(0, 1fr); }
    .hero h1 { font-size: clamp(3.15rem, 11vw, 6.1rem); }
    .feature-grid { grid-template-columns: minmax(0, 1fr); }
    .feature-chart { width: min(100%, 480px); }
  }

  @media (max-width: 650px) {
    .impact-grid { grid-template-columns: minmax(0, 1fr); }
    .impact { padding: 18px 0; }
    .impact + .impact { border-top: 1px solid var(--border-strong); border-left: 0; }
    .impact p { max-width: 50ch; }
    .team-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
</style>

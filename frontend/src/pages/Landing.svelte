<script>
  import { Activity, ArrowDown, Box, Globe, MapPin } from '@lucide/svelte';
  import ActivityTrend from '../features/fire-monitoring/components/ActivityTrend.svelte';
  import MapPreview from '../features/fire-monitoring/components/MapPreview.svelte';
  import RegionalDepth from '../features/fire-monitoring/components/RegionalDepth.svelte';
  import { countries } from '../features/fire-monitoring/data/demo.js';
  import BrandLockup from '../layouts/BrandLockup.svelte';
  import TeamPhoto from './landing/TeamPhoto.svelte';

  import { groupPhoto, impacts, landingCopy as copy, team } from '../content/landing.js';
</script>

<section id="solucao" class="hero page-section" aria-labelledby="hero-title" tabindex="-1">
  <div class="hero-copy">
    <div class="hero-brand"><BrandLockup /></div>
    <h1 id="hero-title">{copy.heroTitle} <em>{copy.heroHighlight}</em></h1>
    <p>{copy.heroDescription}</p>
    <div class="hero-actions">
      <a href="#recursos" class="button button-primary">{copy.heroAction} <ArrowDown size={17} aria-hidden="true" /></a>
    </div>
  </div>

  <MapPreview />
</section>

<section id="problema" class="problem page-section" aria-labelledby="problem-title" tabindex="-1">
  <div class="section-heading">
    <p class="eyebrow">{copy.problemLabel}</p>
    <h2 id="problem-title">{copy.problemTitle}</h2>
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
    <a href="https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/vigilancia-ambiental/queimadas-e-incencios-florestais-2a-edicao.pdf">{copy.healthSource}</a>
    <span aria-hidden="true">·</span>
    <a href="https://www.gov.br/ibama/pt-br/servicos/consultas/incendios-florestais/monitoramento-de-focos-de-queimadas-em-imagens-de-satelites">{copy.ibamaSource}</a>
  </p>
</section>

<section id="recursos" class="features page-section" aria-labelledby="features-title" tabindex="-1">
  <div class="section-heading">
    <p class="eyebrow">{copy.featuresLabel}</p>
    <h2 id="features-title">{copy.featuresTitle}</h2>
  </div>

  <div class="feature-grid">
    <article class="card feature">
      <div class="feature-copy">
        <h3><Globe size={20} aria-hidden="true" /> {copy.filterTitle}</h3>
        <p>{copy.filterDescription}</p>
      </div>
      <ul class="region-list" aria-label={copy.countryList}>
        {#each Object.values(countries) as { name }}
          <li><MapPin size={14} aria-hidden="true" /> {name}</li>
        {/each}
      </ul>
    </article>
    <article class="card feature">
      <div class="feature-copy">
        <h3><Activity size={20} aria-hidden="true" /> {copy.trendTitle}</h3>
        <p>{copy.trendDescription}</p>
      </div>
      <div class="feature-chart"><ActivityTrend /></div>
    </article>
    <article class="card feature">
      <div class="feature-copy">
        <h3><Box size={20} aria-hidden="true" /> {copy.compareTitle}</h3>
        <p>{copy.compareDescription}</p>
      </div>
      <div class="feature-chart"><RegionalDepth /></div>
    </article>
  </div>
</section>

<section id="equipe" class="team page-section" aria-labelledby="team-title" tabindex="-1">
  <div class="section-heading">
    <p class="eyebrow">{copy.teamLabel}</p>
    <h2 id="team-title">{copy.teamTitle}</h2>
    <p class="team-description">{copy.teamDescription}</p>
  </div>
  <TeamPhoto src={groupPhoto} group />
  <ul class="team-list" aria-label={copy.teamList}>
    {#each team as { initials, name, photo } (name)}
      <li><TeamPhoto src={photo} {name} {initials} /><strong>{name}</strong></li>
    {/each}
  </ul>
</section>

<style>
  .page-section {
    display: grid;
    align-content: center;
    min-block-size: min(76svh, 820px);
    padding: clamp(42px, 6vw, 90px) var(--page-inset);
  }
  .page-section:focus { outline: none; }

  .hero {
    display: grid;
    grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr);
    min-block-size: calc(100svh - var(--header-height));
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
  .hero-actions { margin-top: 28px; }

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

  .feature-grid { gap: 16px; }
  .feature { display: flex; flex-direction: column; padding: 18px 0; background: var(--accent-surface); border-color: var(--accent-border); }
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
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: var(--card-radius);
    background: var(--background);
    font-size: .95rem;
    overflow-wrap: anywhere;
  }

  .team-list strong { display: block; padding: 12px; }

  @keyframes enter-section {
    from { opacity: .68; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @supports (animation-timeline: view()) {
    @media (prefers-reduced-motion: no-preference) {
      .section-heading, .impact, .feature, .team-list li {
        animation: enter-section linear both;
        animation-timeline: view();
        animation-range: entry 0% cover 30%;
      }

      .hero :global(.analysis-map) {
        animation: map-scroll linear both;
        animation-timeline: view();
        animation-range: exit 0% exit 100%;
      }
    }
  }

  @keyframes map-scroll {
    from { transform: translateY(0); }
    to { transform: translateY(22px); }
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

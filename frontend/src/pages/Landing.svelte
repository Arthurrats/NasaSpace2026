<script>
  import { onMount, tick } from 'svelte';
  import { Activity, ArrowDown, ArrowRight, ArrowUpRight, CalendarDays, ChevronDown, Globe2, Satellite } from '@lucide/svelte';
  import ActivityTrend from '../features/fire-monitoring/components/ActivityTrend.svelte';
  import MapPreview from '../features/fire-monitoring/components/MapPreview.svelte';
  import RegionalDepth from '../features/fire-monitoring/components/RegionalDepth.svelte';
  import { dailyActivity, regionalActivity } from '../features/fire-monitoring/data/demo.js';
  import BrandLockup from '../layouts/BrandLockup.svelte';
  import TeamPhoto from './landing/TeamPhoto.svelte';
  import { coverage, faq, groupPhoto, impacts, landingCopy as copy, landingDemoCopy as demo, landingDemos, team, useCases, workflow } from '../content/landing.js';

  let { onSectionChange } = $props();
  let landing = $state();
  let currentSection = $state('');
  let visible = $state(true);
  const motionSection = $derived(visible ? currentSection : '');
  const heroImage = import.meta.env.BASE_URL + 'previa-orbita.webp';

  const demoIcons = { trend: Activity, calendar: CalendarDays, regions: Globe2 };
  const demoKeys = Object.keys(landingDemos);
  let activeDemo = $state('trend');
  let period = $state(14);
  let selectedDay = $state(0);
  let selectedRegion = $state(regionalActivity[0].label);
  const sampleDays = dailyActivity.slice(0, 30).map((row, index) => ({
    value: row.value, label: String(index + 1), detail: demo.day + ' ' + (index + 1),
  }));
  const samplePeak = Math.max(...sampleDays.map(row => row.value));
  const visibleDays = $derived(sampleDays.slice(-period));
  const regionValue = $derived(regionalActivity.find(row => row.label === selectedRegion)?.value ?? 0);
  const comparison = $derived(regionalActivity.map(row => ({ ...row, emphasized: row.label === selectedRegion })));
  const format = new Intl.NumberFormat('pt-BR');

  function moveTab(event) {
    const index = demoKeys.indexOf(activeDemo);
    const destinations = {
      ArrowRight: (index + 1) % demoKeys.length, ArrowDown: (index + 1) % demoKeys.length,
      ArrowLeft: (index + demoKeys.length - 1) % demoKeys.length, ArrowUp: (index + demoKeys.length - 1) % demoKeys.length,
      Home: 0, End: demoKeys.length - 1,
    };
    if (!Object.hasOwn(destinations, event.key)) return;
    event.preventDefault();
    activeDemo = demoKeys[destinations[event.key]];
    tick().then(() => landing?.querySelector('#demo-tab-' + activeDemo)?.focus());
  }

  onMount(() => {
    const sections = [...landing.querySelectorAll(':scope > section[id]')];
    const footer = document.getElementById('contato');
    if (footer) sections.push(footer);
    let observer;

    function activateSection() {
      const headerBottom = document.querySelector('.site-layout > header')?.getBoundingClientRect().bottom ?? 0;
      const center = (window.innerHeight + headerBottom) / 2;
      const current = sections.find(element => {
        const rect = element.getBoundingClientRect();
        return rect.top <= center && rect.bottom > center;
      }) ?? (footer && footer.getBoundingClientRect().top < window.innerHeight ? footer : null);
      const id = current?.id ?? '';
      if (id === currentSection) return;
      currentSection = id;
      onSectionChange?.(id);
    }

    function observe() {
      observer?.disconnect();
      const center = (window.innerHeight + (document.querySelector('.site-layout > header')?.offsetHeight ?? 0)) / 2;
      // A narrow band at the center of the visible page keeps one section active.
      observer = new IntersectionObserver(activateSection, { rootMargin: `-${Math.floor(center - 1)}px 0px -${Math.floor(window.innerHeight - center - 1)}px 0px` });
      sections.forEach(section => observer.observe(section));
      activateSection();
    }

    function checkVisibility() {
      visible = document.visibilityState === 'visible';
    }

    observe();
    checkVisibility();
    window.addEventListener('resize', observe);
    document.addEventListener('visibilitychange', checkVisibility);
    return () => {
      observer?.disconnect();
      window.removeEventListener('resize', observe);
      document.removeEventListener('visibilitychange', checkVisibility);
      onSectionChange?.('');
    };
  });
</script>

<div class="landing" bind:this={landing}>
  <section id="solucao" class="hero page-section" class:current={motionSection === 'solucao'} aria-labelledby="hero-title" tabindex="-1">
    <img class="hero-image" src={heroImage} width="1672" height="941" alt="" fetchpriority="high" />
    <div class="container hero-layout">
      <div class="hero-copy reveal">
        <div class="hero-brand"><BrandLockup /></div>
        <p class="hero-context"><Satellite size={18} aria-hidden="true" />{copy.heroContext}</p>
        <h1 id="hero-title">{copy.heroTitle} <em>{copy.heroHighlight}</em></h1>
        <p class="hero-description">{copy.heroDescription}</p>
        <div class="actions">
          <a href="#recursos" class="button hero-primary">{copy.heroAction}<ArrowDown size={17} aria-hidden="true" /></a>
          <a href="#dados" class="hero-secondary">{copy.heroSecondaryAction}<ArrowUpRight size={16} aria-hidden="true" /></a>
        </div>
      </div>
      <div class="hero-map">
        <MapPreview active={motionSection === 'solucao'} />
      </div>
    </div>
  </section>

  <section id="problema" class="problem page-section" class:current={motionSection === 'problema'} aria-labelledby="problem-title" tabindex="-1">
    <div class="container">
      <div class="section-heading reveal">
        <h2 id="problem-title">{copy.problemTitle}</h2>
      </div>
      <ul class="story-grid">
        {#each impacts as { icon: Icon, title, detail } (title)}
          <li class="story"><span class="story-icon warm"><Icon size={22} aria-hidden="true" /></span><h3>{title}</h3><p>{detail}</p></li>
        {/each}
      </ul>
      <div class="references">
        <a href="https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/vigilancia-ambiental/queimadas-e-incencios-florestais-2a-edicao.pdf">{copy.healthSource}<ArrowUpRight size={13} aria-hidden="true" /></a>
        <a href="https://www.gov.br/ibama/pt-br/servicos/consultas/incendios-florestais/monitoramento-de-focos-de-queimadas-em-imagens-de-satelites">{copy.ibamaSource}<ArrowUpRight size={13} aria-hidden="true" /></a>
      </div>
    </div>
  </section>

  <section id="recursos" class="resources page-section" class:current={motionSection === 'recursos'} aria-labelledby="resources-title" tabindex="-1">
    <div class="container">
      <div class="section-heading reveal"><h2 id="resources-title">{copy.featuresTitle}</h2></div>
      <div class="demo-layout">
        <div class="demo-tabs" role="tablist" aria-label={demo.help}>
          {#each demoKeys as key (key)}
            {@const Icon = demoIcons[key]}
            <button type="button" role="tab" id="demo-tab-{key}" aria-controls="demo-panel-{key}" aria-selected={activeDemo === key}
              tabindex={activeDemo === key ? 0 : -1} onclick={() => { activeDemo = key; }} onkeydown={moveTab}>
              <span class="story-icon"><Icon size={20} aria-hidden="true" /></span>
              <span>{landingDemos[key].title}</span><ArrowRight size={17} class="tab-arrow" aria-hidden="true" />
            </button>
          {/each}
        </div>
        <div class="card demo-stage">
          {#each demoKeys as key (key)}
            <div class="demo-panel" id="demo-panel-{key}" role="tabpanel" aria-labelledby="demo-tab-{key}" tabindex="0" hidden={activeDemo !== key}>
              {#if activeDemo === key}
                <div class="demo-content">
                  <div class="demo-header">
                    <h3>{landingDemos[key].title}</h3>
                    <span class="sample-label">{demo.sample}</span>
                  </div>
                  <p>{landingDemos[key].detail}</p>
                  {#if key === 'trend'}
                    <div class="range-control" role="group" aria-label={demo.range}>
                      {#each [14, 30] as range (range)}
                        <button type="button" aria-pressed={period === range} onclick={() => { period = range; }}>{range} {demo.days}</button>
                      {/each}
                    </div>
                    <ActivityTrend data={visibleDays} title={landingDemos.trend.title} wide />
                  {:else if key === 'calendar'}
                    <div class="sample-calendar" role="group" aria-label={landingDemos.calendar.title}>
                      {#each sampleDays as day, index (day.label)}
                        <button type="button" aria-pressed={selectedDay === index} style:--level={Math.round(day.value / samplePeak * 43) + '%'}
                          aria-label={day.detail + ', ' + format.format(day.value) + ' ' + demo.detections} onclick={() => { selectedDay = index; }}>{day.label}</button>
                      {/each}
                    </div>
                    <p class="readout" aria-live="polite"><strong>{sampleDays[selectedDay].detail}</strong> · {format.format(sampleDays[selectedDay].value)} {demo.detections}</p>
                  {:else}
                    <label class="region-control">
                      <span>{demo.country}</span>
                      <select class="data-control" bind:value={selectedRegion}>
                        {#each regionalActivity as row (row.label)}<option value={row.label}>{row.label}</option>{/each}
                      </select>
                    </label>
                    <div class="region-chart"><RegionalDepth data={comparison} title={landingDemos.regions.title + ' · ' + demo.sample} /></div>
                    <p class="readout" aria-live="polite"><strong>{selectedRegion}</strong> · {format.format(regionValue)} {demo.detections}</p>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    </div>
  </section>

  <section id="dados" class="data-section page-section" class:current={motionSection === 'dados'} aria-labelledby="data-title" tabindex="-1">
    <div class="container">
      <div class="section-heading reveal"><h2 id="data-title">{copy.coverageTitle}</h2><p>{copy.coverageDescription}</p></div>
      <dl class="coverage">
        {#each coverage as item (item.label)}
          <div><dt>{item.label}</dt><dd class="coverage-value">{item.value}</dd><dd class="coverage-detail">{item.detail}</dd></div>
        {/each}
      </dl>
      <div class="workflow">
        <div class="workflow-intro"><h3>{copy.workflowTitle}</h3><p>{copy.workflowDescription}</p></div>
        <ol>
          {#each workflow as { icon: Icon, title, detail } (title)}
            <li><span class="story-icon"><Icon size={20} aria-hidden="true" /></span><div><h4>{title}</h4><p>{detail}</p></div></li>
          {/each}
        </ol>
      </div>
    </div>
  </section>

  <section id="uso" class="uses page-section" class:current={motionSection === 'uso'} aria-labelledby="uses-title" tabindex="-1">
    <div class="container">
      <div class="section-heading reveal"><h2 id="uses-title">{copy.useCasesTitle}</h2><p>{copy.useCasesDescription}</p></div>
      <ul class="story-grid">
        {#each useCases as { icon: Icon, title, detail } (title)}
          <li class="story"><span class="story-icon"><Icon size={22} aria-hidden="true" /></span><h3>{title}</h3><p>{detail}</p></li>
        {/each}
      </ul>
    </div>
  </section>

  <section id="equipe" class="team page-section" class:current={motionSection === 'equipe'} aria-labelledby="team-title" tabindex="-1">
    <div class="container">
      <div class="team-heading">
        <div class="section-heading reveal"><h2 id="team-title">{copy.teamTitle}</h2><p>{copy.teamDescription}</p></div>
        <TeamPhoto src={groupPhoto} group />
      </div>
      <ul class="team-list" aria-label={copy.teamList}>
        {#each team as { initials, name, photo } (name)}
          <li><TeamPhoto src={photo} {name} {initials} /><strong>{name}</strong></li>
        {/each}
      </ul>
    </div>
  </section>

  <section id="perguntas" class="faq-section page-section" class:current={motionSection === 'perguntas'} aria-labelledby="faq-title" tabindex="-1">
    <div class="container faq-layout">
      <div class="section-heading reveal"><h2 id="faq-title">{copy.faqTitle}</h2></div>
      <div class="faq-list">
        {#each faq as { question, answer } (question)}
          <details name="previa-faq">
            <summary>{question}<ChevronDown size={19} aria-hidden="true" /></summary>
            <p>{answer}</p>
          </details>
        {/each}
      </div>
      <div class="closing">
        <div><h3>{copy.closingTitle}</h3><p>{copy.closingDescription}</p></div>
        <a href="#/login" class="button button-primary">{copy.closingAction}<ArrowRight size={18} aria-hidden="true" /></a>
      </div>
    </div>
  </section>
</div>

<style>
  .landing { overflow: clip; }
  .page-section { position: relative; padding: clamp(58px, 8.5vw, 140px) var(--page-inset); }
  .page-section:focus { outline: none; }
  .container { width: 100%; max-width: 1400px; margin-inline: auto; }
  .hero {
    display: grid;
    align-items: center;
    min-height: max(630px, calc(100svh - var(--header-height)));
    isolation: isolate;
    padding-block: clamp(46px, 6vw, 96px);
    background: #101b19;
    color: #f2f5f0;
    --background: #101b19;
    --surface: #1d302a;
    --text: #f2f5f0;
    --muted: #bbc9bf;
    --accent: #b6e36b;
    --indicator: #b6e36b;
  }
  .hero-image, .hero::before { position: absolute; z-index: -1; inset: 0; width: 100%; height: 100%; }
  .hero-image { object-fit: cover; object-position: 66% center; }
  .hero::before { content: ''; z-index: 0; pointer-events: none; background: linear-gradient(90deg, #071511c7 5%, #0a1b1162 56%, #0c1a1245), linear-gradient(0deg, #101b19 0%, #101b1900 32%); }
  .hero-layout { position: relative; display: grid; grid-template-columns: minmax(0, .91fr) minmax(0, 1.09fr); align-items: center; gap: clamp(24px, 5vw, 82px); }
  .hero-copy, .hero-map { min-width: 0; }
  .hero-brand { --brand-size: clamp(1.9rem, 3vw, 2.8rem); margin: 0 0 26px -.24em; }
  .hero-context { display: flex; align-items: center; gap: 8px; color: #d6e6da; font-size: .82rem; font-weight: 600; }
  .hero-context :global(svg) { color: var(--accent); }
  h1, h2, .workflow h3, .closing h3 { font-family: var(--heading); font-weight: 700; }
  .hero h1 { margin-block: 12px 18px; font-size: clamp(4rem, 7.6vw, 8.2rem); line-height: .84; letter-spacing: -.03em; text-wrap: balance; }
  .hero h1 em { display: block; color: var(--accent); font-style: normal; }
  .hero-description { max-width: 44ch; color: var(--muted); font-size: clamp(.94rem, 1.45vw, 1.14rem); line-height: 1.63; }
  .actions { display: flex; align-items: center; flex-wrap: wrap; gap: 14px 19px; margin-top: 24px; }
  .hero-primary { gap: 8px; border-color: #b6e36b; background: #b6e36b; color: #101b19; }
  .hero-primary:hover { border-color: #d2f29b; background: #d2f29b; }
  .hero-secondary { display: inline-flex; align-items: center; gap: 6px; padding-block: 10px; color: #edf4ef; font-size: .87rem; font-weight: 650; }
  .hero-secondary:hover { color: #b6e36b; }
  .section-heading { max-width: 760px; margin-bottom: clamp(20px, 3vw, 38px); }
  .section-heading h2 { font-size: clamp(2.9rem, 5.8vw, 6rem); line-height: .91; letter-spacing: -.02em; text-wrap: balance; }
  .section-heading p, .story p, .demo-content > p, .workflow p, .coverage-detail, .faq-list p, .closing p { color: var(--muted); line-height: 1.65; font-size: .92rem; }
  .section-heading p { max-width: 56ch; margin-top: 13px; font-size: 1rem; }
  .problem, .team { border-block: 1px solid var(--border); background: var(--surface); }
  .story-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 0; padding: 0; border-block: 1px solid var(--border-strong); list-style: none; }
  .story { padding: clamp(18px, 3vw, 38px); }
  .story:first-child { padding-left: 0; }
  .story + .story { border-left: 1px solid var(--border-strong); }
  .story h3, .demo-content h3 { margin: 12px 0 6px; font-size: 1.13rem; font-weight: 730; }
  .story-icon { display: inline-grid; flex: none; place-items: center; width: 42px; height: 42px; border: 1px solid var(--accent-border); border-radius: var(--control-radius); background: var(--accent-surface); color: var(--indicator); }
  .story-icon.warm { color: var(--heat); border-color: color-mix(in srgb, var(--heat), var(--border) 70%); background: color-mix(in srgb, var(--heat) 8%, var(--background)); }
  .references { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px; }
  .references a { display: inline-flex; align-items: center; gap: 5px; color: var(--muted); font-size: .78rem; }
  .references a:hover { color: var(--text); text-decoration: underline; }

  .demo-layout { display: grid; grid-template-columns: minmax(220px, .65fr) minmax(0, 1.8fr); gap: clamp(13px, 3vw, 36px); }
  .demo-tabs { display: grid; align-content: start; gap: 7px; }
  .demo-tabs button { display: flex; align-items: center; gap: 12px; min-width: 0; min-height: 62px; padding: 8px 11px; text-align: left; border: 1px solid var(--border); border-radius: var(--control-radius); background: var(--background); color: var(--muted); font-size: .91rem; font-weight: 650; }
  .demo-tabs button:hover, .demo-tabs button[aria-selected="true"] { border-color: var(--accent-border); background: var(--accent-surface); color: var(--text); }
  .demo-tabs button :global(.tab-arrow) { margin-left: auto; color: var(--accent); }
  .demo-stage { min-width: 0; min-height: 370px; border-color: var(--accent-border); background: var(--surface); overflow: hidden; }
  .demo-content { min-width: 0; padding: clamp(13px, 2.4vw, 32px); }
  .demo-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 5px 12px; }
  .demo-header h3 { margin: 0; }
  .demo-content > p { margin-block: 5px 14px; }
  .sample-label { color: var(--muted); font-size: .72rem; }
  .range-control { display: flex; gap: 6px; margin-bottom: 6px; }
  .range-control button, .sample-calendar button { min-height: 38px; padding: 5px 11px; border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--background); color: var(--text); font-size: .8rem; }
  .range-control button[aria-pressed="true"], .sample-calendar button[aria-pressed="true"] { outline: 2px solid var(--indicator); outline-offset: -2px; }
  .range-control button[aria-pressed="true"] { background: var(--accent-surface); }
  .sample-calendar { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 5px; max-width: 550px; }
  .sample-calendar button { padding-inline: 2px; background: color-mix(in srgb, var(--accent) var(--level), var(--background)); color: var(--text); }
  .sample-calendar button:hover, .range-control button:hover { border-color: var(--accent); }
  .readout strong { color: var(--text); }
  .region-control { display: flex; align-items: center; gap: 9px; color: var(--muted); font-size: .8rem; }
  .region-chart { max-width: 580px; margin-inline: auto; }

  .data-section { border-block: 1px solid var(--border); background: linear-gradient(120deg, var(--surface), var(--background) 82%); }
  .coverage { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 0; border: 1px solid var(--accent-border); border-radius: var(--card-radius); background: var(--accent-surface); }
  .coverage div { display: flex; flex-direction: column; gap: 4px; padding: clamp(16px, 3vw, 38px); }
  .coverage div + div { border-left: 1px solid var(--border); }
  .coverage dt { font-size: .92rem; font-weight: 700; }
  .coverage dd { margin: 0; }
  .coverage-value { order: -1; color: var(--indicator); font: 700 clamp(3rem, 7vw, 6.9rem)/.9 var(--heading); font-variant-numeric: tabular-nums; }
  .coverage .coverage-detail { margin-top: 5px; max-width: 35ch; }
  .workflow { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); gap: 22px; align-items: start; margin-top: clamp(27px, 5.5vw, 65px); }
  .workflow h3, .closing h3 { margin: 0 0 7px; font-size: clamp(2.05rem, 3.3vw, 3.45rem); line-height: .96; }
  .workflow ol { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
  .workflow li { display: flex; align-items: flex-start; gap: 13px; padding: 14px 0; border-top: 1px solid var(--border-strong); }
  .workflow h4 { margin: 0 0 5px; font-size: .96rem; }
  .team-heading { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); align-items: center; gap: clamp(18px, 4vw, 55px); }
  .team-list { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; padding: 0; margin: 0; list-style: none; }
  .team-list li { overflow: hidden; border: 1px solid var(--border); border-radius: var(--control-radius); background: var(--background); }
  .team-list strong { display: block; padding: 10px; font-size: .84rem; overflow-wrap: anywhere; }

  .faq-layout { display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr); gap: clamp(17px, 4vw, 55px); }
  .faq-list { border-top: 1px solid var(--border-strong); }
  .faq-list details { border-bottom: 1px solid var(--border-strong); }
  .faq-list summary { display: flex; justify-content: space-between; align-items: center; gap: 15px; padding-block: 17px; color: var(--text); cursor: pointer; font-weight: 650; list-style: none; }
  .faq-list summary::-webkit-details-marker { display: none; }
  .faq-list summary :global(svg) { color: var(--accent); }
  .faq-list details[open] summary :global(svg) { transform: rotate(180deg); }
  .faq-list p { margin: 0 26px 16px 0; }
  .closing { grid-column: 1 / -1; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px; padding: clamp(16px, 3.5vw, 45px); border: 1px solid var(--accent-border); border-radius: var(--card-radius); background: var(--accent-surface); }
  .closing .button { gap: 8px; }

  @media (prefers-reduced-motion: no-preference) {
    .current .reveal { animation: section-in .48s cubic-bezier(.22, .75, .32, 1) both; }
    .current .demo-content, .current details[open] p { animation: section-in .25s ease-out both; }
    .current .faq-list summary :global(svg) { transition: transform .18s ease; }
    @keyframes section-in {
      from { opacity: .56; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  }
  @media (max-width: 950px) {
    .hero-layout { grid-template-columns: minmax(0, 1fr); }
    .hero h1 { font-size: clamp(3.9rem, 11vw, 7.2rem); }
    .hero::before { background: linear-gradient(90deg, #071511d9 4%, #0a1b1175 75%), linear-gradient(0deg, #101b19, #101b1900 55%); }
    .hero-brand { margin-bottom: 17px; }
    .hero-map { width: min(100%, 680px); }
    .team-list { grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); }
  }
  @media (max-width: 700px) {
    .demo-layout, .team-heading, .workflow, .faq-layout { grid-template-columns: minmax(0, 1fr); }
    .team-heading .section-heading, .faq-layout .section-heading { margin-bottom: 0; }
    .demo-tabs { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .demo-tabs button { flex-direction: column; align-items: flex-start; justify-content: flex-start; min-height: 79px; gap: 6px; padding: 8px; font-size: .74rem; }
    .demo-tabs .story-icon { width: 30px; height: 30px; }
    .demo-tabs button :global(.tab-arrow) { display: none; }
    .demo-stage { min-height: 290px; }
    .story-grid { grid-template-columns: minmax(0, 1fr); }
    .story { padding: 18px 0; }
    .story + .story { border-left: 0; border-top: 1px solid var(--border-strong); }
    .coverage .coverage-detail { font-size: .78rem; }
  }
  @media (max-width: 490px) {
    .hero h1 { font-size: clamp(3.3rem, 14vw, 4.6rem); }
    .hero-layout { gap: 26px; }
    .coverage { grid-template-columns: 1fr; }
    .coverage div { display: grid; grid-template-columns: 70px 1fr; align-items: center; gap: 5px 12px; }
    .coverage div + div { border-left: 0; border-top: 1px solid var(--border); }
    .coverage-value { grid-row: span 2; font-size: 2.8rem; }
    .coverage .coverage-detail { margin-top: 0; }
  }
</style>

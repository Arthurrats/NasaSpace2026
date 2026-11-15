<script>
  import { onMount, tick } from 'svelte';
  import SiteLayout from './layouts/SiteLayout.svelte';
  import Landing from './pages/Landing.svelte';
  import Dashboard from './pages/Dashboard.svelte';
  import FireActivity from './pages/FireActivity.svelte';
  import Login from './pages/Login.svelte';
  import MapWorkspace from './pages/MapWorkspace.svelte';

  let currentPage = $state('#/');
  let landingSection = $state('solucao');
  let demoSession = $state(false);
  let sessionReady = false;
  let sessionBusy = $state(false);
  let sessionError = $state('');
  let loginDestination = '#/painel';
  const pageTitles = {
    '#/': 'prevIA — Monitoramento e análise de queimadas',
    '#/login': 'Login — prevIA',
    '#/painel': 'Dashboard — prevIA',
    '#/mapa': 'Mapa — prevIA',
    '#/timelapse': 'Timelapse — prevIA',
    '#/paises': 'Análise por país — prevIA',
    '#/previsor': 'Previsor — prevIA',
    '#/calendario': 'Calendário — prevIA',
  };

  function syncRoute() {
    if (!sessionReady) return;
    let hash = window.location.hash;
    if (Object.hasOwn(pageTitles, hash) && hash !== '#/' && hash !== '#/login' && !demoSession) {
      loginDestination = hash;
      hash = '#/login';
      window.history.replaceState(null, '', hash);
    }
    const nextPage = Object.hasOwn(pageTitles, hash) ? hash : '#/';
    const pageChanged = currentPage !== nextPage;
    if (pageChanged) {
      currentPage = nextPage;
      landingSection = 'solucao';
    }
    const sectionId = nextPage === '#/' && hash.startsWith('#') && !hash.startsWith('#/') ? hash.slice(1) : '';
    if (pageChanged || sectionId) {
      tick().then(() => {
        if (window.location.hash !== hash) return;
        const behavior = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
        const section = sectionId ? document.getElementById(sectionId) : null;
        if (section) {
          section.scrollIntoView({ behavior, block: 'start' });
          section.focus({ preventScroll: true });
        } else if (pageChanged) {
          window.scrollTo({ top: 0, behavior });
          document.getElementById('conteudo')?.focus({ preventScroll: true });
        }
      });
    }
    document.title = pageTitles[nextPage];
  }

  async function requestSession(method = 'GET') {
    const options = method === 'POST' ? { method, headers: { 'Content-Type': 'application/json' }, body: '{}' } : { method };
    const response = await fetch('/api/demo-session', options);
    if (!response.ok) throw new Error('Falha na sessão demonstrativa.');
    return (await response.json()).active === true;
  }

  async function enterDemo() {
    if (sessionBusy) return;
    sessionBusy = true;
    sessionError = '';
    try {
      demoSession = await requestSession('POST');
      if (!demoSession) throw new Error('Sessão recusada.');
      window.location.hash = loginDestination;
      loginDestination = '#/painel';
    } catch {
      sessionError = 'Não foi possível iniciar a sessão demonstrativa. Tente novamente.';
    } finally {
      sessionBusy = false;
    }
  }

  async function leaveDemo() {
    if (sessionBusy) return;
    sessionBusy = true;
    sessionError = '';
    try {
      demoSession = await requestSession('DELETE');
      if (demoSession) throw new Error('Sessão ainda ativa.');
      window.history.replaceState(null, '', '#/login');
      syncRoute();
    } catch {
      sessionError = 'Não foi possível encerrar a sessão demonstrativa. Tente novamente.';
    } finally {
      sessionBusy = false;
    }
  }

  onMount(() => {
    requestSession().then(active => { demoSession = active; }).catch(() => {}).finally(() => {
      sessionReady = true;
      syncRoute();
    });
  });
</script>

<svelte:window onhashchange={syncRoute} />
<SiteLayout {currentPage} {landingSection} onLogout={leaveDemo}>
  {#if sessionError}<p class="session-error" role="alert">{sessionError}</p>{/if}
  {#if currentPage === '#/painel' && demoSession}
    <Dashboard />
  {:else if currentPage === '#/login'}
    <Login onLogin={enterDemo} busy={sessionBusy} />
  {:else if currentPage === '#/mapa' && demoSession}
    <MapWorkspace />
  {:else if currentPage === '#/timelapse' && demoSession}
    <MapWorkspace timelineOnly />
  {:else if currentPage === '#/paises' && demoSession}
    <Dashboard countryOnly />
  {:else if (currentPage === '#/previsor' || currentPage === '#/calendario') && demoSession}
    <FireActivity view={currentPage === '#/calendario' ? 'calendar' : 'forecast'} />
  {:else}
    <Landing onSectionChange={(id) => { landingSection = id; }} />
  {/if}
</SiteLayout>

<style>
  .session-error { margin: 12px; padding: 10px 14px; border: 1px solid var(--critical); border-radius: var(--control-radius); color: var(--text); background: var(--surface); }
  @media (prefers-reduced-motion: reduce) {
    :global(html) { scroll-behavior: auto; }
  }
</style>

<script>
  import { onMount, tick } from 'svelte';
  import SiteLayout from './layouts/SiteLayout.svelte';
  import Landing from './pages/Landing.svelte';
  import Dashboard from './pages/Dashboard.svelte';
  import Login from './pages/Login.svelte';
  import MapWorkspace from './pages/MapWorkspace.svelte';

  let currentPage = $state('#/');
  let demoSession = $state(false);
  let loginDestination = '#/painel';
  const sessionKey = 'previa:demo-session';
  const pageTitles = {
    '#/': 'prevIA — Monitoramento e análise de queimadas',
    '#/login': 'Login — prevIA',
    '#/painel': 'Dashboard — prevIA',
    '#/mapa': 'Mapa — prevIA',
  };

  function linkedSection() {
    return document.getElementById(window.location.hash.slice(1));
  }

  function syncRoute() {
    let hash = window.location.hash;
    if ((hash === '#/painel' || hash === '#/mapa') && !demoSession) {
      loginDestination = hash;
      hash = '#/login';
      window.history.replaceState(null, '', hash);
    }
    const nextPage = Object.hasOwn(pageTitles, hash) ? hash : '#/';
    if (currentPage !== nextPage) {
      currentPage = nextPage;
      tick().then(() => {
        const section = linkedSection();
        if (section) {
          section.scrollIntoView();
          section.focus({ preventScroll: true });
        } else {
          window.scrollTo(0, 0);
          document.getElementById('conteudo').focus({ preventScroll: true });
        }
      });
    }
    document.title = pageTitles[nextPage];
  }

  function enterDemo() {
    demoSession = true;
    try { sessionStorage.setItem(sessionKey, 'active'); } catch {}
    window.location.hash = loginDestination;
    loginDestination = '#/painel';
  }

  function leaveDemo() {
    demoSession = false;
    try { sessionStorage.removeItem(sessionKey); } catch {}
    window.history.replaceState(null, '', '#/login');
    syncRoute();
  }

  onMount(() => {
    try { demoSession = sessionStorage.getItem(sessionKey) === 'active'; } catch {}
    syncRoute();
    linkedSection()?.scrollIntoView();
  });
</script>

<svelte:window onhashchange={syncRoute} />
<SiteLayout {currentPage} onLogout={leaveDemo}>
  {#if currentPage === '#/painel' && demoSession}
    <Dashboard />
  {:else if currentPage === '#/login'}
    <Login onLogin={enterDemo} />
  {:else if currentPage === '#/mapa' && demoSession}
    <MapWorkspace />
  {:else}
    <Landing />
  {/if}
</SiteLayout>

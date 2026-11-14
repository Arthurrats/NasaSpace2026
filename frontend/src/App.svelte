<script>
  import { onMount, tick } from 'svelte';
  import SiteLayout from './layouts/SiteLayout.svelte';
  import Landing from './pages/Landing.svelte';
  import Dashboard from './pages/Dashboard.svelte';

  let currentPage = $state('#/');

  function linkedSection() {
    return document.getElementById(window.location.hash.slice(1));
  }

  function syncRoute() {
    const nextPage = window.location.hash === '#/painel' ? '#/painel' : '#/';
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
    document.title = nextPage === '#/painel'
      ? 'Painel — prevIA'
      : 'prevIA — Monitoramento e análise de queimadas';
  }

  onMount(() => {
    syncRoute();
    linkedSection()?.scrollIntoView();
  });
</script>

<svelte:window onhashchange={syncRoute} />
<SiteLayout {currentPage}>
  {#if currentPage === '#/painel'}
    <Dashboard />
  {:else}
    <Landing />
  {/if}
</SiteLayout>

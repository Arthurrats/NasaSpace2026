<script>
  import { onMount, tick } from 'svelte';
  import { ArrowUpRight, Flame, LayoutDashboard, House, Menu, X } from '@lucide/svelte';
  import Landing from './pages/Landing.svelte';
  import Dashboard from './pages/Dashboard.svelte';

  const pages = [
    { href: '#/', title: 'Início', icon: House },
    { href: '#/painel', title: 'Painel', icon: LayoutDashboard },
  ];

  let currentPage = $state('#/');
  let navigation = $state();

  function syncRoute() {
    const nextPage = window.location.hash === '#/painel' ? '#/painel' : '#/';
    if (currentPage !== nextPage) {
      currentPage = nextPage;
      window.scrollTo(0, 0);
      tick().then(() => document.getElementById('conteudo').focus());
    }
    document.title = nextPage === '#/painel'
      ? 'Painel — Vigia Terra'
      : 'Vigia Terra — Observatório de incêndios';
  }

  onMount(syncRoute);
</script>

<svelte:window onhashchange={syncRoute} />
<a class="skip-link" href="#conteudo" onclick={(event) => {
  event.preventDefault();
  document.getElementById('conteudo').focus();
}}>Pular para o conteúdo</a>

<header class="topbar">
  <div class="shell topbar-inner">
    <a class="brand" href="#/" aria-label="Vigia Terra — Início">
      <span class="brand-mark"><Flame size={19} strokeWidth={2.1} /></span>
      VIGIA<span class="brand-quiet">TERRA</span>
    </a>

    <nav class="desktop-navigation" aria-label="Navegação principal">
      {#each pages as page}
        <a href={page.href} aria-current={currentPage === page.href ? 'page' : undefined}>{page.title}</a>
      {/each}
    </nav>

    <div class="topbar-actions">
      {#if currentPage === '#/'}
        <a class="button button-outline desktop-cta" href="#/painel">Abrir painel <ArrowUpRight size={16} /></a>
      {/if}
      <button class="icon-button mobile-menu" aria-label="Abrir menu" aria-haspopup="dialog" onclick={() => navigation.showModal()}>
        <Menu size={23} />
      </button>
    </div>
  </div>
</header>

<dialog class="mobile-drawer" bind:this={navigation} aria-labelledby="menu-title">
  <div class="drawer-header">
    <strong id="menu-title">Menu</strong>
    <button class="icon-button" aria-label="Fechar menu" onclick={() => navigation.close()}><X size={22} /></button>
  </div>
  <nav aria-label="Navegação móvel">
    {#each pages as page}
      <a href={page.href} aria-current={currentPage === page.href ? 'page' : undefined} onclick={() => navigation.close()}>
        <page.icon size={18} /> {page.title}
      </a>
    {/each}
  </nav>
</dialog>

<main id="conteudo" class="shell" tabindex="-1">
  {#if currentPage === '#/painel'}
    <Dashboard />
  {:else}
    <Landing />
  {/if}
</main>

<footer class="shell footer">
  <div class="footer-brand"><Flame size={17} /> Vigia Terra</div>
  <span>Observatório de incêndios florestais</span>
</footer>

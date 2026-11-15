<script>
  import { Activity, CircleHelp, Database, Flame, Globe, House, LogIn, Mail, Menu, Moon, Route, Sun, Users, X } from '@lucide/svelte';
  import BrandLockup from './BrandLockup.svelte';

  let { currentPage, landingSection } = $props();
  let navigation;
  let theme = $state(document.documentElement.dataset.theme === 'light' ? 'light' : 'dark');

  const landingSections = [
    { id: 'solucao', title: 'Solução', icon: Globe, desktop: true },
    { id: 'problema', title: 'Impactos', icon: Flame },
    { id: 'recursos', title: 'Recursos', icon: Activity, desktop: true },
    { id: 'dados', title: 'Dados', icon: Database, desktop: true },
    { id: 'uso', title: 'Como usar', icon: Route, desktop: true },
    { id: 'equipe', title: 'Equipe', icon: Users, desktop: true },
    { id: 'perguntas', title: 'Perguntas frequentes', icon: CircleHelp },
    { id: 'contato', title: 'Contato', icon: Mail },
  ];
  const isLanding = $derived(currentPage === '#/');
  const pages = $derived(isLanding ? landingSections : [{ id: 'solucao', title: 'Início', icon: House, desktop: true }]);
  const themeAction = $derived(theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro');

  function toggleTheme() {
    theme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    const themeColor = document.querySelector('meta[name="theme-color"]');
    if (themeColor) themeColor.content = getComputedStyle(document.documentElement).getPropertyValue('--background').trim();
    try { localStorage.setItem('previa:theme', theme); } catch {}
  }
</script>

<header class:landing={isLanding}>
  <div class="header-inner">
    <a class="brand" href="#solucao" aria-label="prevIA, início"><BrandLockup /></a>

    <nav class="desktop-navigation" aria-label="Navegação principal">
      {#each pages.filter((page) => page.desktop) as { id, title } (id)}
        <a href={'#' + id} aria-current={isLanding && landingSection === id ? 'location' : undefined}>{title}</a>
      {/each}
    </nav>

    <div class="header-actions">
      <button type="button" class="icon-button" aria-label={themeAction} title={themeAction} onclick={toggleTheme}>
        {#if theme === 'dark'}<Sun size={20} aria-hidden="true" />{:else}<Moon size={20} aria-hidden="true" />{/if}
      </button>
      {#if isLanding}
        <a class="button button-outline account-button" href="#/login" aria-label="Login">
          <LogIn size={18} aria-hidden="true" /><span>Login</span>
        </a>
      {/if}
      <button type="button" class="icon-button mobile-menu" aria-label="Abrir menu" aria-haspopup="dialog" onclick={() => navigation.showModal()}>
        <Menu size={23} aria-hidden="true" />
      </button>
    </div>
  </div>
</header>

<dialog class="mobile-drawer" bind:this={navigation} aria-labelledby="menu-title">
  <div class="drawer-header">
    <strong id="menu-title">Menu</strong>
    <button type="button" class="icon-button" aria-label="Fechar menu" onclick={() => navigation.close()}><X size={22} aria-hidden="true" /></button>
  </div>
  <nav aria-label="Navegação móvel">
    {#each pages as { id, title, icon: Icon } (id)}
      <a href={'#' + id} aria-current={isLanding && landingSection === id ? 'location' : undefined} onclick={() => navigation.close()}>
        <Icon size={18} aria-hidden="true" /> {title}
      </a>
    {/each}
  </nav>
</dialog>

<style>
  header {
    position: sticky;
    z-index: 20;
    top: 0;
    border-bottom: 1px solid var(--border);
    background: var(--background);
  }

  header.landing {
    background: color-mix(in srgb, var(--background) 94%, transparent);
    backdrop-filter: blur(16px);
  }

  .header-inner {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    min-height: calc(var(--header-height) - 1px);
    gap: 20px;
    padding-inline: var(--page-inset);
  }

  .brand {
    display: inline-flex;
    width: fit-content;
  }

  .header-actions { display: flex; align-items: center; justify-self: end; gap: 8px; }
  .account-button { gap: 8px; background: transparent; color: var(--text); }
  .account-button :global(svg) { color: var(--accent); }

  .desktop-navigation { display: flex; align-items: stretch; gap: clamp(18px, 2.25vw, 32px); align-self: stretch; }
  .desktop-navigation a {
    display: grid;
    align-items: center;
    position: relative;
    color: var(--muted);
    font-size: .875rem;
    font-weight: 600;
    white-space: nowrap;
  }

  .desktop-navigation a:hover, .desktop-navigation a[aria-current] { color: var(--text); }
  .desktop-navigation a[aria-current]::after {
    content: '';
    position: absolute;
    inset: auto 0 -1px;
    height: 2px;
    background: var(--accent);
    border-radius: 2px 2px 0 0;
  }

  .icon-button {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    color: var(--text);
    border: 1px solid var(--border-strong);
    border-radius: var(--control-radius);
    background: transparent;
  }

  .icon-button:hover { background: var(--surface-raised); }
  .mobile-menu { display: none; }

  .mobile-drawer {
    position: fixed;
    inset: 0 0 0 auto;
    margin: 0;
    width: min(84vw, 360px);
    max-width: none;
    height: 100%;
    max-height: none;
    padding: 20px;
    border: 0;
    border-left: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    overflow-y: auto;
    overscroll-behavior: contain;
  }

  .mobile-drawer::backdrop { background: color-mix(in srgb, var(--background) 80%, transparent); }
  .drawer-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
  .mobile-drawer nav { display: grid; gap: 7px; margin-top: 16px; }
  .mobile-drawer nav a {
    min-height: 48px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding-inline: 12px;
    border-radius: var(--control-radius);
    color: var(--muted);
  }

  .mobile-drawer nav a[aria-current], .mobile-drawer nav a:hover { background: var(--surface-raised); color: var(--text); }
  .mobile-drawer nav a[aria-current] :global(svg) { color: var(--indicator); }

  @media (max-width: 920px) {
    .header-inner { grid-template-columns: 1fr auto; gap: 8px; }
    .desktop-navigation { display: none; }
    .mobile-menu { display: grid; }
  }

  @media (max-width: 380px) {
    .header-inner { padding-inline: 12px; }
    .header-actions { gap: 6px; }
    .brand { --brand-size: 1.3rem; }
    .account-button { width: 44px; padding-inline: 0; }
    .account-button span { display: none; }
  }
</style>

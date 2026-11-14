<script>
  import { Activity, ArrowUpRight, Flame, Globe, House, LayoutDashboard, Mail, Menu, Users, X } from '@lucide/svelte';
  import BrandLockup from './BrandLockup.svelte';

  let { currentPage } = $props();
  let navigation;

  const dashboard = { href: '#/painel', title: 'Painel', icon: LayoutDashboard };
  const landingSections = [
    { href: '#solucao', title: 'Solução', icon: Globe },
    { href: '#problema', title: 'O problema', icon: Flame },
    { href: '#recursos', title: 'Recursos', icon: Activity },
    { href: '#equipe', title: 'Equipe', icon: Users },
    { href: '#contato', title: 'Contato', icon: Mail },
  ];
  const dashboardPages = [{ href: '#/', title: 'Início', icon: House }, dashboard];
  const isLanding = $derived(currentPage === '#/');
  const pages = $derived(isLanding ? landingSections : dashboardPages);
  const mobilePages = $derived(isLanding ? [...landingSections, dashboard] : dashboardPages);
</script>

<header>
  <div class="header-inner">
    <a class="brand" href="#/" aria-label="prevIA, início"><BrandLockup /></a>

    <nav class="desktop-navigation" aria-label="Navegação principal">
      {#each pages as { href, title }}
        <a {href} aria-current={currentPage === href ? 'page' : undefined}>{title}</a>
      {/each}
    </nav>

    <div class="header-actions">
      {#if isLanding}
        <a class="button button-outline desktop-cta" href={dashboard.href}>Abrir painel <ArrowUpRight size={16} /></a>
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
    {#each mobilePages as { href, title, icon: Icon }}
      <a {href} aria-current={currentPage === href ? 'page' : undefined} onclick={() => navigation.close()}>
        <Icon size={18} /> {title}
      </a>
    {/each}
  </nav>
</dialog>

<style>
  header { border-bottom: 1px solid var(--border); }

  .header-inner {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    min-height: 72px;
    gap: 20px;
    padding-inline: var(--page-inset);
  }

  .brand {
    display: inline-flex;
    width: fit-content;
  }

  .header-actions { justify-self: end; }

  .desktop-navigation { display: flex; align-items: stretch; gap: 32px; align-self: stretch; }
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
    .header-inner { min-height: 64px; grid-template-columns: 1fr auto; }
    .desktop-navigation, .desktop-cta { display: none; }
    .mobile-menu { display: grid; }
  }
</style>

<script>
  import { CalendarDays, Clock, Flame, Globe, LayoutDashboard, LogOut, MapPin, Menu, Moon, Sun, TrendingUp, X } from '@lucide/svelte';
  import BrandLockup from './BrandLockup.svelte';

  let { currentPage, onLogout } = $props();
  let theme = $state(document.documentElement.dataset.theme === 'light' ? 'light' : 'dark');
  let menuOpen = $state(false);
  let menuToggle;
  const groups = [
    { label: 'Monitoramento', items: [
      { href: '#/mapa', label: 'Mapa de focos', icon: Globe },
      { href: '#/painel', label: 'Dashboard', icon: LayoutDashboard },
      { href: '#/timelapse', label: 'Timelapse', icon: Clock },
    ] },
    { label: 'Análise', items: [
      { href: '#/paises', label: 'Análise por país', icon: MapPin },
      { href: '#/previsor', label: 'Previsor', icon: TrendingUp },
      { href: '#/calendario', label: 'Calendário', icon: CalendarDays },
    ] },
  ];
  const themeLabel = $derived(theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro');

  function closeMenu(returnFocus = false) {
    if (!menuOpen) return;
    menuOpen = false;
    if (returnFocus) menuToggle?.focus();
  }

  function toggleTheme() {
    theme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = getComputedStyle(document.documentElement).getPropertyValue('--background').trim();
    try { localStorage.setItem('previa:theme', theme); } catch {}
  }
</script>

<svelte:window onkeydown={(event) => { if (event.key === 'Escape') closeMenu(true); }} />

<aside class="platform-sidebar" aria-label="Plataforma prevIA">
  <div class="sidebar-header">
    <a class="brand" href="#/painel" aria-label="prevIA, Dashboard" onclick={() => closeMenu()}><BrandLockup /></a>
    <button class="menu-toggle" type="button" aria-expanded={menuOpen} aria-controls="platform-menu" bind:this={menuToggle}
      onclick={() => { menuOpen = !menuOpen; }}>
      {#if menuOpen}<X size={19} aria-hidden="true" />{:else}<Menu size={19} aria-hidden="true" />{/if}
      Menu
    </button>
  </div>
  <div class="platform-menu" class:open={menuOpen} id="platform-menu">
  <nav aria-label="Navegação da plataforma">
    {#each groups as group (group.label)}
      <div class="nav-group">
        <p class="workspace-label">{group.label}</p>
        {#each group.items as { href, label, icon: Icon } (href)}
          <a class="nav-item" class:active={currentPage === href} {href} aria-current={currentPage === href ? 'page' : undefined}
            onclick={() => closeMenu(currentPage === href)}>
            <Icon size={20} aria-hidden="true" /><span>{label}</span>
          </a>
        {/each}
      </div>
    {/each}
  </nav>
  <section class="data-note" aria-label="Estado dos dados">
    <Flame size={17} aria-hidden="true" />
    <p><strong>Dados históricos</strong><br />Cenário demonstrativo</p>
  </section>
  <div class="sidebar-actions">
    <button type="button" class="action" aria-label={themeLabel} onclick={toggleTheme}>
      {#if theme === 'dark'}<Sun size={18} aria-hidden="true" />{:else}<Moon size={18} aria-hidden="true" />{/if}
      <span>{themeLabel}</span>
    </button>
    <button type="button" class="action logout" onclick={onLogout}><LogOut size={18} aria-hidden="true" /><span>Sair</span></button>
  </div>
  </div>
</aside>

<style>
  .platform-sidebar {
    position: sticky;
    z-index: 19;
    top: 0;
    display: flex;
    flex-direction: column;
    width: 236px;
    height: 100svh;
    flex: 0 0 236px;
    padding: 24px 14px 16px;
    border-right: 1px solid var(--border);
    background: var(--surface);
  }

  .sidebar-header { display: flex; justify-content: space-between; align-items: center; }
  .brand { display: inline-flex; width: fit-content; min-height: 44px; align-items: center; padding-inline: 10px; }
  .menu-toggle { display: none; }
  .platform-menu { min-height: 0; flex: 1; display: flex; flex-direction: column; overflow-y: auto; margin-top: 24px; padding: 4px; }
  .workspace-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 10px 7px;
    color: var(--muted);
    font-size: .72rem;
    font-weight: 750;
    letter-spacing: .085em;
    text-transform: uppercase;
  }

  nav { display: grid; gap: 18px; margin-bottom: 20px; }
  .nav-group { display: grid; gap: 4px; }
  .nav-item, .action {
    display: flex;
    align-items: center;
    gap: 11px;
    min-height: 48px;
    padding-inline: 11px;
    border: 1px solid transparent;
    border-radius: var(--control-radius);
    color: var(--muted);
    font-size: .9rem;
    font-weight: 600;
    transition: color .2s ease, background .2s ease, border-color .2s ease;
  }

  .nav-item:hover, .action:hover { background: var(--background); color: var(--text); }
  .nav-item.active { border-color: var(--accent-border); background: var(--accent-surface); color: var(--text); box-shadow: inset 3px 0 var(--accent); }
  .nav-item :global(svg), .action :global(svg) { flex: none; }
  .nav-item.active :global(svg) { color: var(--accent); }
  .data-note { display: flex; gap: 10px; margin: auto 4px 18px; padding: 12px 10px; border: 1px solid var(--border); border-radius: var(--control-radius); color: var(--indicator); }
  .data-note p { color: var(--muted); font-size: .8rem; line-height: 1.6; }
  .data-note strong { color: var(--text); font-weight: 600; }
  .sidebar-actions { display: grid; gap: 4px; padding-top: 12px; border-top: 1px solid var(--border); }
  .action { width: 100%; border: 0; background: transparent; cursor: pointer; text-align: left; }
  .action :global(svg) { color: var(--accent); }
  .logout :global(svg) { color: var(--critical); }

  @media (max-width: 760px) {
    .platform-sidebar {
      position: sticky;
      top: 0;
      width: 100%;
      height: auto;
      flex: none;
      padding: 8px var(--workspace-inset);
      border-right: 0;
      border-bottom: 1px solid var(--border);
    }

    .brand { padding-inline: 0; }
    .data-note { display: none; }
    .menu-toggle { display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 5px 12px;
      border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--background); color: var(--text); font-weight: 650; }
    .platform-menu { display: none; max-height: 60svh; margin-top: 10px; }
    .platform-menu.open { display: flex; }
    nav { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-bottom: 8px; }
    .sidebar-actions { display: flex; padding-top: 6px; }
    .action { width: auto; }
  }
  @media (max-width: 390px) { nav { grid-template-columns: 1fr; } }
</style>

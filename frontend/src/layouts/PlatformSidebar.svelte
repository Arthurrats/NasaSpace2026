<script>
  import { CalendarDays, Clock, Flame, Globe, LayoutDashboard, LogOut, MapPin, Moon, Sun, TrendingUp } from '@lucide/svelte';
  import BrandLockup from './BrandLockup.svelte';

  let { currentPage, onLogout } = $props();
  let theme = $state(document.documentElement.dataset.theme === 'light' ? 'light' : 'dark');
  const items = [
    { href: '#/painel', label: 'Dashboard', icon: LayoutDashboard },
    { href: '#/mapa', label: 'Mapa de focos', icon: Globe },
    { href: '#/timelapse', label: 'Timelapse', icon: Clock },
    { href: '#/paises', label: 'Países', icon: MapPin },
    { href: '#/previsor', label: 'Previsor', icon: TrendingUp },
    { href: '#/calendario', label: 'Calendário', icon: CalendarDays },
  ];
  const themeLabel = $derived(theme === 'dark' ? 'Ativar tema claro' : 'Ativar tema escuro');

  function toggleTheme() {
    theme = theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = getComputedStyle(document.documentElement).getPropertyValue('--background').trim();
    try { localStorage.setItem('previa:theme', theme); } catch {}
  }
</script>

<aside class="platform-sidebar" aria-label="Plataforma prevIA">
  <a class="brand" href="#/painel" aria-label="prevIA dashboard"><BrandLockup /></a>
  <div class="workspace-label"><span class="status-dot"></span> MONITORAMENTO</div>
  <nav aria-label="Navegação da plataforma">
    {#each items as { href, label, icon: Icon }}
      <a class="nav-item" class:active={currentPage === href} {href} aria-current={currentPage === href ? 'page' : undefined}>
        <Icon size={19} aria-hidden="true" /><span>{label}</span>
      </a>
    {/each}
  </nav>
  <section class="data-note" aria-label="Estado dos dados">
    <Flame size={17} aria-hidden="true" />
    <p>Dados observados<br /><strong>Cenário demonstrativo</strong></p>
  </section>
  <div class="sidebar-actions">
    <button type="button" class="action" aria-label={themeLabel} onclick={toggleTheme}>
      {#if theme === 'dark'}<Sun size={18} aria-hidden="true" />{:else}<Moon size={18} aria-hidden="true" />{/if}
      <span>{themeLabel}</span>
    </button>
    <button type="button" class="action logout" onclick={onLogout}><LogOut size={18} aria-hidden="true" /><span>Sair</span></button>
  </div>
</aside>

<style>
  .platform-sidebar {
    position: sticky;
    z-index: 19;
    top: 0;
    display: flex;
    flex-direction: column;
    width: 252px;
    height: 100svh;
    flex: 0 0 252px;
    padding: 22px 14px 16px;
    border-right: 1px solid var(--border);
    background: var(--surface);
  }

  .brand { display: inline-flex; width: fit-content; padding-inline: 8px; }
  .workspace-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 34px 8px 12px;
    color: var(--muted);
    font-size: .65rem;
    font-weight: 750;
    letter-spacing: .11em;
  }

  .status-dot { width: 7px; height: 7px; background: var(--accent); }
  nav { display: grid; gap: 5px; }
  .nav-item, .action {
    display: flex;
    align-items: center;
    gap: 11px;
    min-height: 44px;
    padding-inline: 11px;
    border: 1px solid transparent;
    border-radius: var(--control-radius);
    color: var(--muted);
    font-size: .86rem;
    font-weight: 600;
    transition: color .2s ease, background .2s ease, border-color .2s ease;
  }

  .nav-item:hover, .action:hover { background: var(--background); color: var(--text); }
  .nav-item.active { border-color: var(--accent-border); background: var(--accent-surface); color: var(--text); }
  .nav-item.active :global(svg) { color: var(--accent); }
  .data-note { display: flex; gap: 10px; margin: auto 4px 18px; padding: 12px 10px; border: 1px solid var(--border); border-radius: var(--control-radius); color: var(--indicator); }
  .data-note p { color: var(--muted); font-size: .73rem; line-height: 1.6; }
  .data-note strong { color: var(--text); font-weight: 600; }
  .sidebar-actions { display: grid; gap: 4px; padding-top: 12px; border-top: 1px solid var(--border); }
  .action { width: 100%; border: 0; background: transparent; font: inherit; cursor: pointer; text-align: left; }
  .action :global(svg) { color: var(--accent); }
  .logout :global(svg) { color: var(--critical); }

  @media (max-width: 760px) {
    .platform-sidebar {
      position: sticky;
      top: 0;
      width: 100%;
      height: auto;
      flex: none;
      padding: 8px var(--page-inset);
      border-right: 0;
      border-bottom: 1px solid var(--border);
    }

    .brand, .workspace-label, .data-note { display: none; }
    nav { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px; }
    .nav-item { justify-content: center; min-height: 42px; padding-inline: 3px; gap: 4px; font-size: .72rem; }
    .sidebar-actions { display: flex; justify-content: center; padding: 4px 0 0; border: 0; }
    .action { width: auto; min-height: 42px; padding-inline: 9px; font-size: .75rem; }
  }
  @media (max-width: 430px) { .nav-item { flex-direction: column; } }
</style>

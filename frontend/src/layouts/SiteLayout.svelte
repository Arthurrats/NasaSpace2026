<script>
  import SiteFooter from './SiteFooter.svelte';
  import SiteHeader from './SiteHeader.svelte';
  import PlatformSidebar from './PlatformSidebar.svelte';

  let { currentPage, landingSection, onLogout, children } = $props();
  const inPlatform = $derived(currentPage !== '#/' && currentPage !== '#/login');
  let content;

  function skipToContent(event) {
    event.preventDefault();
    content.focus();
  }
</script>

<div class="site-layout">
  <a class="skip-link" href="#conteudo" onclick={skipToContent}>Pular para o conteúdo</a>
  {#if !inPlatform}<SiteHeader {currentPage} {landingSection} />{/if}

  <div class:platform-shell={inPlatform}>
    {#if inPlatform}<PlatformSidebar {currentPage} {onLogout} />{/if}
    <main id="conteudo" tabindex="-1" bind:this={content}>{@render children()}</main>
  </div>

  {#if !inPlatform}<SiteFooter />{/if}
</div>

<style>
  .site-layout {
    display: flex;
    flex-direction: column;
    min-height: 100svh;
  }

  .platform-shell { display: flex; height: 100svh; min-height: 0; }
  main { min-width: 0; flex: 1; }
  .platform-shell main { min-height: 0; overflow: auto; scrollbar-gutter: stable; }
  @media (max-width: 760px) { .platform-shell { flex-direction: column; } }
  main:focus { outline: none; }

  .skip-link:focus {
    position: fixed;
    z-index: 30;
    top: 12px;
    left: 12px;
    padding: 12px;
    border-radius: var(--control-radius);
    background: var(--text);
    color: var(--background);
  }

</style>

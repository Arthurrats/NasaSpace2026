<script>
  import SiteFooter from './SiteFooter.svelte';
  import SiteHeader from './SiteHeader.svelte';

  let { currentPage, onLogout, children } = $props();
  let content;

  function skipToContent(event) {
    event.preventDefault();
    content.focus();
  }
</script>

<div class="site-layout">
  <a class="skip-link" href="#conteudo" onclick={skipToContent}>Pular para o conteúdo</a>
  <SiteHeader {currentPage} {onLogout} />

  <main id="conteudo" tabindex="-1" bind:this={content}>
    {@render children()}
  </main>

  <SiteFooter />
</div>

<style>
  .site-layout {
    display: flex;
    flex-direction: column;
    min-height: 100svh;
  }

  main { flex: 1; }
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

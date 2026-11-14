<script>
  import { ArrowUpRight, MessageSquare } from '@lucide/svelte';
  import BrandLockup from './BrandLockup.svelte';

  const contactUrl = 'https://github.com/Arthurrats/NasaSpace2026/issues';
</script>

<footer id="contato" aria-labelledby="contact-title" tabindex="-1">
  <div class="footer-brand">
    <a href="#solucao" aria-label="prevIA, início"><BrandLockup /></a>
    <p>Monitoramento e análise de queimadas.</p>
  </div>

  <div class="footer-contact">
    <div>
      <h2 id="contact-title">Fale com a equipe</h2>
      <p>Use o repositório para compartilhar sugestões ou relatar problemas.</p>
    </div>
    <a href={contactUrl} class="button button-outline">
      <MessageSquare size={17} aria-hidden="true" /> Contato pelo GitHub <ArrowUpRight size={16} aria-hidden="true" />
    </a>
  </div>
</footer>

<style>
  footer {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 30px 48px;
    padding: 34px var(--page-inset);
    border-top: 1px solid var(--border);
    background: var(--background);
  }

  .footer-brand a { display: inline-flex; }
  .footer-brand p { margin-top: 7px; }
  .footer-contact { display: flex; flex-wrap: wrap; align-items: center; gap: 16px 24px; }
  .footer-contact h2 { margin-bottom: 5px; font-size: 1rem; }
  p { color: var(--muted); font-size: .83rem; line-height: 1.55; }
  .footer-contact .button :global(svg:first-child) { color: var(--indicator); }
  footer:focus { outline: none; }
</style>

<script>
  import { footerCopy as copy } from '../content/platform.js';
  import { ArrowUpRight, MessageSquare } from '@lucide/svelte';
  import BrandLockup from './BrandLockup.svelte';

  const repositoryUrl = 'https://github.com/Arthurrats/NasaSpace2026';
</script>

<footer id="contato" aria-labelledby="contact-title" tabindex="-1">
  <div class="footer-brand">
    <a href="#solucao" aria-label="prevIA, início"><BrandLockup /></a>
    <p>{copy.scope}</p>
    <p>{copy.sample}</p>
  </div>

  <nav aria-label="Links do rodapé">
    <h2>{copy.explore}</h2>
    <a href="#problema">{copy.impacts}</a>
    <a href="#recursos">{copy.features}</a>
    <a href="#equipe">{copy.team}</a>
  </nav>

  <div class="footer-contact">
    <div>
      <h2 id="contact-title">{copy.contact}</h2>
      <p>{copy.details}</p>
    </div>
    <a href={repositoryUrl + '/issues'} class="button button-outline">
      <MessageSquare size={17} aria-hidden="true" /> {copy.contactLink} <ArrowUpRight size={16} aria-hidden="true" />
    </a>
    <a class="repository-link" href={repositoryUrl}>Código do projeto <ArrowUpRight size={14} aria-hidden="true" /></a>
  </div>
</footer>

<style>
  footer {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: flex-start;
    gap: 30px 48px;
    padding: 34px var(--page-inset);
    border-top: 1px solid var(--border);
    background: var(--background);
  }

  .footer-brand a { display: inline-flex; }
  .footer-brand p { margin-top: 7px; }
  .footer-contact, nav { display: grid; justify-items: start; gap: 10px; }
  h2 { margin-bottom: 4px; font-size: 1rem; }
  p { color: var(--muted); font-size: .83rem; line-height: 1.55; }
  nav a, .repository-link { color: var(--muted); font-size: .83rem; }
  nav a:hover, .repository-link:hover { color: var(--text); text-decoration: underline; }
  .footer-contact .button :global(svg:first-child) { color: var(--indicator); }
  footer:focus { outline: none; }
</style>

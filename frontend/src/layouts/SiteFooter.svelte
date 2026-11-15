<script>
  import { footerCopy as copy } from '../content/platform.js';
  import { ArrowUpRight, MessageSquare } from '@lucide/svelte';
  import BrandLockup from './BrandLockup.svelte';

  const repositoryUrl = 'https://github.com/Arthurrats/NasaSpace2026';
  const links = [
    { id: 'problema', label: copy.impacts },
    { id: 'recursos', label: copy.features },
    { id: 'dados', label: 'Dados e cobertura' },
    { id: 'uso', label: 'Como usar' },
    { id: 'equipe', label: copy.team },
    { id: 'perguntas', label: 'Perguntas frequentes' },
  ];
</script>

<footer id="contato" aria-labelledby="contact-title" tabindex="-1">
  <div class="footer-brand">
    <a href="#solucao" aria-label="prevIA, início"><BrandLockup /></a>
    <p>{copy.scope}</p>
    <p>{copy.sample}</p>
  </div>

  <nav aria-label="Links do rodapé">
    <h2>{copy.explore}</h2>
    <ul>
      {#each links as { id, label } (id)}
        <li><a href={'#' + id}>{label}</a></li>
      {/each}
    </ul>
  </nav>

  <div class="footer-contact">
    <div>
      <h2 id="contact-title">{copy.contact}</h2>
      <p>{copy.details}</p>
    </div>
    <a href={repositoryUrl + '/issues'} class="button button-outline">
      <MessageSquare size={17} aria-hidden="true" /> {copy.contactLink} <ArrowUpRight size={16} aria-hidden="true" />
    </a>
    <a class="repository-link" href={repositoryUrl}>{copy.source} <ArrowUpRight size={14} aria-hidden="true" /></a>
  </div>
</footer>

<style>
  footer {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr) minmax(14rem, .85fr);
    align-items: start;
    gap: 30px clamp(28px, 4vw, 64px);
    padding: clamp(36px, 4vw, 56px) var(--page-inset);
    border-top: 1px solid var(--border);
    background: color-mix(in srgb, var(--background) 84%, var(--surface));
  }

  .footer-brand a { display: inline-flex; }
  .footer-brand p { margin-top: 7px; }
  .footer-contact, nav { display: grid; justify-items: start; gap: 10px; }
  ul { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 20px; margin: 0; padding: 0; list-style: none; }
  h2 { margin-bottom: 4px; font-size: 1rem; }
  p { color: var(--muted); font-size: .83rem; line-height: 1.55; }
  nav a, .repository-link { color: var(--muted); font-size: .83rem; }
  nav a:hover, .repository-link:hover { color: var(--text); text-decoration: underline; }
  .footer-contact .button :global(svg:first-child) { color: var(--indicator); }
  footer:focus { outline: none; }

  @media (max-width: 940px) {
    footer { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }

  @media (max-width: 580px) {
    footer { grid-template-columns: 1fr; }
  }
</style>

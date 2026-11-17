<script>
  import { loginCopy as copy } from '../content/platform.js';
  import { ArrowRight, UserRound } from '@lucide/svelte';

  let { onLogin, busy = false, checking = false } = $props();
</script>

<section class="login" aria-labelledby="login-title">
  <div class="card login-card">
    <p class="eyebrow">{copy.eyebrow}</p>
    <h1 id="login-title">{copy.title}</h1>
    <p class="description">{copy.description}</p>

    <div class="demo-account">
      <UserRound size={22} aria-hidden="true" />
      <div><strong>{copy.account}</strong><p>{copy.email}</p></div>
    </div>
    <button type="button" class="button button-primary" onclick={onLogin} disabled={busy || checking}>
      {checking ? 'Verificando sessão…' : busy ? 'Iniciando sessão…' : copy.action} <ArrowRight size={18} aria-hidden="true" />
    </button>
  </div>
</section>

<style>
  .login {
    display: grid;
    place-items: center;
    min-block-size: calc(82svh - var(--header-height));
    padding: 32px var(--page-inset);
    background: radial-gradient(ellipse at 50% 40%, var(--surface), var(--background) 70%);
  }

  .login-card { width: min(100%, 460px); padding: clamp(20px, 4vw, 36px); }
  h1 { margin-block: 7px 12px; font: 700 clamp(3.4rem, 7vw, 4.8rem)/.95 var(--heading); }
  .description, .demo-account p { color: var(--muted); font-size: .88rem; line-height: 1.55; }
  .demo-account {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-block: 22px 16px;
    padding: 12px;
    border: 1px solid var(--border);
    border-radius: var(--control-radius);
    background: var(--background);
    overflow-wrap: anywhere;
  }

  .demo-account :global(svg) { color: var(--indicator); }
  .button { width: 100%; }
</style>

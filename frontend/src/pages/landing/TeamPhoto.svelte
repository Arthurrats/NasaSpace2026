<script>
  import { ImageIcon, UsersRound } from '@lucide/svelte';

  let { src, name, initials, group = false } = $props();
</script>

<div class="photo" class:group>
  {#if src}
    <img {src} alt={group ? 'Equipe prevIA' : `Retrato de ${name}`} loading="lazy" />
  {:else}
    <div class="placeholder" aria-hidden="true">
      {#if group}
        <UsersRound size={40} />
        <span>Foto da equipe</span>
      {:else}
        <ImageIcon size={20} />
        <span>{initials}</span>
      {/if}
    </div>
  {/if}
</div>

<style>
  .photo {
    display: grid;
    place-items: center;
    width: 100%;
    aspect-ratio: 4 / 3;
    overflow: hidden;
    background: radial-gradient(ellipse at 50% 30%, var(--surface-raised), var(--surface) 72%);
  }

  .photo.group {
    aspect-ratio: 16 / 7;
    max-block-size: 430px;
    margin-bottom: 16px;
    border: 1px dashed var(--border-strong);
    border-radius: var(--card-radius);
    background: radial-gradient(ellipse at 50% 30%, var(--surface-raised), var(--background) 82%);
  }

  img { width: 100%; height: 100%; min-height: 0; object-fit: cover; }
  .placeholder {
    display: grid;
    justify-items: center;
    gap: 10px;
    color: var(--indicator);
    font-size: .85rem;
    font-weight: 650;
  }
</style>

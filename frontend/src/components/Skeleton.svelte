<script>
  let { width = '100%', height = '1rem', overlay = false } = $props();
</script>

<span class="skeleton" class:overlay aria-hidden="true" style:width style:height></span>

<style>
  .skeleton {
    --skeleton-base: color-mix(in srgb, var(--border) 80%, var(--accent));
    --skeleton-highlight: color-mix(in srgb, var(--surface-raised) 60%, var(--accent));

    display: block;
    max-width: 100%;
    border-radius: var(--control-radius);
    background-color: var(--skeleton-base);
    background-image: linear-gradient(100deg, var(--skeleton-base) 20%, var(--skeleton-highlight) 50%, var(--skeleton-base) 80%);
    background-position: 50% 0;
    background-size: 200% 100%;
    animation: shimmer 1.6s ease-in-out infinite;
  }

  .overlay { position: absolute; inset: 0; opacity: .85; pointer-events: none; }

  @keyframes shimmer {
    from { background-position: 100% 0; }
    to { background-position: -100% 0; }
  }
</style>

<script>
  import { onDestroy, tick } from 'svelte';
  import { Search, X } from '@lucide/svelte';
  import { autocompleteTerritories, cachedSuggestions, loadTerritory, normalizePlaceQuery, rankTerritories } from '../data/territories.js';

  let { territory, onSelect, onClear } = $props();
  const id = $props.id();
  const areaFormat = new Intl.NumberFormat('pt-BR', { maximumSignificantDigits: 5 });
  let input;
  let query = $state('');
  let open = $state(false);
  let highlightedId = $state(null);
  let remote = $state.raw(null);
  let searching = $state(false);
  let searchError = $state(false);
  let pendingPlace = $state(null);
  let failedPlace = $state(null);
  let boundaryRequest;
  const term = $derived(normalizePlaceQuery(query));
  const results = $derived(term.length < 2 ? [] : rankTerritories(term, remote?.term === term ? remote.matches : []));
  const highlighted = $derived(results.findIndex(place => place.id === highlightedId));
  const expanded = $derived(open && term.length >= 2 && !pendingPlace);

  $effect(() => {
    const candidate = term;
    const cached = cachedSuggestions(candidate);
    const shouldSearch = expanded && !cached;
    remote = cached ? { term: candidate, matches: cached } : null;
    searchError = false;
    searching = shouldSearch;
    if (!shouldSearch) return;

    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const matches = await autocompleteTerritories(candidate, controller.signal);
        if (!controller.signal.aborted) remote = { term: candidate, matches };
      } catch {
        if (!controller.signal.aborted) searchError = true;
      } finally {
        if (!controller.signal.aborted) searching = false;
      }
    }, 250);

    return () => { clearTimeout(timer); controller.abort(); };
  });

  async function select(place) {
    boundaryRequest?.abort();
    const controller = new AbortController();
    boundaryRequest = controller;
    pendingPlace = place;
    failedPlace = null;
    open = false;

    try {
      const boundary = await loadTerritory(place, controller.signal);
      if (controller.signal.aborted) return;
      query = '';
      onSelect({ ...place, ...boundary });
    } catch {
      if (!controller.signal.aborted) failedPlace = place;
    } finally {
      if (!controller.signal.aborted) pendingPlace = null;
    }
  }

  function edit(event) {
    boundaryRequest?.abort();
    pendingPlace = null;
    failedPlace = null;
    highlightedId = null;
    query = event.currentTarget.value;
    open = true;
  }

  function navigate(event) {
    if (event.key === 'Escape') {
      open = false;
      return;
    }
    if (!results.length || pendingPlace) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      open = true;
      const next = event.key === 'ArrowDown' ? (highlighted + 1) % results.length :
        (highlighted <= 0 ? results.length : highlighted) - 1;
      highlightedId = results[next].id;
      tick().then(() => document.getElementById(id + '-result-' + highlighted)?.scrollIntoView({ block: 'nearest' }));
    }
    if (event.key === 'Enter' && expanded && results[highlighted]) {
      event.preventDefault();
      select(results[highlighted]);
    }
  }

  function clearTerritory() {
    boundaryRequest?.abort();
    pendingPlace = null;
    failedPlace = null;
    onClear();
    input.focus();
  }

  onDestroy(() => boundaryRequest?.abort());
</script>

<div class="territory-search">
  <div class="field">
    <label class="sr-only" for={id}>Pesquisar cidade, estado ou país</label>
    <div class="input-wrap">
      <Search size={18} aria-hidden="true" />
      <input bind:this={input} {id} class="data-control" type="search" role="combobox"
        placeholder="Buscar cidade, estado ou país" value={query} maxlength="120" autocomplete="off"
        aria-autocomplete="list" aria-expanded={expanded} aria-controls={id + '-results'}
        aria-activedescendant={expanded && results[highlighted] ? id + '-result-' + highlighted : undefined}
        oninput={edit} onfocus={() => { open = true; highlightedId = null; }} onblur={() => { open = false; }}
        onkeydown={navigate} />
    </div>
    <div class="popover" hidden={!expanded}>
      <div id={id + '-results'} role="listbox" aria-label="Sugestões de territórios">
        {#each results as place, index (place.id)}
          <button type="button" role="option" tabindex="-1" id={id + '-result-' + index}
            aria-selected={index === highlighted} onmousedown={event => event.preventDefault()}
            onclick={() => select(place)}>
            <span><strong>{place.name}</strong>{#if place.context}<small>{place.context}</small>{/if}</span>
            <span class="kind">{place.label}</span>
          </button>
        {/each}
      </div>
      {#if searching}<p role="status">Buscando locais…</p>
      {:else if searchError}<p role="status">A busca por cidades e estados está indisponível no momento.</p>
      {:else if !results.length}<p role="status">Nenhum território encontrado.</p>{/if}
    </div>
  </div>
  {#if pendingPlace}
    <p class="search-status" role="status">Carregando o contorno de {pendingPlace.name}…</p>
  {:else if failedPlace}
    <p class="search-status" role="status">
      Não foi possível carregar o contorno de {failedPlace.name}.
      <button type="button" class="retry" onclick={() => select(failedPlace)}>Tentar novamente</button>
    </p>
  {/if}
  {#if territory}
    <div class="territory">
      <p aria-live="polite">
        <strong>{territory.name}</strong> <span>· {territory.label}</span>
        <span>· Área aproximada de {areaFormat.format(territory.area)} km²</span>
      </p>
      <button type="button" class="clear" aria-label="Limpar território selecionado" onclick={clearTerritory}>
        <X size={17} aria-hidden="true" />
      </button>
    </div>
  {/if}
</div>

<style>
  .territory-search { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px; }
  .field { position: relative; flex: 1 1 19rem; min-width: 0; }
  .input-wrap { position: relative; }
  .input-wrap :global(svg) { position: absolute; top: 50%; left: 12px; transform: translateY(-50%); color: var(--muted); pointer-events: none; }
  .input-wrap input { width: 100%; min-width: 0; padding-left: 38px; }
  .popover { position: absolute; z-index: 5; top: calc(100% + 5px); inset-inline: 0; max-height: min(42svh, 320px); overflow: auto;
    border: 1px solid var(--border-strong); border-radius: var(--control-radius); background: var(--background); box-shadow: 0 6px 20px #0005; }
  .popover p { padding: 10px 12px; color: var(--muted); font-size: .8rem; }
  .popover button { display: flex; align-items: center; justify-content: space-between; gap: 8px; width: 100%;
    min-height: 48px; padding: 10px 12px; border: 0; color: var(--text); background: transparent; text-align: left; cursor: pointer; }
  .popover button:hover, .popover button[aria-selected='true'] { background: var(--accent-surface); }
  .popover strong { display: block; font-size: .95rem; }
  .popover small, .kind, .territory p span, .search-status { color: var(--muted); font-size: .76rem; }
  .kind { flex: none; }
  .territory { display: flex; align-items: center; gap: 6px; border: 1px solid var(--accent-border);
    border-radius: var(--control-radius); padding: 4px 6px 4px 10px; background: var(--accent-surface); font-size: .85rem; }
  .territory p { margin: 0; }
  .clear { display: grid; flex: none; place-items: center; width: 28px; height: 28px; padding: 0; border: 0;
    border-radius: var(--control-radius); background: transparent; color: var(--muted); cursor: pointer; }
  .clear:hover { background: var(--background); color: var(--text); }
  .retry { padding: 0; border: 0; color: var(--accent); background: transparent; text-decoration: underline; cursor: pointer; }
</style>

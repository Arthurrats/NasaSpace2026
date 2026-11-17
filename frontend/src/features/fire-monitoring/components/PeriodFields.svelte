<script>
  let { start = $bindable(), end = $bindable(), first = '2025-01-01', last = '2025-12-31' } = $props();
  const presets = [
    { label: 'Ano completo', from: '2025-01-01', to: '2025-12-31' },
    { label: 'Janeiro a março', from: '2025-01-01', to: '2025-03-31' },
    { label: 'Abril a junho', from: '2025-04-01', to: '2025-06-30' },
    { label: 'Julho a setembro', from: '2025-07-01', to: '2025-09-30' },
    { label: 'Outubro a dezembro', from: '2025-10-01', to: '2025-12-31' },
  ];
  const preset = $derived(presets.find(item => item.from === start && item.to === end)?.label ?? '');

  function pickPreset(event) {
    const choice = presets.find(item => item.label === event.currentTarget.value);
    if (choice) {
      start = choice.from;
      end = choice.to;
    }
  }
</script>

<fieldset class="fields" aria-label="Período de 2025">
  <label>Período
    <select class="data-control" value={preset} onchange={pickPreset}>
      <option value="" disabled>Personalizado</option>
      {#each presets as item (item.label)}<option value={item.label}>{item.label}</option>{/each}
    </select>
  </label>
  <label>Data inicial <input class="data-control" type="date" min={first} max={end || last} bind:value={start} required /></label>
  <label>Data final <input class="data-control" type="date" min={start || first} max={last} bind:value={end} required /></label>
</fieldset>

<style>
  .fields { display: flex; flex-wrap: wrap; gap: 10px; min-width: 0; margin: 0; padding: 0; border: 0; }
  .fields label { display: grid; min-width: 0; gap: 6px; color: var(--muted); font-size: .86rem; }
</style>

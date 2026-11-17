<script>
  let { days } = $props();
  const weekdays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
  const formatMonth = new Intl.DateTimeFormat('pt-BR', { month: 'short', timeZone: 'UTC' });
  const formatAverage = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
  const compact = new Intl.NumberFormat('pt-BR', { notation: 'compact', maximumFractionDigits: 1 });

  const months = $derived.by(() => {
    const groups = new Map();
    for (const { start_date, detections } of days) {
      const date = new Date(start_date + 'T00:00:00Z');
      const month = start_date.slice(0, 7);
      const weekday = (date.getUTCDay() + 6) % 7;
      if (!groups.has(month)) groups.set(month, weekdays.map(() => ({ total: 0, count: 0 })));
      const cell = groups.get(month)[weekday];
      cell.total += detections;
      cell.count++;
    }
    return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([month, cells]) => ({
      month,
      label: formatMonth.format(new Date(month + '-01T00:00:00Z')).replace('.', ''),
      averages: cells.map(({ total, count }) => count ? total / count : null),
    }));
  });
  const peak = $derived(Math.max(0, ...months.flatMap(({ averages }) => averages)));
</script>

{#if peak > 0}
  <!-- svelte-ignore a11y_no_noninteractive_tabindex (Keyboard users need to focus the scrollable table region.) -->
  <div class="heatmap-scroll" role="region" aria-label="Grade por mês e dia da semana" tabindex="0">
    <table aria-label="Média diária de detecções por mês e dia da semana">
      <thead>
        <tr>
          <td></td>
          {#each months as { month, label } (month)}<th scope="col">{label}</th>{/each}
        </tr>
      </thead>
      <tbody>
        {#each weekdays as weekday, index (weekday)}
          <tr>
            <th scope="row">{weekday}</th>
            {#each months as { month, averages } (month)}
              {@const value = averages[index]}
              <td class:missing={value === null} style:--strength={Math.round(40 * Math.sqrt((value ?? 0) / peak)) + '%'}
                title={value === null ? 'Dia fora do recorte' : formatAverage.format(value) + ' focos por dia'}>
                <span aria-hidden="true">{value === null ? '–' : compact.format(value)}</span>
                <span class="sr-only">{value === null ? 'Dia fora do recorte' : formatAverage.format(value) + ' focos por dia'}</span>
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  <div class="scale"><span>0</span><span class="ramp" aria-hidden="true"></span><span>{formatAverage.format(peak)} focos por dia</span></div>
{:else}
  <p class="empty-state">Sem detecções no período selecionado.</p>
{/if}

<style>
  .heatmap-scroll { position: relative; margin-inline: 12px; overflow-x: auto; border-radius: var(--control-radius); }
  .heatmap-scroll:focus-visible { outline-offset: 0; }
  table { width: 100%; border-spacing: 3px; white-space: nowrap; font-size: .72rem; font-variant-numeric: tabular-nums; }
  th { padding: 3px 2px; color: var(--muted); font-weight: 600; text-align: center; }
  th[scope='row'] { padding-right: 4px; text-align: left; }
  .heatmap-scroll tbody td {
    min-width: 28px;
    padding: 4px 3px;
    border-radius: 4px;
    background: color-mix(in srgb, var(--accent) var(--strength), var(--surface-raised));
    color: var(--text);
    text-align: center;
  }
  .heatmap-scroll tbody .missing { background: var(--background); color: var(--muted); }
  .scale { display: flex; flex-wrap: wrap; align-items: center; justify-content: end; gap: 6px; padding: 6px 15px 0; color: var(--muted); font-size: .72rem; }
  .ramp { width: 64px; height: 6px; border-radius: 4px; background: linear-gradient(90deg, var(--surface-raised), color-mix(in srgb, var(--accent) 40%, var(--surface-raised))); }
</style>

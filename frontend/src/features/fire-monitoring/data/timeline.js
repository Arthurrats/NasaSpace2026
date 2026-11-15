const dateFormat = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC', day: '2-digit', month: 'short', year: 'numeric' });

export function periodLabel(startDate, endDate) {
  const start = Date.parse(startDate);
  return startDate === endDate ? dateFormat.format(start) : dateFormat.formatRange(start, Date.parse(endDate));
}

export async function loadTimeline(startDate, endDate, step, signal) {
  const params = new URLSearchParams({ start_date: startDate, end_date: endDate, step });
  const response = await fetch('/api/map/timeline?' + params, { signal });
  if (!response.ok) throw new Error('Não foi possível consultar os quadros do timelapse.');
  const { frames } = await response.json();
  return frames.map(({ start_date: startDate, end_date: endDate }) => ({ startDate, endDate, label: periodLabel(startDate, endDate) }));
}

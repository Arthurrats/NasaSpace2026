import { createQuery } from './query.js';

const dateFormat = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC', day: '2-digit', month: 'short', year: 'numeric' });

export function periodLabel(startDate, endDate) {
  const start = Date.parse(startDate);
  return startDate === endDate ? dateFormat.format(start) : dateFormat.formatRange(start, Date.parse(endDate));
}

const queryTimeline = createQuery(async (search, signal) => {
  const response = await fetch('/api/map/timeline?' + search, { signal });
  if (!response.ok) throw new Error('Não foi possível consultar os quadros do timelapse.');
  const { frames } = await response.json();
  return frames.map(({ start_date: startDate, end_date: endDate }) => ({ startDate, endDate, label: periodLabel(startDate, endDate) }));
});

export function timelineQuery(startDate, endDate, step) {
  const params = new URLSearchParams({ start_date: startDate, end_date: endDate, step });
  return queryTimeline(params.toString());
}

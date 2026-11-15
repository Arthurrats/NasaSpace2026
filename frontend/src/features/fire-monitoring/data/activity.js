export const formatCount = new Intl.NumberFormat('pt-BR');
export const formatMetric = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
export const formatDay = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', timeZone: 'UTC' });
export const formatDate = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium', timeZone: 'UTC' });
const formatMonth = new Intl.DateTimeFormat('pt-BR', { month: 'long', timeZone: 'UTC' });
export const monthName = (month) => formatMonth.format(Date.UTC(2025, month - 1));
export const fromDate = (day) => new Date(day + 'T00:00:00Z');

export async function loadActivity({ country, sensor, bounds, year }, signal) {
  const search = new URLSearchParams({ country, sensor });
  if (bounds) search.set('bbox', bounds.flat().join(','));
  if (year != null) search.set('year', year);
  const response = await fetch('/api/activity?' + search, { signal });
  if (!response.ok) throw new Error('A consulta de atividade falhou.');
  const activity = await response.json();
  if (!Array.isArray(activity.days) || !Array.isArray(activity.months) || !Array.isArray(activity.seasonal?.months)) throw new Error('Formato de atividade inválido.');
  return { ...activity, revision: response.headers.get('ETag') };
}

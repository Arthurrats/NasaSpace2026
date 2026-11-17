import { regions } from './demo.js';
import { createQuery } from './query.js';

const queryCountries = createQuery(async (url, signal) => {
  const response = await fetch(url, { signal });
  if (!response.ok) throw new Error('Não foi possível carregar a lista de países.');
  const { countries } = await response.json();
  if (!Array.isArray(countries)) throw new Error('A API retornou uma lista de países inválida.');
  return countries;
});

export const countriesQuery = queryCountries('/api/countries');

const querySummary = createQuery(async (search, signal) => {
  const response = await fetch('/api/summary?' + search, { signal });
  if (!response.ok) throw new Error('A API não conseguiu consultar o conjunto selecionado.');
  const data = await response.json();
  if (!Array.isArray(data.by_country) || !Array.isArray(data.by_sensor) || !Array.isArray(data.by_intensity)
    || !['day', 'week', 'month'].every(step => Array.isArray(data.series?.[step]))
    || !Array.isArray(data.monthly_comparison?.country) || !Array.isArray(data.monthly_comparison?.sensor)
    || (new URLSearchParams(search).has('sector') && !Array.isArray(data.by_sector))) {
    throw new Error('A API retornou um resumo em formato inválido.');
  }
  return data;
});

export function summaryQuery({ sensor, country, startDate, endDate, sector, countryOnly }) {
  const params = new URLSearchParams({ sensor, country, start_date: startDate, end_date: endDate, bbox: regions.southAmerica.bounds.flat().join(',') });
  if (countryOnly) params.set('sector', sector);
  else params.set('grid', '1');
  return querySummary(params.toString());
}

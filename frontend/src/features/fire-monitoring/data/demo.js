import nw from './quadrants/nw.json';
import ne from './quadrants/ne.json';
import sw from './quadrants/sw.json';
import se from './quadrants/se.json';

export const countries = {
  brazil: { name: 'Brasil', bounds: [[-75, -35], [-32, 6]], total: 462 },
  argentina: { name: 'Argentina', bounds: [[-75, -56], [-52, -21]], total: 318 },
  bolivia: { name: 'Bolívia', bounds: [[-70, -24], [-57, -9]], total: 216 },
  colombia: { name: 'Colômbia', bounds: [[-80, -5], [-65, 14]], total: 154 },
  paraguay: { name: 'Paraguai', bounds: [[-64, -28], [-53, -18]], total: 134 },
};

export const regions = {
  southAmerica: { name: 'América do Sul', bounds: [[-84, -57], [-31, 15]] },
  ...countries,
};

export const hotspots = [...nw, ...ne, ...sw, ...se];

export const regionalActivity = Object.entries(countries).map(([id, { name, total }]) => ({
  id,
  label: name,
  value: total,
}));

const totalHotspots = regionalActivity.reduce((total, { value }) => total + value, 0);

export const metrics = [
  { id: 'hotspots', label: 'Focos de calor', value: totalHotspots.toLocaleString('pt-BR'), detail: 'Total no período' },
  { id: 'regions', label: 'Países no comparativo', value: regionalActivity.length, detail: 'Cobertura de exemplo' },
  { id: 'critical', label: 'Alta intensidade', value: '216', detail: 'Focos no período' },
];

export const dailyActivity = Array.from({ length: 90 }, (_, index) => ({
  label: index % 7 === 0 ? 'Seg' : index % 7 === 6 ? 'Dom' : 'D' + (index + 1),
  value: [92, 149, 137, 212, 183, 268, 243][index % 7],
}));

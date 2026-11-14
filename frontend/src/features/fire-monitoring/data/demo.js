export const regions = {
  world: { name: 'Visão global', bounds: null },
  local: { name: 'Minha região · Brasil (exemplo)', bounds: [[-83, -38], [-25, 14]] },
  americas: { name: 'América do Sul', bounds: [[-92, -60], [-28, 16]] },
  africa: { name: 'África', bounds: [[-26, -39], [60, 40]] },
  oceania: { name: 'Austrália', bounds: [[109, -46], [161, -8]] },
};

export const hotspots = [
  { name: 'Califórnia', coordinates: [-120, 37], intensity: 'high' },
  { name: 'Canadá', coordinates: [-113, 57], intensity: 'medium' },
  { name: 'México', coordinates: [-101, 22], intensity: 'low' },
  { name: 'Colômbia', coordinates: [-73, 6], intensity: 'low' },
  { name: 'Acre', coordinates: [-68, -10], intensity: 'medium' },
  { name: 'Pará', coordinates: [-53, -5], intensity: 'high' },
  { name: 'Mato Grosso', coordinates: [-57, -13], intensity: 'high' },
  { name: 'Tocantins', coordinates: [-48, -11], intensity: 'medium' },
  { name: 'Mato Grosso do Sul', coordinates: [-55, -20], intensity: 'medium' },
  { name: 'Goiás', coordinates: [-51, -16], intensity: 'low' },
  { name: 'Bahia', coordinates: [-42, -13], intensity: 'high' },
  { name: 'Paraná', coordinates: [-51, -25], intensity: 'low' },
  { name: 'Bolívia', coordinates: [-65, -18], intensity: 'medium' },
  { name: 'Argentina', coordinates: [-63, -32], intensity: 'low' },
  { name: 'Portugal', coordinates: [-8, 40], intensity: 'medium' },
  { name: 'Grécia', coordinates: [23, 39], intensity: 'low' },
  { name: 'Argélia', coordinates: [5, 34], intensity: 'medium' },
  { name: 'Gana', coordinates: [-1, 9], intensity: 'low' },
  { name: 'Congo', coordinates: [23, -4], intensity: 'high' },
  { name: 'Angola', coordinates: [17, -12], intensity: 'high' },
  { name: 'Moçambique', coordinates: [35, -15], intensity: 'medium' },
  { name: 'Sibéria', coordinates: [100, 57], intensity: 'medium' },
  { name: 'Laos', coordinates: [104, 18], intensity: 'high' },
  { name: 'Bornéu', coordinates: [113, 0], intensity: 'medium' },
  { name: 'Austrália Ocidental', coordinates: [122, -20], intensity: 'low' },
  { name: 'Território do Norte', coordinates: [134, -17], intensity: 'medium' },
  { name: 'Queensland', coordinates: [147, -23], intensity: 'high' },
];

export const metrics = [
  { id: 'hotspots', label: 'Focos de incêndio', value: '1.284', detail: 'Total no período' },
  { id: 'regions', label: 'Regiões no comparativo', value: '05', detail: 'Cobertura de exemplo' },
  { id: 'critical', label: 'Alta intensidade', value: '216', detail: 'Focos no período' },
];

export const dailyActivity = [
  { label: 'Seg', value: 92 }, { label: 'Ter', value: 149 },
  { label: 'Qua', value: 137 }, { label: 'Qui', value: 212 },
  { label: 'Sex', value: 183 }, { label: 'Sáb', value: 268 },
  { label: 'Dom', value: 243 },
];

export const regionalActivity = [
  { label: 'América do Sul', value: 462 },
  { label: 'África', value: 318 },
  { label: 'Ásia', value: 216 },
  { label: 'Oceania', value: 154 },
  { label: 'Europa', value: 134 },
];

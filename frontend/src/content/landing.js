import { CalendarDays, ChartNoAxesCombined, Flame, MapPin, Microscope, ShieldAlert, Trees, Wind } from '@lucide/svelte';

export const impacts = [
  { icon: Wind, title: 'Fumaça e saúde', detail: 'A fumaça pode viajar longas distâncias e piorar a qualidade do ar mesmo longe da queimada.' },
  { icon: Trees, title: 'Perda de vegetação', detail: 'Os incêndios degradam a vegetação, alteram habitats e afetam a biodiversidade.' },
  { icon: Flame, title: 'Concentração de focos', detail: 'A atividade varia entre regiões e datas. Comparar esses recortes ajuda a identificar concentrações e períodos de pico.' },
];

export const workflow = [
  { icon: MapPin, title: 'Delimite a área', detail: 'Escolha um país, desenhe um retângulo sobre o mapa do Calendário ou informe as coordenadas.' },
  { icon: CalendarDays, title: 'Escolha o período e o sensor', detail: 'Consulte um intervalo de datas com MODIS, VIIRS ou ambos. Use o Timelapse para acompanhar a sequência de detecções.' },
  { icon: ChartNoAxesCombined, title: 'Compare os registros', detail: 'Confronte concentrações, picos diários e diferenças regionais no mapa, nas séries e no calendário.' },
];

export const useCases = [
  { icon: ShieldAlert, title: 'Equipes de alerta', detail: 'Revise datas de maior atividade e identifique áreas para investigar junto a observações oficiais.' },
  { icon: Microscope, title: 'Pesquisa e ensino', detail: 'Explore como o padrão de detecções muda conforme o sensor, o período ou a região.' },
  { icon: Trees, title: 'Gestão territorial', detail: 'Compare setores de um país e identifique meses com maior atividade para orientar o planejamento local.' },
];

export const coverage = [
  { value: '12', label: 'países sul-americanos', detail: 'O acervo organiza as detecções por país e sensor.' },
  { value: '2', label: 'sensores de observação', detail: 'MODIS e VIIRS fornecem registros de focos de calor.' },
  { value: '2025', label: 'ano de referência', detail: 'A plataforma consulta os arquivos Parquet históricos de 2025.' },
];

export const faq = [
  { question: 'O que um foco de calor representa?', answer: 'É uma detecção de calor registrada pelo satélite em uma posição e um instante. Um mesmo incêndio pode gerar várias detecções, e a contagem do painel se refere aos focos registrados.' },
  { question: 'O mapa mostra incêndios em tempo real?', answer: 'A plataforma consulta o acervo histórico local de 2025. Os mapas e gráficos interativos desta página usam amostras ilustrativas identificadas na interface.' },
  { question: 'Como o Previsor calcula as projeções?', answer: 'A projeção diária usa a atividade recente do acervo e estima os 14 dias após a série observada. O cenário sazonal usa a distribuição dos focos do mesmo mês do ano de referência. Ambas as projeções servem à análise exploratória.' },
  { question: 'O que a potência radiativa (FRP) mede?', answer: 'A FRP estima a potência da radiação emitida pelo fogo na área detectada e é expressa em megawatts. Na plataforma, você pode comparar suas medições por período, sensor e região.' },
];

export const landingMapCopy = {
  title: 'Focos na América do Sul',
  sample: 'Amostra ilustrativa',
  area: 'Selecione um recorte de exemplo',
  points: 'Focos ilustrados',
  high: 'Alta intensidade',
};

export const landingDemos = {
  trend: { title: 'Série temporal', detail: 'Alterne o intervalo para comparar os picos de uma série de exemplo.' },
  calendar: { title: 'Calendário de focos', detail: 'Selecione um dia para consultar a contagem. As células mais claras indicam mais detecções na amostra.' },
  regions: { title: 'Comparação regional', detail: 'Escolha um país para consultar o total de exemplo no comparativo.' },
};

export const landingDemoCopy = {
  sample: 'Amostra ilustrativa',
  range: 'Intervalo da amostra',
  days: 'dias',
  detections: 'focos ilustrados',
  day: 'Dia',
  country: 'País em destaque',
  help: 'Explore os recursos',
};

const teamPhotoBase = import.meta.env.BASE_URL + 'team/';
export const groupPhoto = { src: teamPhotoBase + 'team.png', width: 960, height: 1280 };
export const team = [
  { initials: 'AR', name: 'Arthur Rats', photo: teamPhotoBase + 'arthur.png' },
  { initials: 'RR', name: 'RaphaelRates', photo: teamPhotoBase + 'raphael.png' },
  { initials: 'GP', name: 'Guilherme Pinheiro', photo: teamPhotoBase + 'guilherme.png' },
  { initials: 'VH', name: 'Victor Hugo', photo: teamPhotoBase + 'victor.png' },
  { initials: 'JS', name: 'José Sergio', photo: teamPhotoBase + 'sergio.png' },
];
export const landingCopy = {
  heroTitle: 'Focos de calor',
  heroHighlight: 'na América do Sul.',
  heroContext: 'Monitoramento por satélite',
  heroDescription: 'Veja onde a atividade se concentra, compare regiões e investigue como os focos mudam ao longo do tempo com dados de satélite.',
  heroAction: 'Explorar a demonstração',
  heroSecondaryAction: 'Entender os dados',
  problemLabel: 'Impactos',
  problemTitle: 'Os efeitos das queimadas',
  healthSource: 'Ministério da Saúde',
  ibamaSource: 'Ibama',
  featuresLabel: 'Recursos',
  featuresTitle: 'Veja os focos por região e período',
  filterTitle: 'Mapa por país',
  filterDescription: 'Enquadre um país sul-americano e explore a distribuição geográfica das detecções.',
  countryList: 'Países da demonstração',
  trendTitle: 'Evolução diária',
  trendDescription: 'Selecione uma data para observar a contagem e identificar picos na série de exemplo.',
  compareTitle: 'Comparativo entre países',
  compareDescription: 'Compare o volume de detecções entre países no mesmo recorte.',
  workflowTitle: 'Da área de interesse à análise',
  workflowDescription: 'Defina o recorte e investigue os padrões de atividade dos focos.',
  useCasesTitle: 'Como usar a prevIA',
  useCasesDescription: 'O mesmo acervo permite investigar perguntas diferentes sobre o território.',
  coverageTitle: 'O que os dados cobrem',
  coverageDescription: 'A plataforma reúne detecções históricas para comparar regiões e períodos dentro da América do Sul.',
  faqTitle: 'Perguntas frequentes',
  teamLabel: 'Equipe',
  teamTitle: 'Quem desenvolve a prevIA',
  teamDescription: 'Programação, matemática aplicada e análise de dados.',
  teamList: 'Equipe de desenvolvimento',
  closingTitle: 'Explore o histórico de focos',
  closingDescription: 'Use a conta demonstrativa para consultar mapas, séries, calendário e projeções da plataforma.',
  closingAction: 'Entrar na plataforma',
};

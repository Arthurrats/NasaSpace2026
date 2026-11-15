export const dashboardCopy = {
  "label": "OBSERVATÓRIO DE INCÊNDIOS FLORESTAIS",
  "title": "Focos na América do Sul",
  "description": "Compare as detecções sul-americanas por país, sensor e período.",
  "sample": "Dados simulados",
  "metrics": "Indicadores observados",
  "ranking": "Focos por país",
  "rankingDetail": "Comparativo no período",
  "daily": "Evolução diária",
  "dailyDetail": "Detecções mensais no período filtrado",
  "depth": "Comparativo interativo 3D",
  "depthDetail": "Focos observados por país"
};

export const sectorNames = [
  'Noroeste', 'Norte', 'Nordeste', 'Oeste', 'Centro', 'Leste', 'Sudoeste', 'Sul', 'Sudeste',
];

export const sectorMetrics = [
  { key: 'detections', label: 'Detecções' },
  { key: 'active_days', label: 'Dias com detecções', unit: 'dias' },
  { key: 'daily_average', label: 'Detecções por dia ativo' },
  { key: 'frp_mw', label: 'FRP total', unit: 'MW' },
  { key: 'frp_samples', label: 'Detecções com FRP válida' },
  { key: 'mean_frp_mw', label: 'FRP média', unit: 'MW' },
  { key: 'peak_frp_mw', label: 'FRP máxima', unit: 'MW' },
  { key: 'p90_frp_mw', label: 'FRP · percentil 90', unit: 'MW' },
  { key: 'night_pct', label: 'Detecções noturnas', unit: '%' },
  { key: 'high_pct', label: 'Detecções de alta confiança', unit: '%' },
  { key: 'sensors', label: 'Sensores distintos' },
  { key: 'satellites', label: 'Satélites distintos' },
];

export const mapCopy = {
  tileError: 'Alguns blocos do mapa não carregaram.',
  tilesLoading: 'Carregando blocos…',
  timelineRetry: 'Tentar carregar datas novamente',
  timelineLoading: 'Consultando datas do timelapse…',
  "eyebrow": "PLATAFORMA DE MONITORAMENTO",
  "title": "Mapa-múndi de focos",
  "description": "Explore os focos observados na América do Sul. Aproxime o mapa para separar pontos agrupados.",
  "view": "Enquadrar",
  displayMode: 'Visualização',
  heatMetric: 'Medida do calor',
  heatMetrics: [
    { id: 'detections', label: 'Todas as detecções', legend: 'Concentração de detecções' },
    { id: 'frp', label: 'Potência radiativa (FRP)', legend: 'Concentração de FRP acumulada' },
    { id: 'night', label: 'Detecções noturnas', legend: 'Concentração de detecções noturnas' },
    { id: 'high', label: 'Detecções de alta confiança', legend: 'Concentração de detecções de alta confiança' },
  ],
  modes: [
    { id: 'cluster', label: 'Grupos' },
    { id: 'pixel', label: 'Pixels' },
    { id: 'circle', label: 'Círculos' },
    { id: 'heat', label: 'Mapa de calor' },
  ],
  period: 'Período das detecções',
  from: 'De',
  until: 'Até',
  applyPeriod: 'Aplicar período',
  timeline: 'Timelapse de focos',
  timelineStep: 'Intervalo',
  timelineSteps: [
    { id: 'month', label: 'Mensal' },
    { id: 'week', label: 'Semanal' },
    { id: 'day', label: 'Diário' },
  ],
  pauseTimeline: 'Pausar',
  playTimeline: 'Reproduzir',
  exitTimeline: 'Mostrar período completo',
  timelineReady: 'Período completo',
  timelinePosition: 'Posição no timelapse',
  heatTotal: total => total.toLocaleString('pt-BR') + ' detecções no recorte',
  "world": "Visão mundial",
  countries: 'Países da demonstração',
  "sample": "Dados observados · 2025",
  "google": "Mapa-múndi interativo do Google",
  "loading": "Carregando focos…",
  "error": "Falha ao carregar os focos deste recorte.",
  "retry": "Tentar novamente",
  "fallback": "Google Maps indisponível. Exibindo a cartografia local.",
};

export const loginCopy = {
  "eyebrow": "ACESSO DEMONSTRATIVO",
  "title": "Login",
  "description": "Use a conta de demonstração para explorar os focos de calor na América do Sul. A sessão é mantida neste navegador.",
  "account": "Conta demonstração",
  "email": "analista@previa.example",
  "action": "Entrar com conta demo"
};

export const footerCopy = {
  "scope": "Análise de focos de calor na América do Sul.",
  "sample": "A plataforma consulta dados históricos de satélite.",
  "explore": "Explore a prevIA",
  "impacts": "Impactos das queimadas",
  "features": "Recursos de análise",
  "team": "Equipe",
  "contact": "Fale com a equipe",
  "details": "Use o repositório para compartilhar sugestões ou relatar problemas.",
  "contactLink": "Contato pelo GitHub",
  "source": "Código do projeto"
};

export const previewCopy = {
  "title": "Focos de calor na América do Sul",
  "sample": "Dados simulados",
  "points": "Pontos de exemplo no mapa",
  "countries": "Países no comparativo"
};

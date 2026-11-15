# prevIA · Monitoramento de queimadas na América do Sul

A prevIA é um observatório de focos de calor criado para o desafio **Harmonization of MODIS and VIIRS Hot Spots** do NASA Space Apps Challenge. A plataforma reúne detecções de satélite, mapas interativos, comparações históricas e projeções exploratórias. O acervo local atual tem 24 arquivos Parquet de 2025, organizados por sensor e país. [Desafio NASA Space Apps](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/)

## Entrar e navegar

Abra a aplicação, clique em **Login** e selecione **Entrar com conta demo**. O Flask emite um cookie de sessão assinado, com `HttpOnly` e `SameSite=Lax`. O navegador verifica a sessão ao abrir a aplicação. **Sair** encerra a sessão. O acesso é uma demonstração sem credenciais, e as rotas de dados da API são públicas. Ao reiniciar o backend, abra a página novamente e entre se solicitado.

| Página | Rota | O que você pode fazer |
| --- | --- | --- |
| Página inicial | `/#/` | Conhecer a solução, ver amostras ilustrativas, ler sobre impactos e recursos, conhecer a equipe e acessar os links de contato. |
| Login | `/#/login` | Iniciar a sessão demonstrativa e abrir a plataforma. |
| Dashboard | `/#/painel` | Explorar indicadores, séries históricas e comparativos 2D e 3D da América do Sul. |
| Países | `/#/paises` | Comparar até nove setores geográficos de um país e filtrar os indicadores por setor. |
| Mapa de focos | `/#/mapa` | Navegar pela cartografia e alternar entre densidade, grupos, pixels e círculos. |
| Timelapse | `/#/timelapse` | Reproduzir a distribuição de focos ao longo de um período. |
| Previsor | `/#/previsor` | Consultar uma projeção de 14 dias e o cenário espacial mensal do ciclo seguinte. |
| Calendário | `/#/calendario` | Comparar dias e meses, identificar picos e investigar a atividade de uma área de interesse. |

A página inicial abre com um mapa ilustrativo que permite alternar entre a América do Sul e países de exemplo. A seção Recursos permite trocar o intervalo da série temporal, selecionar dias no calendário e destacar um país no comparativo. As demais seções apresentam impactos das queimadas, cobertura do acervo, fluxo de análise, casos de uso, equipe e perguntas frequentes expansíveis.

O cabeçalho acompanha a rolagem e destaca a seção atual. As âncoras movem o foco e usam rolagem suave. As animações ficam restritas à seção no centro da área visível e respeitam a preferência por movimento reduzido. A área interna usa navegação lateral em telas largas e navegação compacta em telas estreitas. Os temas claro e escuro são persistidos no navegador. Os retratos da equipe vêm de `frontend/public/team/`. O espaço da foto de grupo exibe um placeholder. O rodapé oferece links para o repositório e para contato via GitHub. [Guia de design](docs/DESIGN.md)

A [arte orbital do hero](frontend/public/previa-orbita.webp) é uma ilustração produzida com o ImageGen integrado e exportada em WebP.

<details>
<summary>Prompt da arte orbital</summary>

Use case: photorealistic-natural. Generate one wide 16:9 atmospheric background photograph for a premium wildfire-monitoring website. A real-looking near-nadir orbital photograph of tropical South America, with the winding Amazon river and branching dark tributaries, deep forest-green and charcoal terrain, fine satellite-imaging detail, and one very restrained patch of amber heat with wisps of pale smoke on the lower right. The left half is especially dark, low contrast, and open for legible HTML headlines; terrain detail and smoke mainly in the center-right. Satellite editorial photography, subtly desaturated deep petroleum green, no blue sky and no visible horizon. Strong grounded documentary feel, not sci-fi. No borders, words, graphics, marker dots, UI, logos, mountains added to the river basin, or watermarks.

</details>

## Dashboard e análise por país

Selecione o país, o sensor e o período e clique em **Aplicar filtros**. O dashboard e a página de países usam o recorte geográfico sul-americano. O controle de período aceita datas personalizadas e atalhos trimestrais ou anuais.

- **Seis indicadores** acompanham o recorte. São total de focos, FRP acumulada em MW, quantidade de países com detecções no dashboard ou sensores na página de países, média de focos por dia com registros, data e valor do pico diário e mediana da FRP válida.
- **Séries temporais** mostram detecções e FRP acumulada em intervalos diários, semanais ou mensais. A API devolve todas as granularidades na mesma resposta. A semana começa na data inicial escolhida e é dividida em blocos consecutivos de sete dias. Meses e blocos incompletos respeitam a data inicial e a final. Lacunas sem registros entram como zero nas séries dos recortes com detecções. O gráfico horário usa a hora de aquisição em UTC.
- **Comparativos 2D** mostram focos e FRP por sensor, detecções por confiança, dia ou noite, satélite e faixa de FRP. O dashboard também compara FRP por país. A página de países inclui gráficos mensais por sensor. A API ainda oferece quantidade de medições válidas, percentis 90 e 99 e valor máximo de FRP.
- **Comparativos 3D** apresentam detecções e FRP por país e mês em dois gráficos. Cada país com dados usa os mesmos meses do recorte, inclusive meses sem registros. Os controles permitem rotação e zoom.
- **Distribuição geográfica** combina um mapa clicável da América do Sul com um globo 3D texturizado. A API agrega as detecções em células de 0,25° e seleciona até 750 células de maior valor para cada medida. O navegador usa as células ocupadas na textura e uma malha instanciada para as colunas perpendiculares à esfera. No globo, alterne entre detecções e FRP acumulada. [Textura Blue Marble](https://svs.gsfc.nasa.gov/3615)
- **Setores por país** usam uma grade de três por três calculada a partir dos percentis 5 e 95 das coordenadas dos arquivos do país. A análise usa setores geográficos, com nomes como noroeste e sudeste. A seleção de um setor filtra os indicadores e as séries, enquanto o ranking e as bolhas 3D mantêm os demais setores disponíveis para comparação. As doze medidas comparadas são detecções, dias com registros, média por dia ativo, FRP total, quantidade com FRP válida, FRP média, máxima e percentil 90, proporção noturna, proporção de alta confiança, sensores distintos e satélites distintos. As proporções consideram os registros classificados na dimensão correspondente.

FRP é a potência radiativa do fogo. Os totais em MW somam medições individuais. A média dos cartões do Dashboard considera os dias com focos, enquanto a média mensal do Calendário usa todos os dias do mês.

## Mapa de focos e Timelapse

No **Mapa**, abra **Filtros do mapa** para escolher enquadramento, sensor, modo de visualização e período. O recorte principal mostra a América do Sul. O seletor oferece também quadrantes e os países disponíveis nessa tela. Quando configurado, o Google Maps fornece o mapa-base interativo com arraste e zoom. A aplicação oferece cartografia local Natural Earth como alternativa.

| Modo | Como é calculado |
| --- | --- |
| Mapa de calor | Cada detecção contribui com um peso. Escolha contagem de todas as detecções, FRP acumulada, detecções noturnas ou de alta confiança. A API suaviza a concentração atravessando as bordas dos blocos e aplica uma escala comum aos blocos com o mesmo zoom, métrica e duração. |
| Grupos | A API agrega pontos próximos por bloco e nível de zoom. Os grupos são desenhados como círculos de tamanho fixo, sem números sobre os marcadores. |
| Pixels | A API desenha pontos como quadrados pequenos nas coordenadas registradas. |
| Círculos | A API usa marcadores circulares nas posições registradas. |

A legenda acima do mapa descreve a métrica de calor ou a confiança dos marcadores. Verde-limão, laranja e vermelho representam respectivamente baixa, média e alta confiança. Círculos e pixels incluem todas as detecções do recorte solicitado. Pontos muito próximos ou coincidentes podem compartilhar a mesma posição visível.

O Flask gera imagens PNG Web Mercator somente para os blocos pedidos. O navegador usa uma fila de até quatro requisições simultâneas, exibe cada bloco assim que ele chega e cancela requisições descartadas ao mover o mapa, mudar o zoom ou trocar de filtro. Uma consulta compacta obtém a contagem e a revisão dos dados. O Mapa e o Timelapse pausado revalidam o recorte a cada 30 segundos enquanto a página está visível.

No **Timelapse**, selecione o intervalo diário, semanal ou mensal. Os limites inclusivos de cada quadro vêm da API. Use a régua de datas para inspecionar um quadro, **Reproduzir** para avançar automaticamente e **Mostrar período completo** para sair da sequência. A reprodução aguarda os blocos de cada quadro, pausa em caso de falha e preserva o sensor, o recorte e o modo de visualização.

## Calendário de atividade

1. Escolha a América do Sul ou um dos doze países e selecione MODIS, VIIRS ou ambos.
2. Aplique o recorte. Para uma área menor, use **Desenhar área** no mapa e arraste um retângulo, ou ative **Limitar por coordenadas** nos filtros e preencha oeste, sul, leste e norte em graus decimais.
3. Navegue pelos meses com as setas ou com o seletor. Quando houver mais de um ano compatível com o sensor e o país, o seletor de ano fica disponível.
4. Selecione um dia para ver sua contagem, a FRP acumulada e a camada de calor correspondente. Ao abrir um mês, o calendário seleciona o dia de maior atividade.

Os cartões do mês exibem focos detectados, média diária, dias acima do padrão e incêndios notificados. A API divide a intensidade diária em quatro níveis proporcionais ao pico do mês, com um nível separado para dias sem registros. A interface aplica a rampa sequencial Cividis e exibe a contagem em cada célula. Dias fora do padrão recebem borda tracejada e o símbolo `!`. [Referência da rampa Cividis](https://doi.org/10.1371/journal.pone.0199239)

- **Períodos críticos** são até três meses com as maiores médias diárias positivas no recorte do ano.
- **Dia acima do padrão** tem pelo menos dois focos e uma contagem superior ao percentil 90 dos 28 dias anteriores. A classificação exige catorze dias anteriores no período de referência.
- **Comparação histórica** compara cada mês com a média dos totais do mesmo mês em pelo menos dois anos anteriores com arquivos para todos os sensores e países do recorte. Exibe o desvio absoluto e, quando a média é maior que zero, o desvio percentual. A área geográfica é aplicada igualmente a todos os anos.
- **Incêndios notificados** aparecem como **Sem fonte**. Os Parquet locais contêm detecções de satélite e não incluem identificadores de ocorrência ou registros de notificações oficiais. O mesmo incêndio pode produzir várias detecções.

Com o acervo atual, o gráfico mensal e os alertas retrospectivos funcionam em 2025. A comparação plurianual fica indisponível até que haja anos anteriores suficientes. Um dia com zero registros pode incluir lacunas de observação.

## Previsor

As projeções são exploratórias e usam os registros locais da área e do sensor escolhidos. O recorte por desenho ou coordenadas funciona também nesta página. A projeção diária e a sazonal são calculadas no backend.

- **Série diária** projeta os 14 dias seguintes ao fim do ano selecionado. Para cada dia, usa a média das últimas quatro ocorrências do mesmo dia da semana. A faixa empírica usa os percentis 10 e 90 dos erros por horizonte, obtidos ao simular previsões em janelas anteriores. A tela mostra o erro absoluto médio retrospectivo em focos por dia e uma tabela de estimativas com seus limites. A faixa descreve o desempenho no acervo usado.
- **Modelo sazonal** repete a contagem e a distribuição do mesmo mês do ano de referência para o ciclo seguinte. O backend retorna o ano projetado, as datas observadas usadas no mapa e a contagem estimada por mês. A camada desenha pontos pequenos com dados de todas as detecções dentro do recorte e carrega cada bloco separadamente. Pontos próximos podem se sobrepor.

Com o acervo atual, o Previsor usa 2025 e projeta os primeiros 14 dias e o ciclo mensal de 2026. Para operações de alerta e emergência, consulte observações atualizadas e fontes oficiais.

## Dados e arquitetura

| Local | Responsabilidade |
| --- | --- |
| `frontend/` | Svelte 5, Vite e Three.js. Interface, estados de tela, projeção cartográfica, controles, exibição de mapas, gráficos e fila de requisições. Os textos ficam principalmente em `frontend/src/content/`. |
| `backend/app/` | Flask, Pandas, NumPy, PyArrow e Pillow. Validação, leitura dos Parquet, filtros, estatísticas, séries, setores, rankings, calendário, projeções e imagens dos blocos. |
| `dados/parquet/` | Partições por sensor, ano e país. O backend monta esse diretório como somente leitura no Docker. |
| `docs/` | [Contrato HTTP da API](docs/API.md), [guia de design](docs/DESIGN.md), [Docker Compose Watch](docs/DOCKER.md) e [metodologia dos dados e projeções](docs/METODOLOGIA.md). |
| `research/` | Ambiente independente para experimentos em notebooks. [Guia de pesquisa](research/README.md) |

Os países do acervo são Argentina, Bolívia, Brasil, Chile, Colômbia, Equador, Guiana, Paraguai, Peru, Suriname, Uruguai e Venezuela. O identificador do país vem do nome da partição. Os mapas posicionam cada detecção pela latitude e longitude informadas no registro. O Calendário e o Previsor descobrem anos adicionais quando encontram as partições da combinação de país e sensor, seguindo os nomes abaixo. O Dashboard, o Mapa e o Timelapse exibem o período de 2025 na interface atual.

```text
dados/parquet/modis/modis_2025_Brazil.parquet
dados/parquet/viirs/viirs-jpss1_2025_Brazil.parquet
```

O Redis guarda respostas por até 30 minutos. As chaves incluem a rota, os filtros, a versão do código e os metadados dos Parquet. O Flask reutiliza em memória os arquivos e os índices já consultados. Ao substituir um Parquet, a revisão muda e as próximas consultas são recalculadas. O serviço continua lendo os arquivos locais quando o Redis está indisponível. Os blocos podem ser reutilizados pelo navegador por até 30 segundos.

## Executar o projeto

### Docker Compose

Com o Docker em execução, use estes comandos na raiz.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose up --build -d --wait
```

Abra [a aplicação](http://127.0.0.1:8080/) e confira [a saúde da API](http://127.0.0.1:8080/api/health). Se `PORT_FRONTEND` estiver definido no seu `.env`, use essa porta. O Nginx serve o frontend e encaminha `/api/` ao Flask. Para recompilar ao salvar, use `docker compose up --build --watch` em um terminal na raiz. O Compose reconstrói o serviço cuja pasta mudou. [Guia Docker](docs/DOCKER.md)

| Variável | Uso | Padrão |
| --- | --- | --- |
| `PORT_FRONTEND` | Porta local do Nginx no Docker | `8080` |
| `PORT_BACKEND` | Porta local da API no Docker | `5000` |
| `PREVIA_DATA_HOST_DIR` | Pasta Parquet no host | `./dados/parquet` |
| `PREVIA_DATA_DIR` | Raiz Parquet lida pelo Flask | `/data/parquet` no Docker e `dados/parquet` localmente |
| `PREVIA_REDIS_URL` | Endereço do Redis | `redis://redis:6379/0` no Docker |
| `VITE_GOOGLE_MAPS_API_KEY` | Chave do Maps JavaScript API usada no build | Vazia |
| `VITE_GOOGLE_MAP_ID` | Identificador do mapa Google usado no build | `DEMO_MAP_ID` |

Para ativar o Google Maps, configure a chave e reconstrua o frontend. Como o Vite inclui a chave no código enviado ao navegador, a configuração da chave deve restringir seu uso aos domínios e à API do projeto. A cartografia local fica disponível sem chave.

### Desenvolvimento local sem Docker

Inicie o Flask em um terminal a partir da raiz.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run --debug
```

Em outro terminal, use Node.js 20.19+ na linha 20 ou 22.12+.

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Abra [o Vite](http://localhost:5173/). Ele encaminha `/api/` à porta local 5000 do Flask. Para usar o Google Maps no Vite, defina as variáveis `VITE_*` no ambiente do processo ou em `frontend/.env.local`. Rode `npm.cmd run build` para gerar `frontend/dist/`.

### Consultas rápidas à API

| Rota | Resposta |
| --- | --- |
| `GET /api/health` | Estado do processo Flask |
| `GET /api/demo-session`, `POST /api/demo-session`, `DELETE /api/demo-session` | Consulta, início e encerramento do acesso demonstrativo |
| `GET /api/countries` | Códigos e nomes dos países |
| `GET /api/fires` | Registros individuais com filtros e paginação de até 5.000 detecções por página |
| `GET /api/summary` | Indicadores, séries temporais, comparativos e rankings para Dashboard e Países |
| `GET /api/activity` | Calendário diário e mensal, comparação plurianual e duas projeções |
| `GET /api/map/foci` | Contagem, revisão e formatos compactos de detecções |
| `GET /api/map/tiles/{mode}/{zoom}/{x}/{y}.png` | Imagem de cada bloco da camada |
| `GET /api/map/timeline` | Limites inclusivos dos quadros do Timelapse |

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
Invoke-RestMethod 'http://127.0.0.1:5000/api/summary?country=brasil&sensor=modis'
Invoke-RestMethod 'http://127.0.0.1:5000/api/activity?country=argentina&year=2025'
Invoke-RestMethod 'http://127.0.0.1:5000/api/map/timeline?start_date=2025-08-01&end_date=2025-08-31&step=week'
```

Veja rotas, filtros, formatos de resposta, erros e convenções no [contrato da API](docs/API.md).

### Ambiente independente de pesquisa

Para iniciar apenas o JupyterLab pelo Compose, execute `docker compose up --build -d --wait research`. Consulte o token em `docker compose logs research` e abra [o JupyterLab](http://127.0.0.1:8888/lab). Os notebooks ficam em `research/notebooks/`. [Guia de pesquisa](research/README.md)

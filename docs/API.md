# API do PrevIA

Este documento descreve o contrato HTTP do backend da prevIA. A API lê os arquivos Parquet locais em `dados/parquet/{modis,viirs}`. O conjunto atual cobre detecções de 2025 nos doze países da América do Sul. As observações, as comparações históricas e as projeções exploratórias têm campos separados.

## Execução e configuração

Na raiz do repositório, configure as variáveis necessárias em `.env` (use `.env.example` como referência) e execute `docker compose up --build`. O Compose monta `dados/parquet` como somente leitura no backend e define `PREVIA_DATA_DIR=/data/parquet`.

| Variável | Uso | Padrão |
| --- | --- | --- |
| `PREVIA_DATA_DIR` | Diretório que contém as pastas `modis` e `viirs` | `dados/parquet` localmente; `/data/parquet` no Compose |
| `PREVIA_DATA_HOST_DIR` | Diretório Parquet no host montado pelo Docker | `./dados/parquet` |
| `PREVIA_REDIS_URL` | Endereço do cache Redis | `redis://redis:6379/0` no Compose |
| `PORT_BACKEND` | Porta local publicada para a API | `5000` |
| `PORT_FRONTEND` | Porta local publicada para o frontend | `8080` |
| `VITE_GOOGLE_MAPS_API_KEY` | Chave usada pelo mapa do Google no frontend | vazia; o mapa alternativo continua disponível |
| `VITE_GOOGLE_MAP_ID` | Map ID do Google Maps | `DEMO_MAP_ID` |

A API fica disponível em `http://localhost:${PORT_BACKEND:-5000}/api`. O frontend já encaminha `/api` ao backend.

## Cache e atualização dos Parquet

O Redis guarda por até 30 minutos as respostas de `/api/fires`, `/api/map/foci`, `/api/map/tiles/…`, `/api/activity` e `/api/summary`. A chave inclui a rota, os filtros, a versão do código e os metadados dos arquivos. A API compara tamanho, data de modificação, data de mudança de metadados e identificador do arquivo a cada consulta. Se um Parquet mudar, a API recalcula a resposta e atualiza a leitura em memória. Para atualizar o conjunto, substitua cada arquivo pelo novo Parquet completo, de preferência por uma troca atômica.

O Redis é interno ao Compose e pode descartar entradas quando atingir o limite de 128 MB. Se estiver indisponível, o backend continua atendendo a partir dos Parquet. O navegador revalida com `ETag`; a API pode responder `304` para uma resposta sem alterações.

## Convenções

- As rotas de dados são públicas. Usam `GET` e respondem em JSON, com imagens PNG na rota de blocos. A sessão demonstrativa também aceita `POST` e `DELETE`.
- Datas seguem `YYYY-MM-DD`, incluindo os limites `start_date` e `end_date`.
- `sensor` aceita `all`, `modis` ou `viirs` (arquivos VIIRS JPSS-1).
- `country` aceita `all`, um nome em inglês ou slug: `argentina`, `bolivia`, `brasil`, `chile`, `colombia`, `equador`, `guiana`, `paraguai`, `peru`, `suriname`, `uruguai` ou `venezuela`.
- `bbox` usa `oeste,sul,leste,norte` em graus decimais. Uma caixa que cruza o antimeridiano também é aceita.
- Coordenadas seguem graus decimais. O campo `coordinates` usa a ordem `[longitude, latitude]` (GeoJSON); `latitude` e `longitude` também são fornecidos separadamente.
- FRP é a potência radiativa do fogo, expressa em MW. O total é uma soma de detecções, não área queimada.

## Rotas

### `GET /api/health`

Verifica se o processo está ativo. Não verifica se os Parquet estão íntegros.

Resposta `200`:

```json
{"status":"ok"}
```

### `GET /api/countries`

Lista os países que possuem arquivos de dados.

Resposta `200`:

```json
{"countries":[{"id":"argentina","name":"Argentina","iso3":"ARG"},{"id":"brasil","name":"Brazil","iso3":"BRA"}]}
```

O exemplo foi abreviado. A lista completa inclui Argentina, Bolívia, Brasil, Chile, Colômbia, Equador, Guiana, Paraguai, Peru, Suriname, Uruguai e Venezuela.

### `GET /api/demo-session`, `POST /api/demo-session` e `DELETE /api/demo-session`

`GET` verifica o cookie, `POST` com corpo JSON `{}` inicia a demonstração e `DELETE` encerra a sessão. Todos retornam `200` e `{"active":true}` ou `{"active":false}`. A resposta usa `Cache-Control: no-store`. O Flask assina o cookie `previa_demo` com uma chave gerada no início do processo. O cookie usa `HttpOnly` e `SameSite=Lax`. A sessão serve para a navegação demonstrativa do frontend.

### `GET /api/fires`

Retorna detecções, com paginação, filtros de sensor, país, data e caixa geográfica.

| Parâmetro | Tipo | Padrão | Descrição |
| --- | --- | --- | --- |
| `sensor` | texto | `all` | `all`, `modis` ou `viirs` |
| `country` | texto | `all` | País ou slug aceito acima |
| `start_date` | data | — | Data inicial inclusiva |
| `end_date` | data | — | Data final inclusiva |
| `bbox` | quatro números | — | `oeste,sul,leste,norte` |
| `limit` | inteiro | `1000` | Registros por página, de 1 a 5000 |
| `offset` | inteiro | `0` | Deslocamento, não negativo |

Exemplo: `/api/fires?sensor=viirs&country=brasil&start_date=2025-08-01&end_date=2025-08-31&bbox=-75,-35,-32,6&limit=1000`

Resposta `200` (exemplo abreviado):

```json
{
  "data": [{
    "latitude": -10.2,
    "longitude": -55.4,
    "coordinates": [-55.4, -10.2],
    "date": "2025-08-12",
    "time": 1430,
    "country": "Brazil",
    "sensor": "VIIRS",
    "satellite": "NOAA-21",
    "confidence": "h",
    "frp_mw": 4.8,
    "daynight": "D",
    "type": 0,
    "intensity": "high"
  }],
  "pagination": {"limit": 1000, "offset": 0, "total": 1, "has_more": false},
  "meta": {"synthetic": false, "sensors": ["VIIRS"], "unit": "satellite detections"}
}
```

`intensity` normaliza a confiança para `high`, `medium` ou `low`. A confiança de VIIRS usa categorias de letras; a de MODIS usa valores numéricos. Essa normalização é apenas para visualização e não torna as escalas diretamente comparáveis.

### `GET /api/map/foci`

Consulta compacta de detecções. Aceita `bbox` (mundo inteiro quando omitido), `country` e `sensor` (`all` por padrão), além de `start_date` e `end_date` (opcionais e inclusivas). O recorte inclui as bordas e aceita caixas que atravessam o antimeridiano. Use `clip=oeste,sul,leste,norte` para intersectar a área visível com um recorte fixo que não atravesse o antimeridiano.

Cada entrada de `data` começa com `[id, longitude, latitude, intensidade, contagem]`. Até 480 detecções, cada entrada representa um ponto. Em recortes maiores, o modo padrão agrupa detecções por proximidade. O parâmetro legado `markers=points` retorna uma amostra. O painel usa a rota de blocos para mostrar todos os círculos e pixels, e `format=count` para obter a contagem total e a revisão dos dados. Com `layer=heat`, o formato JSON legado usa uma grade de 192 × 144 células.

Com `layer=heat&format=grid`, recortes acima de 480 detecções retornam `grid` em vez de `data`. A grade de 512 × 384 acumula cada registro do recorte e envia apenas as células com peso positivo. `bins` é Base64 com registros de oito bytes em ordem little-endian, cada um com índice `uint32` e peso `float32`. O índice cresce do oeste para o leste, começando na linha mais ao sul. A origem é `west` e `south`. Os passos em graus são `lng_step` e `lat_step`. Recortes menores continuam retornando as coordenadas individuais em `data`.

A interface usa `format=count` para obter `total` e `revision`. A camada de focos e calor é servida como blocos PNG. O Mapa e o Timelapse pausado revalidam o recorte a cada 30 segundos enquanto a página está visível.

Em `layer=heat`, `metric` define o peso da camada e acrescenta um sexto elemento em cada tupla. Use `detections` (padrão), `frp` (soma em MW), `night` (contagem noturna) ou `high` (contagem de alta confiança). A contagem original e o total do recorte são mantidos.

### `GET /api/map/tiles/{mode}/{zoom}/{x}/{y}.png`

Retorna um PNG transparente para um bloco Web Mercator de 256 pixels lógicos. O nível de zoom aceito vai de 0 a 22. Os modos `circle` e `pixel` desenham todas as detecções no bloco em imagens de 512 × 512. Quando símbolos se sobrepõem, o desenho preserva a confiança mais alta. No modo `cluster`, os grupos são calculados por bloco e zoom com círculos de tamanho fixo. As bordas incluem marcadores vizinhos que cruzam o limite.

`heat` retorna uma imagem de 256 × 256 com densidade ponderada. Aceita `metric=detections|frp|night|high` e `palette=default|accessible`. A opção `accessible` usa a rampa Cividis. O cálculo inclui margem geográfica ao redor do bloco e usa a mesma escala em todo o mapa para um mesmo zoom, métrica e duração do intervalo. `dots` desenha círculos de aproximadamente 2 pixels lógicos usando todas as posições do recorte, com `bbox` para aplicar o limite geográfico. É a camada usada pelo mapa sazonal do Previsor.

Aceita filtros de país, sensor e datas, além de `clip` para delimitar a camada. O navegador reutiliza imagens por até 30 segundos. A interface inclui `v` com a revisão ou o ETag da consulta de dados para trocar os blocos ao detectar mudanças.

### `GET /api/map/timeline`

Requer `start_date` e `end_date` inclusivos, com até 367 dias. `step` aceita `day`, `week` ou `month`, com padrão `month`. A resposta traz `frames`, uma lista ordenada de objetos `{start_date, end_date}`. Semanas são blocos de sete dias a partir da data inicial. Meses acompanham a virada do mês civil. O primeiro e o último bloco respeitam o recorte informado.

### `GET /api/activity`

Fornece Calendário e Previsor. Aceita `country`, `sensor`, `bbox` sem cruzamento do antimeridiano e `year`. O recorte é intersectado com a América do Sul. Sem `year`, seleciona o ano mais recente que tenha os arquivos requeridos para todos os países e sensores do filtro. Retorna `400` para um ano que não esteja nessa lista e `503` quando não houver acervo compatível.

| Campo | Conteúdo |
| --- | --- |
| `year`, `first_date`, `last_date`, `available_years` | Ano selecionado, datas inclusivas e inventário compatível. |
| `days` | Data, detecções, FRP em MW, `unusual` e `intensity_level` de 0 a 4, relativo ao pico do mês. |
| `months` | Total, média diária, `critical`, `start_date`, `end_date`, `peak_date`, `unusual_days`, notificações e comparação histórica. |
| `baseline_years`, `baseline_average`, `anomaly`, `anomaly_pct` | Anos de referência e valores por mês. Requer pelo menos dois anos anteriores compatíveis. Diferença percentual fica nula se a média for zero. |
| `total_detections`, `reported_incidents`, `bounds` | Total anual, notificações oficiais e limites sugeridos do mapa. Notificações são nulas com o acervo atual. |
| `forecast` | `training_days`, `evaluation_windows`, `mae` e estimativas diárias com `date`, `estimate`, `lower` e `upper`. Nulo para recorte sem detecções. |
| `seasonal` | `year`, `reference_year`, `method=seasonal_naive` e meses com `estimate`, `reference_start_date` e `reference_end_date`. |

Veja os cálculos, a cobertura e a relação com a proposta original na [metodologia da prevIA](METODOLOGIA.md).

### `GET /api/summary`

Aplica os filtros `sensor`, `country`, `start_date`, `end_date` e `bbox` aos Parquet. A API calcula todos os indicadores e agrupamentos durante a mesma requisição e devolve o resultado completo em uma única resposta.

`by_hour` agrupa horários de aquisição válidos em UTC. `by_frp_band` agrupa potências em cinco faixas com cortes em 10, 50, 100 e 500 MW. `frp_distribution` retorna a quantidade de medições válidas, a mediana, os percentis 90 e 99 e o máximo.

`series.day`, `series.week` e `series.month` retornam janelas com `start_date`, `end_date`, `detections` e `frp_mw`. Para um recorte com dados, as janelas sem detecções têm valor zero. `monthly_comparison.country` e `monthly_comparison.sensor` contêm as matrizes de cada país ou sensor observado por mês, com zero nas lacunas. Os agrupamentos históricos `by_day`, `by_month`, `by_country_month` e `by_sensor_month` continuam disponíveis.

Com `grid=1`, `grid` inclui as células ocupadas na grade mundial de 0,25° em tuplas `[índice, detecções, frp_mw]`. O índice linear começa no noroeste e a grade tem 1.440 colunas. `grid_rankings.detections` e `grid_rankings.frp_mw` identificam até 750 células com os maiores valores positivos em cada medida. O dashboard inclui todas as células na textura e usa uma malha instanciada para as colunas selecionadas. [Textura Blue Marble](https://svs.gsfc.nasa.gov/3615)

Ao selecionar um país, `by_sector` compara até nove setores geográficos numerados de 0 a 8, do noroeste ao sudeste. Os cortes dividem em terços, por eixo, a faixa entre os percentis 5 e 95 das coordenadas dos Parquet do país. Pontos extremos entram nos setores externos. Os cortes ficam fixos ao mudar sensor ou período. `sector=0` a `8` filtra os indicadores e as séries do painel e mantém `by_sector` como referência para comparar todos os setores. A divisão se baseia nas coordenadas, sem limites administrativos.

Cada setor inclui contagem de detecções, dias ativos, média por dia ativo, FRP total, média, máxima, percentil 90 e quantidade de medições válidas de FRP, além de percentuais noturno e de alta confiança e contagem de sensores e satélites distintos. Os percentuais usam apenas as detecções classificadas na respectiva dimensão. Valores indisponíveis são representados por `null`. `sector_rankings` lista os IDs de setores ordenados por valor para cada medida.

Exemplo: `/api/summary?sensor=modis&country=brasil&start_date=2025-01-01&end_date=2025-12-31`

Resposta `200`:

```json
{
  "filters": {"sensor": "modis", "country": "brasil"},
  "total_detections": 12345,
  "total_frp_mw": 67890.1,
  "average_daily_detections": 40.2,
  "peak_day": {"date": "2025-08-12", "detections": 260},
  "by_country": [{"country": "Brazil", "detections": 12345, "frp_mw": 67890.1}],
  "by_day": [{"date": "2025-08-12", "detections": 42, "frp_mw": 840.3}],
  "by_month": [{"month": "2025-08", "detections": 1200, "frp_mw": 6200.4}],
  "by_country_month": [{"country": "Brazil", "month": "2025-08", "detections": 1200, "frp_mw": 6200.4}],
  "by_sensor_month": [{"sensor": "MODIS", "month": "2025-08", "detections": 1200, "frp_mw": 6200.4}],
  "by_sensor": [{"sensor": "MODIS", "detections": 12345, "frp_mw": 67890.1}],
  "by_intensity": [{"intensity": "high", "detections": 1840}],
  "by_daynight": [{"period": "day", "detections": 6700}],
  "by_satellite": [{"satellite": "Aqua", "detections": 3400}],
  "meta": {"synthetic": false, "sensors": ["MODIS"], "unit": "satellite detections"}
}
```

`average_daily_detections` usa os dias com registros no recorte. `peak_day` identifica a maior contagem diária. Os agrupamentos por país e mês e por sensor e mês incluem contagem e soma dos valores válidos de FRP. `by_daynight` distingue `day`, `night` e `unknown`. Em `by_satellite`, `unknown` indica que o Parquet não identificou o satélite. As classes `high`, `medium` e `low` resumem as escalas de confiança dos sensores para visualização.

## Erros

Erros usam `{ "error": { "code": "...", "message": "..." } }`.

| Status | Código | Quando |
| --- | --- | --- |
| `400` | `invalid_request` | Sensor, país, datas, caixa geográfica ou paginação inválidos |
| `404` | `not_found` | Rota não encontrada |
| `500` | `internal_error` | Erro inesperado no processamento |
| `503` | `service_unavailable` | Arquivo Parquet ausente ou ilegível |

## Limitações dos dados

- O acervo atual contém apenas 2025. `/api/summary` e `/api/fires` usam o acervo de 2025. `/api/activity` e as camadas de mapa com datas explícitas podem consultar novos anos instalados no mesmo padrão de nomes.
- Contagens são detecções dos arquivos de origem. MODIS e VIIRS podem detectar o mesmo evento; a API não deduplica nem calcula hectares queimados.
- A confiança e a resolução variam por sensor e não devem ser comparadas sem metodologia específica.
- Os arquivos estão organizados por país de origem, mas há registros VIIRS com coordenadas que parecem incompatíveis com o país associado. O mapa posiciona o ponto pela coordenada do arquivo, e o campo `country` conserva a associação do arquivo para rastreabilidade.
- A rota de registros completos `/api/fires` tem limite de 5000 pontos por página. O mapa usa a rota compacta `/api/map/foci`.

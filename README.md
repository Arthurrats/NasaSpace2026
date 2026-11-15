
# NasaSpace2026

# Vigia Terra

Base para um observatório de incêndios florestais com landing page, painel demonstrativo e ambiente Python independente para pesquisa.

| Pasta | Responsabilidade |
| --- | --- |
| `frontend/` | Interface Svelte e Vite, com início em `/#/` e painel em `/#/painel`. |
| `backend/` | Aplicação Flask com `GET /api/health` para verificar o serviço. |
| `research/` | Ambiente para experimentos e notebooks, com dependências e venv próprias. |
| `docs/` | [Guia da estrutura, do layout e da identidade visual](docs/DESIGN.md). |

O painel usa dados fictícios de cinco países da América do Sul. Entre pelo botão **Login** no cabeçalho e use a conta de demonstração. No painel, o seletor muda o recorte do mapa. Os três módulos podem rodar separadamente.

## Docker Compose

Com o Docker Desktop ou o Docker Engine com Compose em execução, rode na raiz:

```powershell
docker compose up --build -d --wait
```

Abra [o frontend](http://127.0.0.1:8080/) e confira [a saúde da API](http://127.0.0.1:8080/api/health). O Nginx serve a compilação do Svelte e encaminha `/api/` ao Flask pela rede do Compose. Rode o mesmo comando para recompilar após mudanças.

Para iniciar apenas o ambiente de pesquisa em um contêiner separado:

```powershell
docker compose up --build -d --wait research
docker compose logs research
```

Abra [o JupyterLab](http://127.0.0.1:8888/lab) e use o token exibido nos logs. Os notebooks são salvos em `research/notebooks/`.

```powershell
docker compose --profile research down
```

## Frontend

Use Node.js 20.19+ na linha 20 ou 22.12+.

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Abra `http://localhost:5173`. `npm.cmd run build` gera os arquivos em `frontend/dist/`.

## Backend

Em outro terminal, partindo da raiz do projeto:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run --debug
```

Confira `http://127.0.0.1:5000/api/health`. Em desenvolvimento, o Vite também encaminha `/api` para o Flask.

## Pesquisa

Veja [o guia do ambiente Python](research/README.md). A cartografia usa [Natural Earth via World Atlas](https://github.com/topojson/world-atlas).

## Imagem da landing page

O arquivo `frontend/public/incendio-aereo.webp` foi criado com a ferramenta integrada ImageGen.

<details>
<summary>Prompt usado</summary>

Photorealistic editorial hero photograph for a Portuguese wildfire observation site, cinematic wide landscape 3:2. Aerial oblique view above an immense densely forested mountain valley at blue hour, with several natural winding wildfire lines and ember patches concentrated across the lower center and lower right, smoky deep teal mountains layered into the horizon, a column of billowing smoke in the upper-right catching warm copper light, believable scale and topography, subtle photographic grain, atmospheric but detailed. Smoky near-black blue-green negative space on the upper left to allow text overlay added separately, bright orange fire restrained to small areas. No people, structures, text, logos, graphics, framing or watermarks.

</details>

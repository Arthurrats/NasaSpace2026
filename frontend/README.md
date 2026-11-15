# Frontend da prevIA

Os textos das páginas ficam em `src/content/`. O dashboard reúne indicadores e gráficos. O ambiente **Mapa** abre pela navegação da sessão de demonstração e usa os mesmos focos simulados.

## Mapa-múndi

A cartografia local funciona ao iniciar o frontend. Para usar o Google Maps interativo, obtenha uma [Maps Demo Key](https://developers.google.com/maps/documentation/javascript/demo-key), crie `frontend/.env.local` e reinicie o Vite.

```dotenv
VITE_GOOGLE_MAPS_API_KEY=sua_chave_demo
# Opcional. O padrão é DEMO_MAP_ID.
VITE_GOOGLE_MAP_ID=
```

As variáveis Vite são aplicadas durante a compilação. Para um build local com Google Maps, as variáveis precisam estar disponíveis antes de executar `npm.cmd run build`. A chave demo tem limites de uso e serve para prototipagem. Uma chave usada em produção deve ter as restrições recomendadas pelo Google. [Configuração de chaves](https://developers.google.com/maps/documentation/javascript/get-api-key)

Os focos ficam em arquivos JSON por quadrante em `src/features/fire-monitoring/data/quadrants/`. A plataforma abre na visão mundial. O seletor muda o enquadramento por quadrante ou país. No Google Maps, mover ou ampliar a câmera atualiza os dados conforme os limites visíveis. Os arquivos são carregados via HTTP e reutilizados durante a sessão da página.

## Ambiente local e Docker

Copie `.env.example` para `.env` na raiz do repositório para configurar o Docker Compose. `VITE_GOOGLE_MAPS_API_KEY` e `VITE_GOOGLE_MAP_ID` são argumentos de compilação do frontend. Depois de alterar essas variáveis, recompile os containers com `docker compose up --build`. `PORT_FRONTEND` e `PORT_BACKEND` controlam as portas locais publicadas.

Para o Vite local, use `frontend/.env.local` com as mesmas variáveis `VITE_*` e reinicie `npm.cmd run dev`. Não coloque a chave em arquivos versionados.

## Filtros do dashboard

Os filtros de país e de últimos 7, 14, 30 ou 90 dias alteram os indicadores, o ranking e os gráficos. Os valores e a série diária atuais são exemplos de interface. O painel os identifica como demonstrativos e não calcula previsões.

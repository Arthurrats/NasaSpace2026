# Desenvolvimento com atualização automática no Docker

O `compose.yaml` usa Docker Compose Watch para reconstruir apenas o serviço que recebeu alterações nos arquivos do frontend ou backend. O Compose aproveita as camadas de build que não mudaram e substitui o container; não é preciso apagar imagens manualmente.

## Iniciar em modo de desenvolvimento

Na raiz do repositório, execute o comando de desenvolvimento.

```powershell
docker compose up --build --watch
```

Deixe esse comando rodando enquanto edita o projeto. Ao salvar um arquivo em `frontend/`, o serviço `frontend` é reconstruído. Ao salvar um arquivo em `backend/`, o serviço `backend` é reconstruído. Os dados Parquet continuam montados em modo somente leitura e não acionam rebuild.

Para parar, pressione `Ctrl+C`.

## Execução em segundo plano

```powershell
docker compose up --build -d --wait
docker compose ps
docker compose logs --tail 100 frontend backend redis
```

Abra o frontend pela porta `PORT_FRONTEND`, com padrão 8080. O endpoint `/api/health` nessa mesma porta verifica o caminho Nginx → Flask. A porta padrão de acesso direto ao Flask é 5000. Os dois serviços são publicados em `127.0.0.1`. O Redis usa a rede interna e pode ser verificado com `docker compose exec redis redis-cli ping`.

## O que dispara atualização

- Alterações em `frontend/` ou `backend/` reconstruem o serviço correspondente, respeitando os arquivos excluídos em `.dockerignore`.
- Alterações em `.env` ou `compose.yaml` requerem reaplicar o Compose. A chave e o ID do Google Maps são argumentos de build do frontend. Use `docker compose up --build -d --wait` para reaplicar a configuração.
- A substituição de um Parquet no diretório já montado aparece na próxima consulta. Prefira preparar o arquivo completo e fazer uma troca atômica. Mudar o caminho em `PREVIA_DATA_HOST_DIR` requer reaplicar o Compose.
- Dependências e conteúdo são copiados em etapas separadas nos Dockerfiles, permitindo ao BuildKit reutilizar camadas de dependências quando só o código muda.

O Compose recria o serviço com a nova imagem. A sessão demonstrativa pode pedir novo login depois de uma recriação do backend. Se `/api/health` responder, mas as consultas aos dados retornarem `503`, confira o bind mount, os nomes dos Parquet e os logs de `backend`. A API continua consultando Parquet quando o Redis está indisponível.

## Compatibilidade

Confira `docker compose version` e `docker compose up --help` para verificar se a instalação oferece `--watch`.

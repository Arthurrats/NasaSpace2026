# Desenvolvimento com atualização automática no Docker

O `compose.yaml` usa Docker Compose Watch para reconstruir apenas o serviço que recebeu alterações nos arquivos do frontend ou backend. O Compose aproveita as camadas de build que não mudaram e substitui o container; não é preciso apagar imagens manualmente.

## Iniciar em modo de desenvolvimento

Na raiz do repositório, execute:

```powershell
docker compose up --build --watch
```

Deixe esse comando rodando enquanto edita o projeto. Ao salvar um arquivo em `frontend/`, o serviço `frontend` é reconstruído. Ao salvar um arquivo em `backend/`, o serviço `backend` é reconstruído. Os dados Parquet continuam montados em modo somente leitura e não acionam rebuild.

Para parar, pressione `Ctrl+C`.

## O que dispara atualização

- Alterações em qualquer arquivo dentro de `frontend/` reconstruem o frontend.
- Alterações em qualquer arquivo dentro de `backend/` reconstruem o backend.
- Alterações em `.env`, `compose.yaml` ou nos dados Parquet exigem reiniciar o Compose para aplicar a nova configuração.
- Dependências e conteúdo são copiados em etapas separadas nos Dockerfiles, permitindo ao BuildKit reutilizar camadas de dependências quando só o código muda.

O Compose atualiza e remove a imagem antiga sem uso depois do rebuild. A imagem atualmente usada pelo container não é apagada.

## Compatibilidade

O recurso `develop.watch` requer Docker Compose 2.22.0 ou posterior. A versão disponível neste projeto (5.5.1) já é compatível.

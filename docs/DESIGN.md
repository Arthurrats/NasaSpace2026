# Design da prevIA

## Organização

```text
frontend/
├── public/                        Ícone da prevIA
└── src/
    ├── main.js                    Inicialização, fontes e CSS global
    ├── App.svelte                 Rotas, títulos e sessão de demonstração
    ├── layouts/                   Estrutura compartilhada e navegação
    ├── pages/                     Página inicial, login e painel
    ├── features/
    │   └── fire-monitoring/
    │       ├── components/        Mapa, legenda, prévia e gráficos
    │       └── data/demo.js       Regiões, focos e séries de exemplo
    └── styles/
        ├── theme.css              Paleta, tipografia e tokens visuais
        ├── base.css               Regras globais e largura de conteúdo
        └── components.css         Botões, cards e gráficos compartilhados
backend/                           API Flask
research/                          Ambiente Python e notebooks
docs/                              Este guia
```

Estilos específicos de uma página ou componente ficam no bloco `<style>` do arquivo Svelte correspondente. Os dados demonstrativos ficam em `features/fire-monitoring/data/demo.js`, junto da funcionalidade que os consome.

## Layout

- A aplicação seleciona a página pelo hash da URL. [App.svelte](../frontend/src/App.svelte)
- O layout reúne o link para pular a navegação, o cabeçalho, a área de conteúdo e o rodapé. [SiteLayout.svelte](../frontend/src/layouts/SiteLayout.svelte)
- O cabeçalho permanece visível ao rolar e troca os links da navegação por um menu lateral em telas estreitas. O tema e o login continuam acessíveis no cabeçalho. [SiteHeader.svelte](../frontend/src/layouts/SiteHeader.svelte)

| Rota | Conteúdo |
| --- | --- |
| `/#/` | Solução com mapa-múndi e focos na América do Sul, impactos das queimadas, recursos e equipe. |
| `/#/login` | Acesso à conta de demonstração pelo botão Login do cabeçalho. |
| `/#/painel` | Indicadores, mapa com seletor de país, ranking e gráficos. Requer a sessão de demonstração. |

A sessão de demonstração usa o `sessionStorage` da aba. Um acesso direto ao painel sem sessão abre o login. O botão Sair encerra a sessão. O fluxo simula a navegação autenticada no frontend, sem coleta de credenciais.

No painel, mapa, ranking e gráficos são empilhados em telas de até 760 px. Até 560 px, os indicadores também ficam em uma coluna. A demonstração inclui Brasil, Argentina, Bolívia, Colômbia e Paraguai. O seletor muda o recorte e os marcadores do mapa. Os totais e gráficos representam o cenário demonstrativo completo.

Na página inicial, a abertura ocupa pelo menos a altura disponível abaixo do cabeçalho. As demais seções têm altura mínima de 76% da tela, limitada a 820 px, e crescem conforme o conteúdo. O token `--page-inset` define o espaçamento interno em seções de largura total. A entrada do hero e dos títulos usa deslocamento e opacidade leves, respeitando `prefers-reduced-motion`.

## Marca, equipe e contato

- O símbolo da segunda página do PDF da marca foi convertido para PNG transparente e é usado no site e no ícone da aba. [previa-icon.png](../frontend/public/previa-icon.png)
- Os nomes e fotos individuais ficam na lista `team`. Defina `groupPhoto` para a foto coletiva. Com os caminhos vazios, a interface mostra espaços retangulares de 4:3 para retratos e 16:7 para a foto de grupo. [Landing.svelte](../frontend/src/pages/Landing.svelte)
- O rodapé reúne navegação, código do projeto e contato pelas issues do GitHub a partir de `repositoryUrl`. [SiteFooter.svelte](../frontend/src/layouts/SiteFooter.svelte)

## Paleta

O tema escuro usa a paleta original. O tema claro usa branco gelo no fundo, verde petróleo para texto e tons mais escuros de verde e laranja para contraste. A escolha feita no cabeçalho fica no `localStorage`. Os títulos principais usam Barlow Condensed e o restante da interface usa Inter. [theme.css](../frontend/src/styles/theme.css)

| Cor | Hexadecimal | Token | Uso |
| --- | --- | --- | --- |
| Verde petróleo | `#101B19` | `--background` | Fundo, controles e base do mapa |
| Verde floresta | `#1D302A` | `--surface` | Cards, seções e menu móvel |
| Verde tecnológico | `#78C850` | `--accent` | Identidade, botão principal e comparativos |
| Verde-limão | `#B6E36B` | `--indicator` | Ícones, foco do teclado e baixa intensidade |
| Laranja alerta | `#FF8A32` | `--heat` | Focos de média intensidade e gráfico de evolução diária |
| Vermelho incêndio | `#E84B32` | `--critical` | Focos de alta intensidade e ícone do indicador correspondente |
| Branco gelo | `#F2F5F0` | `--text` | Títulos e textos principais |
| Cinza esverdeado | `#9BAAA2` | `--muted` | Descrições, rótulos auxiliares e eixos |

O mapa e a legenda compartilham os mesmos marcadores nos dois temas. A baixa intensidade usa `#B6E36B`, a média usa `#FF8A32` e a alta usa `#FF6148`, uma variação mais viva do vermelho incêndio. Contornos escuros destacam os pontos sobre a cartografia clara e escura.

Para rodar o projeto e compilar o frontend, consulte o [README principal](../README.md).

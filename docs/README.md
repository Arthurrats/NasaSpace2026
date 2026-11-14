# Estrutura e identidade visual da prevIA

## Organização

```text
frontend/
├── public/                        Ícone da prevIA
└── src/
    ├── main.js                    Inicialização, fontes e CSS global
    ├── App.svelte                 Rotas e título da página
    ├── layouts/                   Estrutura compartilhada e navegação
    ├── pages/                     Página inicial e painel
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
- O cabeçalho marca a rota ativa e troca os links da navegação por um menu lateral em telas estreitas. [SiteHeader.svelte](../frontend/src/layouts/SiteHeader.svelte)

| Rota | Conteúdo |
| --- | --- |
| `/#/` | Solução com mapa global, impactos das queimadas, recursos e equipe. |
| `/#/painel` | Indicadores, mapa com seletor de região, ranking e gráficos temporais e regionais. |

No painel, mapa, ranking e gráficos são empilhados em telas de até 760 px. Até 560 px, os indicadores também ficam em uma coluna. O seletor altera o recorte do mapa. Os totais e gráficos continuam representando o cenário demonstrativo completo.

As seções da página inicial ocupam toda a largura da tela. O token `--page-inset` dá respiro ao conteúdo dentro de cada seção. O mapa, a legenda e os gráficos são compartilhados com o painel e usam os mesmos dados simulados.

## Marca, equipe e contato

- O símbolo da segunda página do PDF da marca foi convertido para PNG transparente e é usado no site e no ícone da aba. [previa-icon.png](../frontend/public/previa-icon.png)
- Os nomes da equipe ficam na lista `team` da página inicial. [Landing.svelte](../frontend/src/pages/Landing.svelte)
- O contato usa o endereço `contactUrl` no rodapé e aponta para as issues do repositório. [SiteFooter.svelte](../frontend/src/layouts/SiteFooter.svelte)

## Paleta

O arquivo de tema reúne as cores usadas na interface. O tema usa Barlow Condensed nos títulos principais e Inter nas demais áreas. [theme.css](../frontend/src/styles/theme.css)

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

As classes `intensity-high`, `intensity-medium` e `intensity-low` definem a cor usada tanto no mapa quanto na legenda. Bordas e superfícies auxiliares são misturas da mesma paleta.

Para rodar o projeto e compilar o frontend, consulte o [README principal](../README.md).

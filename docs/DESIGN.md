# Design da prevIA

## Organização

```text
frontend/
├── public/                        Ícone, arte orbital, textura do globo e retratos
└── src/
    ├── main.js                    Inicialização, fontes e CSS global
    ├── App.svelte                 Rotas, títulos e sessão de demonstração
    ├── layouts/                   Estrutura compartilhada e navegação
    ├── pages/                     Landing, login e telas da plataforma
    ├── content/                   Textos e rótulos por área da interface
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

Estilos específicos ficam nos blocos `<style>` dos componentes Svelte. As amostras da landing ficam em `features/fire-monitoring/data/demo.js`. As telas internas usam os dados da API.

## Layout

- A aplicação seleciona a página pelo hash da URL. [App.svelte](../frontend/src/App.svelte)
- O layout reúne o link para pular a navegação, o cabeçalho, a área de conteúdo e o rodapé. [SiteLayout.svelte](../frontend/src/layouts/SiteLayout.svelte)
- O cabeçalho permanece visível ao rolar e troca os links da navegação por um menu lateral em telas estreitas. O tema e o login continuam acessíveis no cabeçalho. [SiteHeader.svelte](../frontend/src/layouts/SiteHeader.svelte)

| Rota | Conteúdo |
| --- | --- |
| `/#/` | Arte orbital, mapa ilustrativo com seletor de país, impactos, demonstrações de série, calendário e comparativo, cobertura dos dados, casos de uso, equipe e FAQ. |
| `/#/login` | Acesso à conta de demonstração pelo botão Login do cabeçalho. |
| `/#/painel` | Seis indicadores, mapa sul-americano, globo 3D e comparativos por país, mês e sensor. |
| `/#/paises` | Indicadores, bolhas 3D e ranking por setor geográfico. |
| `/#/mapa` | Mapa de focos com filtros, legenda e visualização por calor, grupos, pixels ou círculos. |
| `/#/timelapse` | Mapa com régua de datas e reprodução de quadros diários, semanais ou mensais. |
| `/#/previsor` | Projeção diária e mapa sazonal de pontos com área selecionável. |
| `/#/calendario` | Indicadores mensais, calendário diário, mapa de calor e comparação histórica. |

O Flask cria uma sessão demonstrativa por cookie assinado. O acesso direto a uma tela interna sem sessão leva ao login. O botão **Sair** encerra a sessão. A conta de demonstração dispensa credenciais.

A plataforma usa barra lateral em telas largas e navegação compacta até 760 px. As grades de indicadores e gráficos se reorganizam conforme a largura. O Mapa e o Timelapse ocupam a altura disponível, com os filtros sobre a cartografia. Nas telas Calendário e Previsor, é possível delimitar uma área por desenho ou por coordenadas.

O hero usa colunas lado a lado em telas largas e empilha o texto e o mapa até 950 px. O token `--page-inset` define o espaçamento interno em seções de largura total. O cabeçalho acompanha a seção no centro da janela. As animações da landing só rodam na seção ativa, pausam quando a página perde visibilidade e respeitam `prefers-reduced-motion`. As abas de demonstração aceitam setas, Home e End.

## Marca, equipe e contato

- O símbolo da segunda página do PDF da marca foi convertido para PNG transparente e é usado no site e no ícone da aba. [previa-icon.png](../frontend/public/previa-icon.png)
- Os nomes e caminhos individuais ficam na lista `team`. Os cinco retratos estão em `frontend/public/team/`. Defina `groupPhoto` para incluir uma foto coletiva. O espaço atual usa proporção de 16:7 e os retratos usam 4:3. [Configuração da landing](../frontend/src/content/landing.js)
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

Nas camadas operacionais de marcadores, baixa, média e alta confiança usam respectivamente `#B6E36B`, `#FF8A32` e `#E84B32`, conforme a legenda. A prévia ilustrativa usa uma variação mais viva de vermelho. O Calendário aplica Cividis à camada de calor e às células dos dias. O símbolo `!` e a borda tracejada identificam dias incomuns além da cor. O mapa sazonal do Previsor usa pontos amarelos.

Para rodar o projeto e compilar o frontend, consulte o [README principal](../README.md).

# Dados e metodologia da prevIA

Esta página descreve os cálculos em uso na plataforma. O [PDF Modelo de Média Histórica Sazonal](Modelo_Media_Historica_Sazonal_PrevIA.pdf) registra uma proposta metodológica que prevê deduplicação, calibração entre sensores e previsão por média plurianual. A implementação atual combina as detecções dos sensores sob um contrato comum e oferece separadamente a comparação plurianual e a projeção sazonal de referência.

## Acervo e unidade de análise

O acervo atual contém 24 Parquet de 2025, com partições MODIS e VIIRS JPSS-1 para doze países. Os nomes seguem `modis_2025_Brazil.parquet` e `viirs-jpss1_2025_Brazil.parquet` nas pastas `modis/` e `viirs/`. A API conserva a associação ao país do arquivo e posiciona os pontos pelas coordenadas do registro. Há registros com país e coordenadas incompatíveis. O Dashboard aplica a caixa sul-americana `-84,-57,-31,15`, em ordem oeste, sul, leste e norte. O Calendário e o Previsor recortam a consulta pelos mesmos limites, incluindo a interseção com a área desenhada.

Cada linha representa uma detecção de satélite. Um incêndio pode gerar várias detecções no mesmo sensor ou em ambos. A aplicação atual não deduplica incêndios entre sensores, não calibra as escalas de confiança e não recebe notificações oficiais. Por isso, o campo de incêndios notificados é nulo. A soma de FRP reúne medições válidas de potência radiativa em MW. Datas e horários de aquisição são tratados em UTC. Um dia com zero detecções registradas pode ter lacunas de observação.

## Calendário e comparação histórica

- A média diária do calendário divide a contagem mensal pelos dias do mês. No Dashboard a média usa somente os dias com registros.
- Um dia fica acima do padrão quando tem pelo menos dois focos e supera o percentil 90 dos 28 dias anteriores. O início da série precisa acumular pelo menos 14 dias anteriores para classificar.
- Até três meses com as maiores médias diárias positivas recebem a indicação de período crítico. A escala do calendário usa o pico de cada mês como referência e separa zero das quatro faixas de intensidade.
- A comparação plurianual usa a média dos totais do mesmo mês em pelo menos dois anos anteriores com as partições exigidas pelo filtro de país e sensor. A diferença é o total observado menos a média. A diferença percentual usa a média como denominador e fica indisponível quando ela é zero. A disponibilidade de arquivos indica o acervo encontrado e não garante cobertura diária completa.

## Previsor

**Projeção diária.** Estima os 14 dias depois do fim do ano selecionado. A estimativa de cada dia da semana é a média das últimas quatro ocorrências daquele dia nos 28 dias finais. A avaliação repete o cálculo em janelas anteriores e mede o erro absoluto médio. A faixa exibida usa os percentis 10 e 90 dos erros por horizonte, inclui a estimativa central e tem limite inferior de zero. Trata-se de uma faixa empírica retrospectiva.

**Projeção sazonal.** Usa o total observado e a distribuição espacial do mesmo mês do ano de referência para representar o mês do ciclo seguinte. Esse é o método sazonal ingênuo, identificado como `seasonal_naive` na API. Ele usa um único ano de referência mesmo quando há anos suficientes para calcular a comparação plurianual do Calendário. Com os dados atuais, 2025 serve de referência para 2026.

As duas projeções são exploratórias. A aplicação não calcula probabilidade de incêndio, área queimada, índice meteorológico ou alerta operacional.

O [contrato da API](API.md) detalha os campos devolvidos. O [README principal](../README.md) descreve os fluxos de uso.

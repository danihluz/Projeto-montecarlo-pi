# Validação da integração — Marco 2

Data: 16/11/2026. Branch local: `integracao-marco2`, baseada em
`fcb0e329e2ca53f9e82203b721499e163a2f4a7b` do PR #14. Esse commit já contém
integralmente os heads auditados dos PRs #15 (`bc6062d`) e #16 (`151d3ef`).
Os três PRs permaneciam abertos na consulta; nenhum foi alterado remotamente.

## Alterações

- `scripts/coletar.sh`: retirar o CR final do campo `dentro` do gabarito, validar
  o `n` impresso e interromper com erro após registrar uma divergência. Interface
  e nove colunas CSV preservadas; nenhuma alteração nos resultados esperados.
- `Makefile`: `make` compila sequencial, OpenMP e MPI nos caminhos do coletor;
  alvos antigos preservados e perfilamento continua opcional.
- `README.md`, `AUTORES.md`, `mpi/README.md` e análises: instruções completas,
  atribuição de autoria, distinção entre coletas, remoção dos campos pendentes
  e registro explícito das medições ainda necessárias no laboratório.
- `scripts/testar_coletor.py`: sete regressões com fixtures sintéticas isoladas.
- `scripts/gerar_graficos.py`: reprodução dos seis gráficos a partir das tabelas
  do analisador; Matplotlib é uma dependência opcional exclusiva dessa etapa.
- `dados/integracao_local/`: medições e metadados novos, separados dos históricos.

Os arquivos dos algoritmos sequencial, OpenMP e MPI e seus helpers não mudaram.
O SHA-256 do baseline versionado/original continua
`1eda8ea76c5cba608216edf6d8b5d1f02198558013ac291468d9b762c17fde7d`.

## Testes realmente executados

Ambiente: Ubuntu 26.04.1/WSL2, GCC 15.2, OpenMPI 5.0.10, oito CPUs visíveis.
MPI foi disponibilizado por extração local de pacotes Ubuntu no ambiente de
validação. Nenhum pacote ou caminho desse ambiente foi incorporado ao código
do projeto. Os fontes foram copiados do worktree para uma pasta isolada, sem
reutilizar os executáveis antigos. Os CSVs históricos do repositório de trabalho
não foram substituídos pelos executores de testes.

| Verificação | Resultado |
|---|---|
| `make all perfilamento`, sem binários prévios | Três versões e instrumentado compilados pela raiz. |
| Regressões do coletor | **7 aprovadas**: LF, CRLF, `n` errado, `pi` errado, `dentro` errado, saída duplicada e falha de execução. |
| Protocolo nos casos válidos das regressões | 1 aquecimento + 3 repetições por entrada; 9 linhas e formato CSV preservados. |
| Regressões do verificador OpenMP | **2 aprovadas**, preservação de registros. |
| Verificador OpenMP real | **312 comparações aprovadas**, incluindo repetibilidade e equipes ajustadas. |
| Teste original MPI/OpenMPI | **108 comparações exatas**, argumento omitido, rejeição de 0/-1 e **99 medições OK** pelo coletor histórico. |
| Jump-ahead MPI | **2.335 estados, 119 partições e 155.120 coordenadas** iguais ao original. |
| Comparações adicionais OpenMP/MPI | **60 aprovadas**: n=1,17,100003,10M,150M; p=1,3,12; duas repetições por versão. |
| Coleta conjunta atual | **171 medições OK**, 57 configurações, forte/fraca, 1 aquecimento + 3 válidas. O snapshot usava gabarito CRLF. |
| Cálculo independente | Todas as medianas, speedups e eficiências do resumo e tabelas coincidem, respeitado arredondamento de 6 casas. |
| Geração de tabelas | `resumo.csv`, três tabelas fortes e uma fraca gerados pelo analisador. |
| Geração de gráficos | Seis imagens dos dados históricos e seis da nova rodada geradas; imagens históricas originais preservadas. |
| Investigação MPI com um processo | **45 medições OK** em cinco configurações de execução/afinidade; fator 2 não reproduzido. |

As seis figuras da nova rodada foram inspecionadas visualmente: eixos, unidades,
legendas e pontos correspondem às tabelas conferidas. A exportação foi executada
com Python 3.14/Matplotlib 3.11.2 no Windows, lendo os CSVs gerados no WSL; os
tempos das três versões foram todos coletados no mesmo ambiente Linux.

As saídas artificiais dos testes do coletor não integram os CSVs experimentais.
O resumo verificável dos testes está em
[validacao.json](../dados/integracao_local/validacao.json). Os dados, flags,
afinidade e hashes dos fontes estão em
[ambiente.json](../dados/integracao_local/ambiente.json).

O detector ThreadSanitizer não foi repetido nesta rodada, pois os fontes OpenMP
não mudaram. A tentativa da auditoria anterior com GCC/libgomp é inconclusiva:
o alerta na redução também foi reproduzido em um controle mínimo correto.
Não foi considerada uma execução aprovada de detecção dinâmica de corridas.
Não foi encontrado compartilhamento mutável indevido na inspeção; o código
usa redução e estados privados, e as execuções foram reproduzíveis.

## Dados e análise

As 171 medições desta rodada estão em [medicoes.csv](../dados/integracao_local/medicoes.csv).
A investigação MPI está em [investigacao_mpi.csv](../dados/integracao_local/investigacao_mpi.csv).
Os números e a interpretação, incluindo as duas referências de speedup, estão
na [análise experimental](analise_experimental.md). A causa da razão histórica
próxima de 2 na máquina do Gui não foi determinada por testes em outra máquina;
isso foi registrado como limite da evidência, sem atribuição causal inventada.

O programa não depende de caminhos de integrantes nem de `mpi/.ambiente/`.
O teste legado `mpi/testar.py` depende de rede para ler o commit fixado e escreve
em `mpi/resultados/`; o README orienta executá-lo em uma cópia separada. O coletor
e o analisador atuais funcionam com os arquivos locais. Não há conflitos de
arquivos entre as contribuições incorporadas.

## Pendências e parecer

A integração está tecnicamente preparada para revisão e merge, com os testes
acima aprovados. Ainda faltam a coleta final no laboratório, registro de seu
ambiente e ensaio da demonstração ao vivo. Docker/laboratório não foram validados
nesta execução. Os 12 workers locais são sobrealocação em oito CPUs visíveis.
As pendências experimentais não foram substituídas por estimativas ou dados
locais rotulados como laboratório.

A branch inclui o histórico dos três integrantes e pode ser integrada por uma
única PR de integração com merge que preserve commits, quando autorizada. Se o
grupo preferir os PRs originais, a ordem equivalente é **#16 → #15 → #14 → esta
branch de correções** (#15 e #16 são independentes). Incorporar só o #14 remoto
deixaria de fora as correções locais descritas aqui. Evitar squash global ou
reescrita de branches, preservando a autoria e o histórico avaliados.

Nenhum push, abertura de PR ou merge na main foi realizado nesta preparação.

# Ranking das Freguesias

Índice de Freguesia 2.0 dos 16 principais clássicos do futebol brasileiro, feito para o **Canal do Canedo**.

Site: https://vcanedo88.github.io/ranking-classicos/

## O que é

Para cada clássico, o índice mede o aproveitamento do time dominante nos **últimos 50 jogos oficiais** (vitória = 3, empate = 1, derrota = 0), com dois pesos:

- **Recência**, por bloco de 10 jogos: 1–10 ×3 · 11–20 ×2,5 · 21–30 ×2 · 31–40 ×1,5 · 41–50 ×1
- **Importância do jogo**:

| Tipo de jogo | Peso |
|---|---|
| Estadual (classificação), grupos de regional, Taça Rio de consolação | 1,0 |
| Mata-mata de estadual ou regional (inclui finais de turno) | 1,2 |
| Final de estadual ou regional, Supercopa, Recopa, Série B | 1,5 |
| Brasileirão e fase de grupos da Libertadores | 1,75 |
| Mata-mata de Copa do Brasil, Libertadores ou Sul-Americana | 2,0 |
| Final de Copa do Brasil, Libertadores ou Sul-Americana | 2,5 |

Cada mata-mata (ida e volta ou jogo único) vira **um jogo extra** vencido por quem avançou, com o peso da fase. Pênaltis contam como empate no jogo; quem vence a disputa leva o jogo extra. Confronto empatado sem pênaltis: avança quem tinha a vantagem do regulamento.

Índice = Σ(peso × pontos) ÷ Σ(peso × 3). Freguesia a partir de 65; vantagem clara a partir de 55.

## G12: os 66 confrontos entre os 12 grandes

Duas abas no topo do site:

- **G12** (https://vcanedo88.github.io/ranking-classicos/g12.html): só os 52 confrontos interestaduais. No ranking por clube, os clubes do Rio e de São Paulo têm 8 adversários; os de Minas e do Rio Grande do Sul, 10.
- **G12 com clássicos** (https://vcanedo88.github.io/ranking-classicos/g12-classicos.html): os 66 confrontos, com os 14 clássicos locais; cada clube tem 11 adversários.

Mesmo Índice de Freguesia 2.0, aplicado a todos os confrontos entre Flamengo, Fluminense, Vasco, Botafogo, Corinthians, Palmeiras, São Paulo, Santos, Grêmio, Internacional, Cruzeiro e Atlético-MG. Diferenças em relação ao ranking dos clássicos:

- **Janela de 30 jogos oficiais** (recortes de 30, 20 e 10), com os pesos de recência 3 / 2,5 / 2 por bloco de 10. Na aba "G12 com clássicos", os 14 clássicos locais também entram com 30 jogos.
- **Forma**: os últimos 5 jogos, mostrados como contexto, fora do ranking.
- **Mando**: índice do dominante só nos jogos com cada mandante, sem os jogos em campo neutro e sem o bônus dos mata-matas.
- **Ranking por clube**: aproveitamento ponderado de cada clube somando os seus 11 confrontos.
- Mesmos pesos de importância. O Mundial de Clubes (Palmeiras x Botafogo, 2025) usa o peso de mata-mata de copa. Classificações pelo gol fora de casa e decisões do STJD ficam registradas em `avancou_por_vantagem` e `obs`.

Arquivos: `dados/classicos_g12.json`, `dados/jogos_g12.csv` (52 confrontos interestaduais; os locais vêm de `dados/jogos.csv`), `scripts/calcular_g12.py`, `data/g12_*.json` e `csv/g12_*.csv` (aba G12), `data/g12c_*.json` e `csv/g12c_*.csv` (aba G12 com clássicos), `g12.html`, `g12-classicos.html`.

Conferência: oGol como fonte principal. Segunda fonte para cada jogo interestadual da janela: base do Brasileirão 2003–2025 (adaoduque/brasileirao_dataset), Transfermarkt para copas, Série B e 2026, e a imprensa nos casos em que as duas fontes divergiram (coluna `fonte2`).

Para atualizar: acrescente o jogo em `dados/jogos.csv` (clássico local) ou `dados/jogos_g12.csv` (interestadual) e rode `python3 scripts/calcular.py && python3 scripts/calcular_g12.py`.

## Estrutura

- `dados/jogos.csv` — base de jogos (conferida no oGol). Colunas especiais: `tipo` (`turno`, `consolacao`, `wo`) e `avancou_por_vantagem`.
- `dados/pesos.json` — pesos e limiares.
- `dados/classicos.json` — os 16 clássicos.
- `scripts/calcular.py` — gera `data/*.json` (site) e `csv/*.csv`.
- `index.html`, `assets/` — o site (GitHub Pages).

## Atualizar

1. Acrescente o novo jogo em `dados/jogos.csv`.
2. Rode `python3 scripts/calcular.py`.
3. Faça commit e push. O GitHub Pages publica sozinho.

Os escudos pertencem aos respectivos clubes. Fonte Montserrat sob SIL Open Font License 1.1.

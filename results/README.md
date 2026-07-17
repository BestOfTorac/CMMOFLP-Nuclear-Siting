# Risultati

La cartella separa lo **snapshot definitivo pubblicato** dagli output locali prodotti durante nuove esecuzioni.

## Struttura

```text
results/
├── final/
│   ├── raw/        tre CSV consolidati della campagna definitiva
│   ├── summary/    aggregazioni dell’analisi finale
│   └── ablation/   tabelle dell’ablation study
├── raw/            output locali e intermedi ignorati da Git
├── aggregated/     aggregazioni storiche ignorate da Git
├── processed/      elaborazioni locali ignorate da Git
└── plots/          grafici generati localmente
```

## Snapshot definitivo

I file in `final/raw/` sono dati sperimentali immutati:

| File | Righe | Contenuto |
|---|---:|---|
| `final_heuristics.csv` | 180 | greedy e local search su 90 istanze |
| `final_grasp_vnd.csv` | 450 | cinque seed GRASP-VND per istanza |
| `final_exact.csv` | 90 | modello compatto con incumbent, bound e gap |

I file in `final/summary/` e `final/ablation/` sono derivati automaticamente. Non devono essere corretti manualmente.

## Rigenerare le tabelle pubblicate

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
```

I comandi leggono per impostazione predefinita `results/final/raw/` e riscrivono gli output versionati. Un `git diff` vuoto dopo la rigenerazione conferma la riproducibilità.

## Ripetere gli esperimenti

Le nuove campagne devono essere salvate in `results/raw/`, che rimane ignorata da Git. Per analizzarle si passano esplicitamente i percorsi:

```bash
python scripts/analyze_final_results.py \
  --heuristics results/raw/final_heuristics.csv \
  --grasp-vnd results/raw/final_grasp_vnd.csv \
  --exact results/raw/final_exact.csv \
  --output-dir results/processed/final
```

In questo modo una riproduzione locale non sovrascrive lo snapshot ufficiale.

## Regole di interpretazione

- un incumbent compact non viene chiamato ottimo senza `optimality_certified = True`;
- i gap reali sono calcolati soltanto sulle istanze con ottimo certificato;
- le cinque run GRASP-VND sono indipendenti;
- best, average e worst seed restano distinti;
- i CSV grezzi pubblicati non devono essere modificati manualmente.

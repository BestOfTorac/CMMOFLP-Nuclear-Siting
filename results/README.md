# Risultati

La cartella raccoglie gli output degli esperimenti e delle analisi.

## Struttura attuale

```text
results/
├── raw/          una riga per ogni esecuzione
├── aggregated/   aggregazioni storiche
├── processed/    tabelle prodotte dalle analisi finali
└── plots/        grafici generati automaticamente
```

## Risultati grezzi

I file in `raw/` sono prodotti dai runner sperimentali, ad esempio:

```text
final_heuristics.csv
final_grasp_vnd.csv
final_exact.csv
```

Non devono essere modificati manualmente.

## Analisi finali

```bash
python scripts/analyze_final_results.py
```

genera le tabelle in:

```text
results/processed/final/
```

Tra gli output principali:

- `exact_summary.csv`;
- `baseline_summary.csv`;
- `h2_run_summary.csv`;
- `h2_best_of_five_summary.csv`;
- `h2_instance_summary.csv`;
- `class_summary.csv`;
- `noncertified_instances.csv`.

L’ablation study:

```bash
python scripts/analyze_ablation.py
```

genera:

```text
results/processed/ablation/
```

## Politica di versionamento

Gli output intermedi, le calibrazioni e i file generati localmente sono ignorati da Git.

Durante la pulizia del repository verrà pubblicata soltanto una selezione compatta dei risultati definitivi, sufficiente a:

- verificare i numeri riportati nel README;
- rigenerare tabelle e grafici;
- evitare di ripetere l’intera campagna AMPL/Gurobi dopo un clone.

## Regole di interpretazione

- un incumbent compact non viene chiamato ottimo senza `optimality_certified = True`;
- i gap reali sono calcolati soltanto sulle istanze con ottimo certificato;
- i cinque seed GRASP-VND sono conservati come esecuzioni indipendenti;
- best, average e worst seed devono essere distinti;
- i risultati grezzi non devono essere sovrascritti da elaborazioni manuali.

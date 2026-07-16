# Analisi finale dei risultati

Lo script `scripts/analyze_final_results.py` aggrega i tre file grezzi definitivi:

```text
results/raw/final_heuristics.csv
results/raw/final_grasp_vnd.csv
results/raw/final_exact.csv
```

Esecuzione:

```bash
python scripts/analyze_final_results.py
```

Output:

```text
results/processed/final/
```

## Tabelle prodotte

- `exact_summary.csv`: risultati compact per dimensione;
- `baseline_summary.csv`: fattibilità, ottimalità e gap di greedy e local search;
- `h2_run_summary.csv`: risultati GRASP-VND per singola esecuzione;
- `h2_best_of_five_summary.csv`: risultati considerando il migliore dei cinque seed;
- `h2_instance_summary.csv`: dettaglio completo per istanza;
- `class_summary.csv`: confronto per dimensione, distribuzione e capacità;
- `noncertified_instances.csv`: casi nei quali il compact non certifica l'ottimo.

## Regole

I gap reali vengono calcolati soltanto quando:

```text
optimality_certified = True
```

L'incumbent compact di una esecuzione terminata al time limit non viene usato come ottimo.

Per i casi senza ottimo noto vengono riportati separatamente:

- incumbent compact;
- best bound compact;
- migliore soluzione H2;
- miglioramento di H2 rispetto all'incumbent;
- distanza tra il best bound e H2.

Valori numerici con errore assoluto inferiore a `1e-7` sono trattati come zero.

# Grafici

La cartella distingue i grafici definitivi versionati dalle visualizzazioni prodotte durante analisi locali.

## Grafici definitivi

I file in `final/` sono generati esclusivamente dalle tabelle pubblicate in `results/final/`:

```bash
python scripts/generate_final_plots.py
```

Il comando produce:

- `solution_quality.png`: confronto tra ammissibilità e ottimalità delle varianti euristiche;
- `quality_runtime_tradeoff.png`: compromesso tra gap medio e runtime;
- `h2_optimality_by_class.png`: qualità di GRASP-VND best-of-5 nelle 18 classi;
- `noncertified_case.png`: confronto tra incumbent, soluzione H2 e bound nell’unico caso non certificato.

I PNG in `final/` vengono versionati perché sono utilizzati nel README, nella documentazione e nelle slide. Altri grafici sperimentali restano locali e ignorati da Git.

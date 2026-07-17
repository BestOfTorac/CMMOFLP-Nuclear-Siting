# Script storici

Questa cartella conserva le analisi utilizzate durante pilot e calibrazioni.

| Script | Fase |
|---|---|
| `analyze_pilot_results.py` | baseline sulle istanze tiny/small |
| `analyze_exact_results.py` | confronto compact–threshold nel pilot |
| `analyze_heuristic_gaps.py` | gap delle euristiche pilota |
| `analyze_grasp_vnd_pilot.py` | analisi multi-seed e calibrazioni |
| `check_upper_bound_pilot.py` | verifica dell’upper bound nel pilot |

Questi script restano eseguibili, ma leggono per impostazione predefinita file locali storici sotto `results/raw/` e producono output in `results/aggregated/`.

Per la versione finale usare invece:

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
```

La cronologia sperimentale è descritta in [`docs/history/`](../../docs/history/README.md).

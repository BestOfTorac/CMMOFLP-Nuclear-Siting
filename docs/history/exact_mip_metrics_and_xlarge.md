# Metriche MIP e calibrazione XLarge

## Metriche restituite dal modello compatto

Il runner AMPL richiede al solver:

```text
mip:return_gap=3
mip:bestbound=1
```

Per ogni esecuzione del modello compatto vengono registrati:

- `objective_value`: migliore soluzione intera trovata;
- `best_bound`: miglior bound duale;
- `relative_mip_gap`;
- `absolute_mip_gap`;
- `has_incumbent`;
- `optimality_certified`;
- `termination_reason`;
- tempo solver ed end-to-end.

Per un problema di massimizzazione:

```math
\text{absolute gap}
=
|\text{best bound}-\text{incumbent}|
```

e:

```math
\text{relative gap}
=
\frac{\text{absolute gap}}
{|\text{incumbent}|}.
```

Un incumbent trovato al time limit è una soluzione ammissibile, ma non deve essere presentato come ottimo.

## Stati principali

| Condizione | Interpretazione |
|---|---|
| `optimality_certified = True` | ottimo dimostrato |
| incumbent e `time_limit` | soluzione ammissibile con gap |
| nessun incumbent e `time_limit` | nessuna soluzione intera disponibile |
| `infeasible` | problema dimostrato non ammissibile |
| `error` | errore di esecuzione o parsing |

## Calibrazione XLarge

La configurazione:

```text
configs/calibration/xlarge_calibration.yaml
```

genera sei istanze:

```math
1\text{ dimensione}
\cdot
2\text{ distribuzioni}
\cdot
3\text{ capacità}
=
6.
```

Dimensione:

| Comunità | Siti | Centrali | Variabili binarie |
|---:|---:|---:|---:|
| 600 | 150 | 15 | 90150 |

## Protocollo

Prima si verifica il runner sulla toy instance e sulla calibrazione già risolta:

```bash
python scripts/run_exact_toy.py
```

```bash
python scripts/run_exact_benchmark.py \
  --manifest instances/generated/intermediate_calibration/manifest.csv \
  --output results/raw/intermediate_calibration_exact_metrics.csv \
  --methods compact \
  --time-limit 60
```

Successivamente si generano le XLarge:

```bash
python scripts/generate_instances.py \
  --config configs/calibration/xlarge_calibration.yaml
```

e si eseguono:

```bash
python scripts/run_grasp_vnd_benchmark.py \
  --manifest instances/generated/xlarge_calibration/manifest.csv \
  --output results/raw/xlarge_calibration_grasp_vnd.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --stagnation-starts 20 \
  --time-limit 10
```

```bash
python scripts/run_exact_benchmark.py \
  --manifest instances/generated/xlarge_calibration/manifest.csv \
  --output results/raw/xlarge_calibration_exact.csv \
  --methods compact \
  --time-limit 60
```

L'analisi dei gap deve distinguere gli ottimi certificati dagli incumbent non certificati.

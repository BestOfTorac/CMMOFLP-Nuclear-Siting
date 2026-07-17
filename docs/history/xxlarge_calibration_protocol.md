# Calibrazione mirata XXLarge

## Obiettivo

La calibrazione XXLarge serve a verificare il comportamento dei metodi quando il modello compatto contiene circa 360 mila variabili binarie.

Dimensione:

| Comunità | Siti candidati | Centrali |
|---:|---:|---:|
| 1200 | 300 | 30 |

Variabili binarie:

```math
1200 \cdot 300 + 300 = 360300.
```

Vincoli:

```math
1 + 1200 + 1200 \cdot 300 + 2 \cdot 300 = 361801.
```

## Classi selezionate

Non vengono generate tutte le sei combinazioni. La calibrazione usa soltanto:

- `xxlarge_uniform_tight`;
- `xxlarge_uniform_medium`;
- `xxlarge_clustered_tight`.

Queste classi separano gli effetti di distribuzione geografica e capacità.

## Generazione

```bash
python scripts/generate_instances.py \
  --config configs/stress/xxlarge_uniform_tight.yaml

python scripts/generate_instances.py \
  --config configs/stress/xxlarge_uniform_medium.yaml

python scripts/generate_instances.py \
  --config configs/stress/xxlarge_clustered_tight.yaml
```

## Manifest unificato

```bash
python scripts/merge_manifests.py \
  instances/generated/xxlarge_uniform_tight/manifest.csv \
  instances/generated/xxlarge_uniform_medium/manifest.csv \
  instances/generated/xxlarge_clustered_tight/manifest.csv \
  --output instances/generated/xxlarge_calibration/manifest.csv
```

## Ispezione

```bash
python scripts/inspect_instance_manifest.py \
  instances/generated/xxlarge_calibration/manifest.csv
```

## GRASP-VND

Cinque seed per tre istanze:

```math
3 \cdot 5 = 15
```

esecuzioni.

```bash
python scripts/run_grasp_vnd_benchmark.py \
  --manifest instances/generated/xxlarge_calibration/manifest.csv \
  --output results/raw/xxlarge_calibration_grasp_vnd.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --stagnation-starts 20 \
  --time-limit 20
```

## Modello compatto

```bash
python scripts/run_exact_benchmark.py \
  --manifest instances/generated/xxlarge_calibration/manifest.csv \
  --output results/raw/xxlarge_calibration_exact.csv \
  --methods compact \
  --time-limit 60
```

## Interpretazione

Per le istanze chiuse all'ottimo si calcola il gap rispetto a `objective_value`.

Per le istanze terminate al time limit si registrano:

- incumbent;
- best bound;
- MIP gap;
- confronto tra H2 e incumbent;
- distanza di H2 dal best bound.

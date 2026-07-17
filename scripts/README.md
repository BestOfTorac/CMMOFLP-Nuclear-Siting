# Script

Gli script rappresentano l’interfaccia da riga di comando del progetto. Devono essere eseguiti dalla cartella principale del repository con l’ambiente virtuale attivo.

I tre runner principali hanno nomi generali e possono essere applicati a qualunque manifest: `run_baseline_benchmark.py`, `run_grasp_vnd_benchmark.py` e `run_exact_benchmark.py`.

## Comandi essenziali

### Validare una istanza

```bash
python scripts/check_instance.py instances/test/toy_instance_01.json
```

### Eseguire le euristiche sulla toy instance

```bash
python scripts/run_greedy.py
python scripts/run_local_search.py
python scripts/run_grasp_vnd.py
```

`run_grasp_vnd.py` accetta anche:

```bash
python scripts/run_grasp_vnd.py \
  --instance instances/test/toy_instance_01.json \
  --seed 42 \
  --starts 25 \
  --stagnation-starts 20 \
  --time-limit 5
```

### Generare istanze

```bash
python scripts/generate_instances.py \
  --config configs/benchmark/final_benchmark.yaml
```

Il comando genera i JSON e il relativo `manifest.csv` in:

```text
instances/generated/<experiment_name>/
```

Per rigenerare una cartella esistente:

```bash
python scripts/generate_instances.py \
  --config configs/benchmark/final_benchmark.yaml \
  --overwrite
```

## Analisi dello snapshot pubblicato

Il repository contiene i risultati definitivi in `results/final/raw/`. Per rigenerare le tabelle pubblicate:

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
```

Output predefiniti:

```text
results/final/summary/
results/final/ablation/
```

## Esecuzione di un benchmark

### Baseline greedy e local search

```bash
python scripts/run_baseline_benchmark.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_heuristics.csv
```

### GRASP-VND multi-seed

```bash
python scripts/run_grasp_vnd_benchmark.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_grasp_vnd.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --stagnation-starts 20 \
  --time-limit 20
```

### Metodi esatti

```bash
python scripts/run_exact_benchmark.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_exact.csv \
  --methods compact \
  --time-limit 60
```

I metodi esatti richiedono AMPL e un solver MIP configurato localmente. Il solver predefinito è Gurobi.

## Analisi di una nuova riproduzione

I runner salvano normalmente i nuovi output nell’area locale ignorata `results/raw/`. Per analizzarli senza modificare lo snapshot pubblicato:

```bash
python scripts/analyze_final_results.py \
  --heuristics results/raw/final_heuristics.csv \
  --grasp-vnd results/raw/final_grasp_vnd.csv \
  --exact results/raw/final_exact.csv \
  --output-dir results/processed/final

python scripts/analyze_ablation.py \
  --heuristics results/raw/final_heuristics.csv \
  --grasp-vnd results/raw/final_grasp_vnd.csv \
  --exact results/raw/final_exact.csv \
  --output-dir results/processed/ablation
```

## Utilità per manifest e istanze

| Script | Funzione |
|---|---|
| `inspect_instance_manifest.py` | Stima variabili, vincoli e numero di solve a soglia |
| `merge_manifests.py` | Unisce manifest generati separatamente |
| `generate_sample.py` | Genera un esempio semplice |
| `check_upper_bound_pilot.py` | Verifica l’upper bound sulle esecuzioni pilota |

## Analisi storiche e di calibrazione

| Script | Contenuto |
|---|---|
| `analyze_pilot_results.py` | Analisi delle baseline pilota |
| `analyze_exact_results.py` | Confronto dei metodi esatti |
| `analyze_heuristic_gaps.py` | Analisi dei gap euristici |
| `analyze_grasp_vnd_pilot.py` | Analisi multi-seed pilota |

Questi script documentano il percorso sperimentale. Le analisi definitive sono `analyze_final_results.py` e `analyze_ablation.py`.

## File AMPL `.run`

- `run_compact.run`: esecuzione manuale del modello compatto;
- `run_threshold_checks.run`: verifiche manuali del modello a soglia;
- `run_threshold_search.run`: ricerca manuale sulle soglie.

Gli script Python sono l’interfaccia principale per gli esperimenti automatizzati.

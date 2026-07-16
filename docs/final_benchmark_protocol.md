# Campagna sperimentale definitiva

## Obiettivo

La campagna definitiva valuta i metodi sulle dimensioni per le quali il comportamento è risultato stabile e riproducibile:

- `medium`;
- `large`;
- `xlarge`.

Le istanze `xxlarge` restano uno stress test separato e non fanno parte del benchmark principale.

## Struttura del benchmark

| Dimensione | Comunità | Siti candidati | Centrali |
|---|---:|---:|---:|
| medium | 100 | 30 | 5 |
| large | 300 | 75 | 10 |
| xlarge | 600 | 150 | 15 |

Per ogni dimensione vengono combinate:

- distribuzione `uniform`;
- distribuzione `clustered`;
- capacità `tight`;
- capacità `medium`;
- capacità `loose`;
- 5 istanze per classe.

Numero totale:

```math
3 \cdot 2 \cdot 3 \cdot 5 = 90.
```

## Metodi

### Baseline euristiche

- greedy capacitata;
- repair + local search 1-swap.

Una esecuzione deterministica per istanza:

```math
90 + 90 = 180
```

esecuzioni.

### Euristica avanzata

GRASP-VND con cinque seed:

```text
42
123
2026
31415
98765
```

Numero di esecuzioni:

```math
90 \cdot 5 = 450.
```

Parametri principali:

| Parametro | Valore |
|---|---:|
| start massimi | 100 |
| stagnazione | 20 start |
| time limit | 20 secondi |
| alpha | 0.30 |
| candidate list | 20 |
| repair node limit | 100000 |

### Modello compatto

Una esecuzione per istanza:

```math
90
```

esecuzioni, con time limit uniforme di 60 secondi.

### Metodo a soglia

Il metodo a soglia non viene applicato alle `xlarge`, perché può richiedere una risoluzione per ogni soglia candidata.

Verrà eventualmente mantenuto come verifica aggiuntiva sulle dimensioni più piccole.

## Generazione

```bash
python scripts/generate_instances.py \
  --config configs/final_benchmark.yaml
```

Output:

```text
instances/generated/final_benchmark/
instances/generated/final_benchmark/manifest.csv
```

## Ispezione

```bash
python scripts/inspect_instance_manifest.py \
  instances/generated/final_benchmark/manifest.csv
```

Valori attesi:

| Dimensione | Istanze | Variabili binarie | Vincoli |
|---|---:|---:|---:|
| medium | 30 | 3030 | 3161 |
| large | 30 | 22575 | 22951 |
| xlarge | 30 | 90150 | 90901 |

## Ordine delle esecuzioni

### 1. Baseline euristiche

```bash
python scripts/run_pilot_heuristics.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_heuristics.csv
```

### 2. GRASP-VND

```bash
python scripts/run_pilot_grasp_vnd.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_grasp_vnd.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --stagnation-starts 20 \
  --time-limit 20
```

### 3. Modello compatto

```bash
python scripts/run_pilot_exact.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_exact.csv \
  --methods compact \
  --time-limit 60
```

## Regole di interpretazione

### Compact ottimo

Quando:

```text
optimality_certified = True
```

il valore è un ottimo dimostrato e può essere usato come riferimento per il gap.

### Compact al time limit

Quando:

```text
termination_reason = time_limit
```

si distinguono:

- incumbent;
- best bound;
- MIP gap;
- assenza di incumbent.

L'incumbent non viene chiamato ottimo.

### GRASP-VND

Ogni seed è eseguito su una nuova istanza caricata dal JSON.

Le esecuzioni possono terminare per:

```text
upper_bound
stagnation
time_limit
time_limit_no_incumbent
max_starts
```

## Indicatori finali

### Qualità

- percentuale di soluzioni ammissibili;
- percentuale di ottimi;
- gap medio, mediano e massimo;
- best, average e worst seed;
- deviazione standard.

### Tempi

- runtime totale;
- tempo al best;
- tempo solver;
- speedup rispetto al compact.

### Robustezza

- fallimenti;
- time limit senza incumbent;
- repair tentati e riusciti;
- mosse 1-swap e 2-swap;
- arresti per upper bound e stagnazione.

### Effetti sperimentali

- crescita medium-large-xlarge;
- confronto uniform-clustered;
- confronto tight-medium-loose.

## Stress test XXLarge

Le tre istanze già generate restano separate:

```text
xxlarge_uniform_tight_001
xxlarge_uniform_medium_001
xxlarge_clustered_tight_001
```

Servono a mostrare i limiti del modello esatto e dell'euristica, non vengono replicate nel benchmark principale.

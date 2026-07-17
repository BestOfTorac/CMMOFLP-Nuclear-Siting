# Protocollo sperimentale

## Obiettivo

La valutazione confronta:

- modello compatto;
- metodo esatto a soglia nelle dimensioni più piccole;
- greedy;
- repair + local search 1-swap;
- GRASP-VND.

Gli indicatori principali sono:

- fattibilità;
- qualità della soluzione;
- ottimalità certificata;
- gap;
- runtime;
- tempo al best;
- motivo di arresto;
- robustezza tra seed.

## Fasi sperimentali

### Toy instance

Serve a verificare manualmente formulazione, modelli e implementazione.

Risultato noto:

\[
S^*=\{s1,s4\},
\qquad
z^*=18.0278.
\]

### Pilot tiny/small

36 istanze e 12 classi, utilizzate per:

- confrontare compact e threshold;
- valutare greedy e local search;
- validare la pipeline;
- testare GRASP-VND su cinque seed.

### Calibrazione medium/large

12 istanze, una per classe, usate per:

- scegliere le dimensioni;
- calibrare time limit e start;
- introdurre l’arresto per stagnazione;
- verificare la crescita del compact.

### Calibrazione XLarge

6 istanze da 600 comunità e 150 siti, usate per verificare scalabilità e metriche MIP.

### Stress test XXLarge

3 istanze da 1200 comunità e 300 siti, usate per osservare time limit, incumbent e assenza di incumbent.

### Benchmark finale

90 istanze medium, large e xlarge.

## Struttura del benchmark finale

| Dimensione | Comunità | Siti | Centrali | Binarie | Vincoli |
|---|---:|---:|---:|---:|---:|
| `medium` | 100 | 30 | 5 | 3030 | 3161 |
| `large` | 300 | 75 | 10 | 22575 | 22951 |
| `xlarge` | 600 | 150 | 15 | 90150 | 90901 |

Per ogni dimensione:

- due distribuzioni;
- tre livelli di capacità;
- cinque istanze per classe.

Classi complessive: 18.

## Esecuzioni

### Baseline

Una run greedy e una run local search per istanza:

\[
90+90=180.
\]

### GRASP-VND

Cinque seed:

```text
42
123
2026
31415
98765
```

Numero totale:

\[
90\cdot5=450.
\]

Parametri:

| Parametro | Valore |
|---|---:|
| start massimi | 100 |
| stagnazione | 20 start |
| time limit | 20 secondi |
| `alpha` | 0.30 |
| candidate list | 20 |
| repair node limit | 100000 |

### Compact

Una esecuzione per istanza:

\[
90.
\]

Time limit: 60 secondi.

## Comandi principali

Generazione:

```bash
python scripts/generate_instances.py \
  --config configs/final_benchmark.yaml
```

Baseline:

```bash
python scripts/run_pilot_heuristics.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_heuristics.csv
```

GRASP-VND:

```bash
python scripts/run_pilot_grasp_vnd.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_grasp_vnd.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --stagnation-starts 20 \
  --time-limit 20
```

Compact:

```bash
python scripts/run_pilot_exact.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_exact.csv \
  --methods compact \
  --time-limit 60
```

## Regole di interpretazione

### Ottimo compact

Un valore viene considerato ottimo soltanto quando:

```text
optimality_certified = True
```

### Time limit compact

Si riportano separatamente:

- incumbent;
- best bound;
- MIP gap;
- presenza o assenza di una soluzione intera.

### GRASP-VND

Ogni coppia istanza-seed è indipendente e ricarica il JSON.

Possibili motivi di arresto:

```text
upper_bound
stagnation
time_limit
time_limit_no_incumbent
max_starts
```

### Gap euristico

Per un ottimo noto \(z^*\) e una soluzione \(z_H\):

\[
gap_H
=
\frac{z^*-z_H}{|z^*|}\cdot100.
\]

Il gap non viene calcolato:

- quando l’ottimo non è certificato;
- quando l’euristica non trova una soluzione ammissibile.

## Aggregazione

I risultati vengono aggregati per:

- metodo;
- dimensione;
- distribuzione;
- livello di capacità;
- istanza;
- seed.

Per GRASP-VND vengono distinti:

- singola run;
- best, average e worst seed;
- best-of-5;
- tempo di una run;
- somma sequenziale dei cinque runtime.

## Analisi

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
```

Le tabelle vengono salvate in `results/processed/`.

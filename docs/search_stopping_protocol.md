# Arresto per stagnazione e deadline globale

## Motivazione

Nella calibrazione medium/large, GRASP-VND trovava spesso il miglior valore molto prima del termine dell'esecuzione. Quando l'upper bound non era tight, l'algoritmo continuava fino a 100 start o fino al time limit.

Sono stati introdotti due meccanismi:

1. arresto dopo un numero massimo di start consecutivi senza miglioramento dell'obiettivo maximin;
2. controlli della deadline dentro costruzione, 1-swap, 2-swap e repair.

## Stagnazione

Il parametro:

```text
max_starts_without_improvement
```

conta gli start consecutivi che non migliorano:

```math
z(S)=\min_{j\in S}r_j.
```

Il valore predefinito è:

```text
20
```

La somma delle sicurezze rimane uno spareggio, ma non azzera il contatore di stagnazione se il valore maximin non cresce.

L'esecuzione può terminare per:

```text
upper_bound
stagnation
time_limit
max_starts
```

Il motivo viene salvato in `stop_reason`.

## Deadline globale

La stessa deadline assoluta viene propagata a:

- local search deterministica;
- costruzione GRASP;
- ricerca 1-swap;
- ricerca 2-swap;
- backtracking di repair.

Il repair controlla la deadline a ogni nodo e solleva `TimeoutError`. Un insieme interrotto dal tempo non viene memorizzato in cache come non ammissibile.

Il limite rimane soggetto a un piccolo overhead finale per validazione e logging, ma non può più essere superato da un intero vicinato o da un backtracking prolungato.

## Nuovo logging

Ogni esecuzione registra:

```text
max_starts_without_improvement
starts_without_improvement
stagnation_stops
deadline_stops
stop_reason
```

## Esecuzione consigliata per la calibrazione

```bash
python scripts/run_pilot_grasp_vnd.py \
  --manifest instances/generated/intermediate_calibration/manifest.csv \
  --output results/raw/intermediate_calibration_grasp_vnd_stagnation.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --stagnation-starts 20 \
  --time-limit 10
```

Il confronto con la versione precedente deve verificare:

- stesso numero di soluzioni ottime;
- riduzione del tempo totale;
- riduzione degli start completati sulle istanze con upper bound non tight;
- rispetto più stretto del time limit.

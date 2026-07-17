# Pilot multi-seed di GRASP-VND

## Obiettivo

GRASP-VND contiene componenti randomizzate. Una singola esecuzione non è sufficiente per valutarne stabilità e qualità.

La pipeline esegue H2 con più seed algoritmici su ciascuna istanza pilota.

Seed iniziali:

```text
42
123
2026
31415
98765
```

Con 36 istanze e 5 seed vengono effettuate:

```math
36 \cdot 5 = 180
```

esecuzioni.

## Parametri iniziali

| Parametro | Valore |
|---|---:|
| start massimi | 100 |
| time limit | 10 secondi |
| alpha | 0.30 |
| candidate list | 20 |
| peso sicurezza | 0.80 |
| siti aperti secondari | 3 |
| limite nodi repair | 100000 |

Il time limit è un limite massimo. Quando viene raggiunto l'upper bound teorico, l'esecuzione termina anticipatamente.

## Esecuzione

```bash
python scripts/run_grasp_vnd_benchmark.py
```

Output:

```text
results/raw/pilot_grasp_vnd.csv
```

## Analisi

```bash
python scripts/history/analyze_grasp_vnd_pilot.py
```

Output:

```text
results/aggregated/grasp_vnd_by_seed.csv
results/aggregated/grasp_vnd_by_instance.csv
results/aggregated/grasp_vnd_by_class.csv
```

## Indicatori per seed

Per ogni esecuzione vengono registrati:

- valore obiettivo;
- gap rispetto al modello compatto;
- fattibilità;
- ottimalità;
- certificazione tramite upper bound;
- tempo totale e tempo al best;
- start completati;
- repair;
- mosse 1-swap e 2-swap.

## Indicatori per istanza

Sui diversi seed vengono calcolati:

- migliore, media e peggiore soluzione;
- deviazione standard dell'obiettivo;
- gap migliore, medio e peggiore;
- numero di esecuzioni ottime;
- numero di certificazioni;
- tempo medio e mediano;
- start medi completati.

Una deviazione standard nulla e l'ottimo su tutti i seed indicano stabilità rispetto alla randomizzazione.

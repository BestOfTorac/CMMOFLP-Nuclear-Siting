# Configurazioni

Le configurazioni YAML descrivono le classi di istanze sintetiche. Sono divise in base al ruolo sperimentale, così da distinguere immediatamente il benchmark definitivo dalle calibrazioni e dagli stress test.

```text
configs/
├── benchmark/
│   └── final_benchmark.yaml
├── calibration/
│   ├── pilot.yaml
│   ├── intermediate_calibration.yaml
│   └── xlarge_calibration.yaml
└── stress/
    ├── xxlarge_clustered_tight.yaml
    ├── xxlarge_uniform_medium.yaml
    └── xxlarge_uniform_tight.yaml
```

Ogni file specifica:

- nome dell’esperimento;
- numero di istanze per classe;
- seed di base;
- dimensioni;
- distribuzioni geografiche;
- livelli di capacità.

## Benchmark definitivo

### `benchmark/final_benchmark.yaml`

Genera:

- 30 istanze `medium`;
- 30 istanze `large`;
- 30 istanze `xlarge`;
- distribuzioni `uniform` e `clustered`;
- capacità `tight`, `medium` e `loose`;
- 5 istanze per classe.

Totale: **90 istanze in 18 classi**.

Esecuzione:

```bash
python scripts/generate_instances.py \
  --config configs/benchmark/final_benchmark.yaml
```

Senza `--config`, `generate_instances.py` usa questa configurazione come default.

## Calibrazione

### `calibration/pilot.yaml`

36 istanze `tiny` e `small`, usate per validare:

- generatore;
- modello compatto;
- metodo a soglia;
- greedy, repair e local search;
- prima versione di GRASP-VND.

### `calibration/intermediate_calibration.yaml`

12 istanze `medium` e `large`, usate per calibrare:

- numero di start;
- arresto per stagnazione;
- tempo al best;
- crescita del modello compatto.

### `calibration/xlarge_calibration.yaml`

6 istanze `xlarge`, usate per verificare:

- scalabilità;
- time limit;
- metriche MIP;
- comportamento multi-seed.

## Stress test

I file in `stress/` generano tre istanze XXLarge con:

- 1.200 comunità;
- 300 siti candidati;
- 30 centrali.

| File | Distribuzione | Capacità |
|---|---|---|
| `xxlarge_uniform_tight.yaml` | uniform | tight |
| `xxlarge_uniform_medium.yaml` | uniform | medium |
| `xxlarge_clustered_tight.yaml` | clustered | tight |

Queste istanze servono a osservare i limiti dei metodi e non appartengono al benchmark principale.

## Livelli di capacità

| Livello | Fattore |
|---|---:|
| `tight` | 1,05 |
| `medium` | 1,20 |
| `loose` | 1,50 |

Le classi `tight` sono risultate le più difficili.

## Output

Il generatore salva automaticamente le istanze in:

```text
instances/generated/<experiment_name>/
```

Per rigenerare una cartella esistente:

```bash
python scripts/generate_instances.py \
  --config <configurazione.yaml> \
  --overwrite
```

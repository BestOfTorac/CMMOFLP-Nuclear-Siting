# Configurazioni

I file YAML descrivono le classi di istanze sintetiche. Ogni configurazione specifica:

- nome dell’esperimento;
- numero di istanze per classe;
- seed di base;
- dimensioni;
- distribuzioni geografiche;
- livelli di capacità.

La generazione avviene con:

```bash
python scripts/generate_instances.py --config <file.yaml>
```

## Configurazione principale

### `final_benchmark.yaml`

Benchmark definitivo:

- 30 istanze `medium`;
- 30 istanze `large`;
- 30 istanze `xlarge`;
- distribuzioni `uniform` e `clustered`;
- capacità `tight`, `medium` e `loose`;
- 5 istanze per classe;
- 90 istanze complessive.

È la configurazione da usare per riprodurre la campagna finale.

## Calibrazione

### `pilot.yaml`

36 istanze `tiny` e `small`, utilizzate per validare modelli, generatore ed euristiche.

### `intermediate_calibration.yaml`

12 istanze `medium` e `large`, utilizzate per calibrare GRASP-VND e il criterio di stagnazione.

### `xlarge_calibration.yaml`

6 istanze `xlarge`, utilizzate per verificare scalabilità e gestione dei time limit.

## Stress test

- `xxlarge_uniform_tight.yaml`
- `xxlarge_uniform_medium.yaml`
- `xxlarge_clustered_tight.yaml`

Le configurazioni XXLarge generano istanze con:

- 1.200 comunità;
- 300 siti candidati;
- 30 centrali.

Queste istanze costituiscono uno stress test separato e non appartengono al benchmark principale.

## Configurazione storica

### `full_experiment.yaml`

Configurazione preliminare precedente alla definizione del benchmark finale. Non deve essere utilizzata come riferimento principale e verrà valutata durante la riorganizzazione del repository.

## Livelli di capacità

| Livello | Fattore |
|---|---:|
| `tight` | 1,05 |
| `medium` | 1,20 |
| `loose` | 1,50 |

Il fattore controlla la capacità totale disponibile rispetto alla domanda. Le classi `tight` sono risultate le più difficili.

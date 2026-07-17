# Benchmark intermedio: protocollo di calibrazione

## Obiettivo

Il benchmark intermedio serve a passare dalle istanze pilota, progettate per verificare correttezza e pipeline, a istanze abbastanza grandi da mostrare differenze significative tra metodi esatti ed euristici.

La prima attività è una calibrazione delle dimensioni e dei time limit, non ancora la campagna definitiva.

## Dimensioni iniziali

| Dimensione | Comunità | Siti candidati | Centrali |
|---|---:|---:|---:|
| medium | 100 | 30 | 5 |
| large | 300 | 75 | 10 |

Per il modello compatto:

```math
\text{variabili binarie}=|I||J|+|J|
```

e:

```math
\text{vincoli}=1+|I|+|I||J|+2|J|.
```

Ne segue:

| Dimensione | Variabili binarie | Variabile continua | Vincoli |
|---|---:|---:|---:|
| medium | 3030 | 1 | 3161 |
| large | 22575 | 1 | 22951 |

## Classi

La calibrazione combina:

- due dimensioni: `medium`, `large`;
- due distribuzioni: `uniform`, `clustered`;
- tre livelli di capacità: `tight`, `medium`, `loose`;
- una istanza per classe.

Numero complessivo:

```math
2 \cdot 2 \cdot 3 \cdot 1 = 12.
```

Le 12 istanze servono a decidere se le dimensioni sono adeguate prima di generare il benchmark da 60 istanze.

## Fattori di capacità

| Livello | Fattore |
|---|---:|
| tight | 1.05 |
| medium | 1.20 |
| loose | 1.50 |

Il generatore conserva una partizione garantita nei metadati, ma gli algoritmi non la utilizzano.

## Protocollo di calibrazione

### Passo 1 — Generazione

```bash
python scripts/generate_instances.py \
  --config configs/calibration/intermediate_calibration.yaml
```

Output:

```text
instances/generated/intermediate_calibration/
```

### Passo 2 — Ispezione strutturale

```bash
python scripts/inspect_instance_manifest.py \
  instances/generated/intermediate_calibration/manifest.csv
```

### Passo 3 — GRASP-VND

```bash
python scripts/run_grasp_vnd_benchmark.py \
  --manifest instances/generated/intermediate_calibration/manifest.csv \
  --output results/raw/intermediate_calibration_grasp_vnd.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --time-limit 10
```

### Passo 4 — Modello compatto

Si esegue soltanto il modello compatto con un time limit iniziale di 60 secondi:

```bash
python scripts/run_exact_benchmark.py \
  --manifest instances/generated/intermediate_calibration/manifest.csv \
  --output results/raw/intermediate_calibration_exact.csv \
  --methods compact \
  --time-limit 60
```

Il metodo a soglia non viene ancora eseguito sulle istanze large. L'implementazione attuale applica il time limit a ciascun problema di fattibilità e può effettuare un solve per ogni sito candidato. Prima della campagna definitiva deve essere introdotto un limite globale.

### Passo 5 — Analisi

```bash
python scripts/analyze_grasp_vnd_pilot.py \
  --grasp-results results/raw/intermediate_calibration_grasp_vnd.csv \
  --exact-results results/raw/intermediate_calibration_exact.csv \
  --seed-output results/aggregated/intermediate_grasp_vnd_by_seed.csv \
  --instance-output results/aggregated/intermediate_grasp_vnd_by_instance.csv \
  --class-output results/aggregated/intermediate_grasp_vnd_by_class.csv
```

## Criteri decisionali

Le dimensioni vengono confermate se:

- GRASP-VND completa tutte le esecuzioni senza errori;
- il modello compatto mostra una crescita apprezzabile rispetto al pilot;
- almeno alcune istanze richiedono più di pochi secondi, senza rendere impraticabile l'intera campagna;
- le classi tight risultano più difficili o meno frequentemente certificate;
- la memoria rimane sotto controllo.

| Risultato | Decisione |
|---|---|
| compact quasi sempre sotto 1 secondo | aumentare dimensioni o introdurre `xlarge` |
| compact tra 1 e 60 secondi | dimensioni adatte |
| numerosi time limit sulle medium | ridurre le dimensioni |
| time limit soprattutto sulle large | situazione utile per confrontare H2 e MIP |

## Campagna successiva

Solo dopo la calibrazione verrà creato `configs/intermediate.yaml` con cinque istanze per classe:

```math
2 \cdot 2 \cdot 3 \cdot 5 = 60.
```

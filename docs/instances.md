# Istanze e generatore

## Formati supportati

Le istanze principali sono archiviate in JSON. La toy instance dispone anche di un file DAT per AMPL.

## Struttura JSON

Campi principali:

```text
name
p
communities
sites
metadata
```

Ogni comunità contiene:

- `id`;
- coordinate `x`, `y`;
- `demand`.

Ogni sito contiene:

- `id`;
- coordinate `x`, `y`;
- `capacity`.

I metadati possono contenere:

- classe;
- dimensione;
- distribuzione;
- livello e fattore di capacità;
- seed;
- parametri geografici;
- informazioni di generazione.

## Validazione

Le istanze vengono controllate rispetto a:

- identificativi univoci;
- coordinate numeriche;
- domande positive;
- capacità positive;
- numero di siti almeno pari a \(p\);
- valore di \(p\) positivo;
- capacità totale potenzialmente sufficiente.

La condizione sulle \(p\) capacità maggiori è necessaria, ma la fattibilità a singola sorgente deve essere verificata dal solver o dal repair.

## Distanze

Le distanze vengono calcolate in modo euclideo dalle coordinate:

\[
d_{ij}
=
\sqrt{
(x_i-x_j)^2+(y_i-y_j)^2
}.
\]

## Generatore

Il generatore produce istanze pseudo-casuali riproducibili organizzate in classi.

Ogni classe è determinata da:

- dimensione;
- distribuzione geografica;
- livello di capacità.

### Distribuzione uniforme

Comunità e siti candidati sono distribuiti uniformemente nella regione.

### Distribuzione clustered

Le comunità vengono generate intorno a centri urbani con distribuzioni gaussiane. I siti candidati rimangono distribuiti nell’intera regione.

## Livelli di capacità

| Livello | Fattore |
|---|---:|
| `tight` | 1.05 |
| `medium` | 1.20 |
| `loose` | 1.50 |

Il fattore viene applicato ai carichi di un insieme di \(p\) siti anchor costruito internamente.

## Garanzia di fattibilità

Durante la generazione viene creata una partizione delle comunità tra \(p\) siti anchor. Le capacità di questi siti vengono impostate in modo coerente con il fattore scelto.

Questo garantisce l’esistenza di almeno una soluzione ammissibile con assegnamento a singola sorgente.

La partizione garantita:

- è memorizzata soltanto nei metadati;
- serve a validare il generatore;
- non viene letta dagli algoritmi risolutivi.

## Riproducibilità

Ogni istanza conserva il seed di generazione. Il manifest associa:

- `instance_id`;
- classe;
- dimensione;
- distribuzione;
- capacità;
- percorso JSON;
- seed.

## Generazione

```bash
python scripts/generate_instances.py \
  --config configs/final_benchmark.yaml
```

Per rigenerare una cartella:

```bash
python scripts/generate_instances.py \
  --config configs/final_benchmark.yaml \
  --overwrite
```

## Benchmark finale

| Dimensione | Comunità | Siti | Centrali | Istanze |
|---|---:|---:|---:|---:|
| `medium` | 100 | 30 | 5 | 30 |
| `large` | 300 | 75 | 10 | 30 |
| `xlarge` | 600 | 150 | 15 | 30 |

Ogni dimensione combina:

- `uniform` e `clustered`;
- `tight`, `medium` e `loose`;
- cinque istanze per classe.

Totale:

\[
3\cdot2\cdot3\cdot5=90.
\]

## Stress test XXLarge

Le tre istanze XXLarge hanno:

| Comunità | Siti | Centrali |
|---:|---:|---:|
| 1200 | 300 | 30 |

Sono state usate soltanto per analizzare i limiti dei metodi e non fanno parte del benchmark principale.

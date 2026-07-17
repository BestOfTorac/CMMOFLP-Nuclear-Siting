# Esperimenti pilota

## Obiettivo

La pipeline pilota esegue automaticamente le euristiche sulle istanze elencate nel manifest prodotto dal generatore.

In questa prima sottofase vengono eseguiti:

- `greedy`;
- `local_search`.

I metodi esatti verranno integrati successivamente tramite AMPL.

## Dati registrati

Per ogni combinazione istanza-metodo vengono salvati:

- identificativo dell'istanza;
- classe;
- dimensione;
- distribuzione geografica;
- livello di capacità;
- seed;
- metodo;
- stato;
- fattibilità;
- valore obiettivo;
- tempo di esecuzione;
- siti aperti;
- iterazioni della local search;
- valore iniziale della local search;
- eventuale errore.

## Esecuzione

Prima generare le istanze:

```bash
python scripts/generate_instances.py --config configs/pilot.yaml
```

Poi eseguire le euristiche:

```bash
python scripts/run_pilot_heuristics.py
```

Il file prodotto è:

```text
results/raw/pilot_heuristics.csv
```

La cartella dei risultati grezzi è esclusa da Git perché i dati possono essere rigenerati.

## Scopo del pilot

La campagna pilota serve a:

- verificare la pipeline;
- controllare la fattibilità delle euristiche;
- misurare ordini di grandezza dei tempi;
- individuare classi troppo facili o troppo difficili;
- calibrare le dimensioni della campagna definitiva.

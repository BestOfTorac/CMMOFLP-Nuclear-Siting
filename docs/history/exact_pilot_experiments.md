# Esperimenti pilota con i metodi esatti

## Obiettivo

La pipeline esegue tramite AMPL CLI:

- modello compatto PLI;
- metodo esatto a soglia.

Le istanze JSON vengono convertite automaticamente in file `.dat` temporanei.

## Tempi registrati

Per ogni esecuzione vengono misurati:

- `runtime_seconds`: tempo end-to-end osservato da Python, comprensivo di avvio di AMPL, caricamento del modello e risoluzione;
- `solver_time_seconds`: tempo riportato da AMPL per il solver.

Il tempo end-to-end è il riferimento principale per confrontare implementazioni complete.

## Esecuzione

Dopo aver generato le istanze pilota:

```bash
python scripts/run_pilot_exact.py
```

Il risultato viene salvato in:

```text
results/raw/pilot_exact.csv
```

È possibile cambiare solver o time limit:

```bash
python scripts/run_pilot_exact.py --solver gurobi --time-limit 300
```

## Test automatici

I test della pipeline verificano:

- esportazione dei dati AMPL;
- parsing dei marker prodotti dagli script;
- gestione degli output non validi.

GitHub Actions non esegue AMPL, perché il software e la licenza sono disponibili nell'ambiente locale degli autori.

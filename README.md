# CMMOFLP Nuclear Siting

Studio computazionale del **Capacitated Multiple Maximin Obnoxious Facility Location Problem (CMMOFLP)** applicato alla localizzazione di centrali nucleari.

> Stato del progetto: struttura iniziale del repository. Modelli, algoritmi ed esperimenti verranno aggiunti e validati progressivamente.

## Descrizione

Si considerano un insieme di comunità con domanda energetica, un insieme di siti candidati, una capacità produttiva per ogni sito e un numero prefissato `p` di centrali da costruire.

L'obiettivo è selezionare i siti, assegnare ogni comunità a una centrale aperta e rispettare le capacità, massimizzando la minima distanza tra qualunque comunità e qualunque centrale costruita.

L'assegnazione energetica serve a verificare le capacità. La distanza di sicurezza deve invece considerare tutte le centrali aperte.

## Obiettivi

1. definizione formale del problema;
2. due metodi esatti;
3. euristica greedy di riferimento;
4. euristica migliorata con riparazione e ricerca locale;
5. generazione di classi di istanze riproducibili;
6. campagna sperimentale;
7. confronto tra qualità e tempi;
8. relazione e presentazione.

## Metodi previsti

- **M1 — Modello compatto PLI**
- **M2 — Metodo esatto a soglia**
- **H1 — Greedy baseline**
- **H2 — Local search**

## Struttura

```text
.
├── configs/        configurazioni degli esperimenti
├── docs/           specifica, piano di lavoro, relazione, slide e riferimenti
├── instances/      istanze di test e istanze generate
├── models/         modelli matematici
├── results/        risultati grezzi, aggregati e grafici
├── scripts/        comandi di utilità
├── src/            codice sorgente Python
└── tests/          test automatici
```

## Avvio rapido

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
python scripts/check_instance.py instances/test/toy_instance_01.json
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
python scripts/check_instance.py instances/test/toy_instance_01.json
```

## Convenzioni

- README, documentazione e descrizioni in italiano;
- cartelle, file, classi, funzioni e variabili in inglese;
- seed e configurazioni sempre salvati;
- nessuna credenziale o licenza locale nel repository;
- risultati grezzi mai modificati manualmente.

## Documentazione

- [Definizione del problema](docs/problem_definition.md)
- [Piano di sviluppo](docs/development_plan.md)
- [Protocollo sperimentale](docs/experimental_protocol.md)
- [Formato delle istanze](docs/instance_format.md)

## Autori

- Valerio Torac
- Ali Shalby

## Licenza

La licenza non è ancora stata definita. Prima della pubblicazione sarà necessario sceglierne una compatibile con il materiale e le dipendenze usate.

# CMMOFLP Nuclear Siting

**Versione del progetto: 1.0.0**

[![Tests](https://github.com/BestOfTorac/CMMOFLP-Nuclear-Siting/actions/workflows/tests.yml/badge.svg)](https://github.com/BestOfTorac/CMMOFLP-Nuclear-Siting/actions/workflows/tests.yml)

Studio computazionale del **Capacitated Multiple Maximin Obnoxious Facility Location Problem (CMMOFLP)** applicato alla localizzazione discreta di centrali nucleari.

Il progetto è stato sviluppato per il corso di **Algoritmi e Modelli di Ottimizzazione Discreta (AMOD)** dell’Università degli Studi di Roma Tor Vergata.

## Il problema

Sono dati:

- un insieme di comunità con domanda energetica;
- un insieme di siti candidati;
- la capacità produttiva associata a ciascun sito;
- un numero prefissato `p` di centrali da costruire.

Ogni comunità deve essere assegnata a una centrale aperta e le capacità produttive devono essere rispettate. L’obiettivo consiste nel massimizzare la distanza di sicurezza minima tra le comunità e tutte le centrali costruite.

Per un insieme di siti aperti \(S\), il valore della soluzione è:

\[
z(S)=\min_{j\in S}\min_{i\in I} d_{ij}.
\]

L’assegnamento energetico viene utilizzato per verificare la fattibilità rispetto alle capacità. La distanza di sicurezza dipende invece da **tutte** le centrali aperte, non soltanto dalla centrale assegnata a ciascuna comunità.

## Metodi implementati

| Metodo | Tipo | Ruolo |
|---|---|---|
| Modello compatto | PLI esatta in AMPL | Risoluzione e certificazione dell’ottimo |
| Metodo a soglia | Sequenza di problemi di fattibilità | Verifica esatta su istanze piccole |
| Greedy capacitata | Euristica costruttiva | Baseline rapida |
| Repair + 1-swap | Euristica migliorativa | Recupero della fattibilità e ricerca locale |
| GRASP-VND | Euristica multi-start | Metodo euristico principale |

GRASP-VND combina costruzione randomizzata, repair capacitato, cache degli assegnamenti, vicinati 1-swap e 2-swap mirato, arresto per stagnazione e certificazione tramite upper bound quando possibile.

## Risultati principali

La campagna finale comprende **90 istanze**, suddivise tra dimensioni `medium`, `large` e `xlarge`, distribuzioni `uniform` e `clustered`, e capacità `loose`, `medium` e `tight`.

| Indicatore | Risultato |
|---|---:|
| Test automatici | 62 superati |
| Incumbent trovati dal modello compatto | 90/90 |
| Ottimi certificati dal modello compatto | 89/90 |
| Run GRASP-VND ammissibili | 449/450 |
| Istanze con ottimo noto risolte da GRASP-VND best-of-5 | 85/89 |
| Errori software nella campagna finale | 0 |

Le capacità `tight` rappresentano il principale fattore di difficoltà. La local search 1-swap applicata isolatamente non ha migliorato la greedy, mentre GRASP-VND ha aumentato sensibilmente robustezza e qualità.

L’analisi completa è disponibile in [`docs/results.md`](docs/results.md).

## Struttura del repository

```text
.
├── configs/        configurazioni di benchmark, calibrazione e stress test
├── docs/           problema, modelli, metodi, esperimenti e risultati
├── instances/      toy instance e istanze generate localmente
├── models/         modelli AMPL
├── results/        output grezzi, aggregazioni e grafici
├── scripts/        comandi per esecuzione e analisi
├── src/            package Python
└── tests/          test automatici
```

## Requisiti

### Funzioni Python ed euristiche

- Python 3.10 o successivo;
- dipendenze elencate in `requirements.txt`.

### Metodi esatti

Per eseguire il modello compatto e il metodo a soglia sono inoltre necessari:

- AMPL;
- un solver MIP compatibile, utilizzato nel progetto con Gurobi;
- licenze configurate localmente.

Nessuna licenza o credenziale è inclusa nel repository.

## Installazione

### Windows — Prompt dei comandi

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -W error::FutureWarning
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -W error::FutureWarning
```

## Avvio rapido

Validazione della toy instance:

```bash
python scripts/check_instance.py instances/test/toy_instance_01.json
```

Esecuzione della greedy:

```bash
python scripts/run_greedy.py
```

Esecuzione della local search:

```bash
python scripts/run_local_search.py
```

Esecuzione di GRASP-VND:

```bash
python scripts/run_grasp_vnd.py \
  --instance instances/test/toy_instance_01.json \
  --seed 42 \
  --starts 25 \
  --stagnation-starts 20 \
  --time-limit 5
```

Su Windows `cmd`, lo stesso comando può essere scritto su una sola riga.

## Riproduzione del benchmark finale

Generazione delle 90 istanze:

```bash
python scripts/generate_instances.py \
  --config configs/benchmark/final_benchmark.yaml
```

Esecuzione delle baseline:

```bash
python scripts/run_baseline_benchmark.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_heuristics.csv
```

Esecuzione di GRASP-VND con cinque seed:

```bash
python scripts/run_grasp_vnd_benchmark.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_grasp_vnd.csv \
  --algorithm-seeds 42 123 2026 31415 98765 \
  --starts 100 \
  --stagnation-starts 20 \
  --time-limit 20
```

Esecuzione del modello compatto:

```bash
python scripts/run_exact_benchmark.py \
  --manifest instances/generated/final_benchmark/manifest.csv \
  --output results/raw/final_exact.csv \
  --methods compact \
  --time-limit 60
```

Analisi finale:

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
```

La campagna completa richiede AMPL e Gurobi per il metodo esatto. Le istanze generate e gli output intermedi non vengono versionati automaticamente.

## Documentazione

Il punto di accesso principale è:

- [Indice della documentazione](docs/index.md)

Documenti essenziali:

- [Problema e formulazione](docs/problem.md)
- [Modelli matematici esatti](docs/mathematical_models.md)
- [Euristiche](docs/heuristics.md)
- [Istanze e generatore](docs/instances.md)
- [Protocollo sperimentale](docs/experiments.md)
- [Risultati](docs/results.md)
- [Note di implementazione](docs/implementation_notes.md)
- [Soluzione della toy instance](docs/toy_instance_solution.md)

Per i comandi disponibili:

- [Guida agli script](scripts/README.md)
- [Guida alle configurazioni](configs/README.md)
- [Modelli AMPL](models/README.md)
- [Organizzazione dei risultati](results/README.md)

## Autori

- Valerio Torac
- Ali Shalby

## Stato del progetto

Lo sviluppo algoritmico, la campagna sperimentale e la pubblicazione dei risultati definitivi sono conclusi. Le attività residue riguardano la generazione dei grafici finali, la preparazione della relazione di studio e la realizzazione delle slide.

## Licenza

La licenza del repository deve ancora essere formalizzata. Il codice e la documentazione non devono essere riutilizzati assumendo implicitamente una licenza open source.

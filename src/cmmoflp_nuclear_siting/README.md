# Package `cmmoflp_nuclear_siting`

Questa cartella contiene l’implementazione Python del progetto.

Gli script presenti nella cartella `scripts/` rappresentano i comandi da terminale, mentre il codice effettivo degli algoritmi, della generazione delle istanze e della pipeline sperimentale si trova in questo package.

## Struttura

```text
cmmoflp_nuclear_siting/
├── analysis/
├── core/
├── exact/
├── experiments/
├── generation/
├── heuristics/
├── __init__.py
└── README.md
```

## `core/`

Contiene le strutture dati fondamentali del progetto.

Si occupa di:

- rappresentare comunità e siti candidati;
- caricare e validare le istanze;
- rappresentare le soluzioni;
- verificare assegnamenti, capacità e valore obiettivo.

Gli altri moduli del progetto utilizzano queste strutture condivise.

## `generation/`

Contiene il generatore delle istanze sintetiche.

Gestisce:

- distribuzioni uniformi e clustered;
- domande delle comunità;
- capacità dei siti;
- livelli `tight`, `medium` e `loose`;
- seed di generazione;
- partizione interna che garantisce la fattibilità;
- esportazione delle istanze JSON e del manifest.

## `heuristics/`

Contiene gli algoritmi euristici implementati nel progetto:

- Greedy capacitata;
- procedura di repair;
- local search 1-swap;
- GRASP-VND con 1-swap e 2-swap mirato.

Questi moduli selezionano i siti aperti e cercano un assegnamento ammissibile delle comunità.

## `exact/`

Contiene l’integrazione tra Python, AMPL e il solver MIP.

Gestisce:

- esecuzione del modello Compact;
- esecuzione del metodo Threshold;
- esportazione dei dati verso AMPL;
- lettura degli output del solver;
- incumbent;
- best bound;
- MIP gap;
- certificazione dell’ottimalità;
- motivi di terminazione.

I modelli matematici AMPL si trovano nella cartella principale `models/`.

## `experiments/`

Contiene la logica per eseguire gli algoritmi su interi manifest di istanze.

Si occupa di:

- caricare le istanze del benchmark;
- eseguire le baseline;
- eseguire GRASP-VND su più seed;
- eseguire i metodi esatti;
- raccogliere tempi, obiettivi e stati;
- esportare i risultati in formato CSV.

I comandi utilizzabili da terminale si trovano nella cartella principale `scripts/`.

## `analysis/`

Contiene le funzioni di supporto per analizzare i risultati finali.

Include strumenti per:

- calcolare gap e confronti tra metodi;
- aggregare le esecuzioni GRASP-VND;
- analizzare la complessità delle istanze;
- supportare la produzione delle tabelle finali.

I risultati pubblicati si trovano nella cartella principale `results/`.

## `__init__.py`

Definisce `cmmoflp_nuclear_siting` come package Python.

Permette agli script e ai test di importare i moduli tramite istruzioni come:

```python
from cmmoflp_nuclear_siting.core import ...
from cmmoflp_nuclear_siting.heuristics import ...
```

## Flusso principale

Il flusso generale del progetto è:

```text
generation
    ↓
istanze JSON e manifest
    ↓
core
    ↓
exact / heuristics
    ↓
experiments
    ↓
risultati CSV
    ↓
analysis
```

In particolare:

1. `generation` crea le istanze;
2. `core` le carica e le valida;
3. `exact` e `heuristics` risolvono il problema;
4. `experiments` esegue i benchmark;
5. `analysis` produce confronti e sintesi.

## Separazione tra package e script

La separazione adottata è:

```text
src/cmmoflp_nuclear_siting/
```

per il codice riutilizzabile, mentre:

```text
scripts/
```

contiene i comandi eseguibili da terminale.

Questa organizzazione evita di duplicare la logica algoritmica e permette di utilizzare gli stessi moduli nei benchmark, nei test e nelle esecuzioni singole.

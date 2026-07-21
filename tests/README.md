# Test

Questa cartella contiene i test automatici del progetto.

I test verificano la correttezza delle strutture dati, della generazione delle istanze, dei metodi euristici, dei runner sperimentali, dell’integrazione AMPL e delle funzioni di analisi.

## Obiettivi

La suite di test serve a controllare:

- caricamento e validazione delle istanze;
- rappresentazione e validazione delle soluzioni;
- generazione riproducibile delle istanze;
- correttezza della Greedy capacitata;
- funzionamento del repair;
- local search 1-swap;
- GRASP-VND e relativi criteri di arresto;
- indipendenza delle esecuzioni tra seed;
- gestione delle deadline;
- classificazione delle esecuzioni senza incumbent;
- acquisizione delle metriche MIP;
- calcolo dei gap e aggregazione dei risultati;
- comportamento dei runner sperimentali;
- correttezza della toy instance.

## Organizzazione

I file seguono la convenzione:

```text
test_<componente>.py
```

Ogni file raccoglie test dedicati a una specifica parte del progetto.

Le principali categorie sono:

| Categoria | Contenuto verificato |
|---|---|
| Core | istanze, soluzioni e validazione |
| Generazione | generatori, seed, manifest e fattibilità |
| Euristiche | Greedy, repair, local search e GRASP-VND |
| Metodi esatti | runner AMPL, Threshold e metriche MIP |
| Esperimenti | runner, seed indipendenti e stati di arresto |
| Analisi | gap, aggregazioni e complessità delle istanze |

## Esecuzione completa

Dalla cartella principale del repository, con l’ambiente virtuale attivo:

```bash
pytest
```

Per un output più compatto:

```bash
pytest -q
```

## Esecuzione di un singolo file

Esempio:

```bash
pytest tests/test_grasp_vnd.py
```

## Esecuzione di un singolo test

Esempio:

```bash
pytest tests/test_grasp_vnd.py::nome_del_test
```

## Output dettagliato

Per visualizzare il nome di ogni test:

```bash
pytest -v
```

Per mostrare anche gli output prodotti durante l’esecuzione:

```bash
pytest -s
```

Le due opzioni possono essere combinate:

```bash
pytest -v -s
```

## Test AMPL

I test automatici non richiedono necessariamente una licenza AMPL o Gurobi attiva.

Le componenti di integrazione vengono verificate tramite:

- esportazione dei dati;
- parsing degli output;
- gestione degli stati del solver;
- output controllati o simulati.

Le esecuzioni reali dei modelli Compact e Threshold richiedono invece AMPL e un solver MIP configurato localmente.

## GitHub Actions

La suite Python viene eseguita automaticamente dalla pipeline di GitHub Actions.

La CI controlla che le modifiche non introducano regressioni nelle componenti principali del progetto.

## Aggiungere un nuovo test

Un nuovo file deve:

1. essere inserito nella cartella `tests/`;
2. avere un nome che inizi con `test_`;
3. contenere funzioni il cui nome inizi con `test_`;
4. verificare un comportamento specifico;
5. evitare dipendenze da risultati casuali non controllati;
6. usare seed espliciti quando è presente casualità.

Esempio minimale:

```python
def test_example():
    obtained = 2 + 2
    expected = 4

    assert obtained == expected
```

## Convenzioni

- ogni test deve essere indipendente dagli altri;
- i file temporanei devono essere creati in cartelle temporanee;
- i seed devono essere espliciti;
- i confronti numerici devono usare tolleranze adeguate;
- un test deve fallire quando il comportamento osservato non coincide con quello atteso;
- i test non devono modificare i risultati ufficiali contenuti in `results/final/`.

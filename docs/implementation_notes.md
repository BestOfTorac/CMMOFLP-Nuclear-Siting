# Note di implementazione

Questo documento raccoglie le principali decisioni tecniche introdotte per garantire correttezza e robustezza sperimentale. Non rappresentano nuove euristiche, ma correzioni o regole di esecuzione.

## Esecuzioni indipendenti tra seed

Ogni coppia `(istanza, seed)` deve essere indipendente.

La pipeline ricarica il JSON per ciascun seed:

```text
riga del manifest
→ nuova ProblemInstance
→ esecuzione del seed
→ eliminazione dell’oggetto
→ nuova lettura per il seed successivo
```

Questo impedisce che cache o mutazioni interne influenzino le run successive.

## Limite di ricorsione del repair

Il repair usa backtracking ricorsivo. La profondità può raggiungere il numero di comunità.

Nelle istanze con 1200 comunità, il limite standard di Python poteva causare:

```text
maximum recursion depth exceeded
```

La procedura aumenta temporaneamente il limite a:

```text
numero_comunità + 200
```

e ripristina il valore precedente al termine.

La logica algoritmica non cambia.

## Deadline globale

Una sola deadline assoluta viene propagata a:

- costruzione GRASP;
- local search;
- 1-swap;
- 2-swap;
- repair.

Il repair controlla la deadline a ogni nodo e può sollevare `TimeoutError`.

Un insieme interrotto dal tempo non viene memorizzato in cache come non ammissibile, perché la ricerca non è stata completata.

## Arresto per stagnazione

Il contatore:

```text
max_starts_without_improvement
```

misura gli start consecutivi che non aumentano:

\[
z(S)=\min_{j\in S}r_j.
\]

Il valore del benchmark finale è 20.

La somma delle sicurezze è usata come spareggio, ma non azzera la stagnazione quando il valore maximin rimane invariato.

## Classificazione delle esecuzioni senza incumbent

La pipeline distingue:

| Stato | Significato |
|---|---|
| `success` | soluzione ammissibile disponibile |
| `limit` | time limit senza incumbent |
| `no_incumbent` | ricerca conclusa senza incumbent prima del limite |
| `error` | eccezione software inattesa |

Quando GRASP-VND raggiunge il time limit senza una soluzione:

```text
status = limit
feasible = False
stop_reason = time_limit_no_incumbent
error = vuoto
```

Un fallimento algoritmico non viene quindi confuso con un errore software.

## Metriche MIP

Il runner AMPL acquisisce:

```text
objective_value
best_bound
relative_mip_gap
absolute_mip_gap
has_incumbent
optimality_certified
termination_reason
solver_time_seconds
runtime_seconds
```

Un incumbent al time limit resta una soluzione ammissibile non certificata.

## Tolleranze numeriche

Le analisi trattano come zero valori con errore assoluto inferiore a:

```text
1e-7
```

I confronti interni alle euristiche usano tolleranze più strette per evitare miglioramenti numericamente fittizi.

## Validazione delle soluzioni

Ogni soluzione viene verificata rispetto a:

- numero di siti aperti;
- completezza degli assegnamenti;
- assegnamenti verso siti aperti;
- capacità;
- coerenza del valore obiettivo.

Il runner registra `invalid` quando una soluzione viene prodotta ma non supera la validazione.

## GitHub Actions

La CI esegue i test Python, ma non AMPL e Gurobi, perché software e licenze non sono disponibili nell’ambiente GitHub Actions.

Le componenti AMPL sono coperte da test di esportazione, parsing e gestione degli stati mediante output controllati.

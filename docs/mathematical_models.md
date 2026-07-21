# Modelli matematici esatti

Il progetto implementa due metodi esatti in AMPL:

1. modello compatto;
2. metodo di fattibilità a soglia.

Entrambi usano lo stesso assegnamento capacitato e la stessa definizione di sicurezza.

## Modello compatto

Il modello [`models/compact.mod`](../models/compact.mod) ottimizza direttamente la variabile continua $z$.

Le variabili sono:

- $|J|$ variabili binarie di apertura;
- $|I||J|$ variabili binarie di assegnamento;
- una variabile continua $z$.

Il numero di variabili binarie è:

```math
|I||J|+|J|.
```

Nell’implementazione, il numero di vincoli è:

```math
1+|I|+|I||J|+2|J|.
```

Il modello compatto è il riferimento esatto principale perché, nelle verifiche pilota, ha restituito gli stessi ottimi del metodo a soglia con tempi inferiori.

### Esecuzione

```bash
python scripts/run_exact_benchmark.py \
  --manifest <manifest.csv> \
  --output <results.csv> \
  --methods compact \
  --time-limit 60
```

## Metodo a soglia

Il modello [`models/threshold.mod`](../models/threshold.mod) riceve una soglia $\tau$ e verifica se esiste una soluzione ammissibile con:

```math
z(S)\ge \tau.
```

Per ogni sito:

```math
\tau y_j\le r_j.
```

Se il sito è aperto, deve avere sicurezza almeno pari alla soglia.

Le soglie candidate sono i valori distinti $r_j$. Il metodo verifica le soglie in ordine e individua il massimo valore ammissibile.

### Vantaggi

- modello semplice di sola fattibilità;
- utile per validare il modello compatto;
- interpretazione immediata della soluzione.

### Limiti

Nel caso peggiore può richiedere un solve per ogni soglia candidata. Per questo è stato usato soprattutto sulla toy instance e nel pilot, non sulle classi XLarge del benchmark finale.

## Metriche MIP

Per ogni esecuzione del modello compatto vengono registrati:

- `objective_value`: migliore incumbent intero;
- `best_bound`: miglior bound duale;
- `relative_mip_gap`;
- `absolute_mip_gap`;
- `has_incumbent`;
- `optimality_certified`;
- `termination_reason`;
- `solver_time_seconds`;
- runtime end-to-end.

Per un problema di massimizzazione:

```math
\text{absolute gap}
=
|\text{best bound}-\text{incumbent}|
```

e:

```math
\text{relative gap}
=
\frac{\text{absolute gap}}
{|\text{incumbent}|}.
```

Un incumbent trovato al time limit è una soluzione ammissibile, ma non viene chiamato ottimo.

## Stati interpretati

| Condizione | Significato |
|---|---|
| `optimality_certified = True` | ottimo dimostrato |
| incumbent con `time_limit` | soluzione ammissibile non certificata |
| nessun incumbent con `time_limit` | nessuna soluzione intera disponibile |
| `infeasible` | problema dimostrato non ammissibile |
| `error` | errore di esecuzione o parsing |

## Ruolo nella sperimentazione

Il compact è stato usato per:

- validare la toy instance;
- confrontare i metodi esatti nel pilot;
- certificare gli ottimi del benchmark finale;
- calcolare i gap reali delle euristiche;
- produrre incumbent e bound negli stress test.

Il metodo a soglia ha avuto principalmente un ruolo di verifica indipendente nelle dimensioni più piccole.
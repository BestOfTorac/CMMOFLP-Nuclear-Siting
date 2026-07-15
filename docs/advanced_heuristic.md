# Euristica avanzata H2: GRASP con VND e riparazione

## Obiettivo

H2 deve migliorare la qualità e la robustezza della baseline greedy, mantenendo tempi molto inferiori rispetto ai modelli esatti.

La struttura adottata è:

```text
GRASP multi-start
→ costruzione randomizzata con RCL
→ assegnamento best-fit
→ repair capacitato
→ VND con 1-swap e 2-swap mirato
→ migliore soluzione globale
```

## Costruzione GRASP

Per ogni start viene costruito un insieme di `p` siti.

A ogni passo:

1. vengono esclusi i candidati che renderebbero impossibile raggiungere la capacità totale;
2. si calcola un punteggio normalizzato basato su sicurezza e capacità;
3. si costruisce una Restricted Candidate List;
4. si estrae casualmente un sito dalla RCL.

Il parametro `alpha` controlla la randomizzazione:

- `alpha = 0`: comportamento quasi greedy;
- valori intermedi: compromesso tra qualità e diversificazione;
- `alpha = 1`: RCL molto ampia.

## Fattibilità e repair

Per ogni insieme di siti:

1. si applicano condizioni necessarie sulla capacità;
2. si tenta il best-fit decreasing;
3. se fallisce, si usa il backtracking limitato;
4. se la riparazione fallisce, la soluzione viene scartata.

Gli assegnamenti vengono memorizzati in cache usando l'insieme dei siti aperti come chiave.

## Variable Neighborhood Descent

### Primo vicinato: 1-swap

Viene rimosso un sito aperto e inserito un sito chiuso.

La ricerca considera prioritariamente i siti aperti con sicurezza minore e una lista limitata di siti entranti promettenti.

### Secondo vicinato: 2-swap mirato

Il 2-swap viene applicato ai siti critici:

```math
C(S)=\{j\in S:r_j=z(S)\}.
```

Se esistono due siti critici, entrambi devono essere rimossi per aumentare il valore maximin.

Se esiste un solo sito critico, viene abbinato a uno dei siti con sicurezza immediatamente successiva.

Il vicinato non enumera tutte le combinazioni possibili: usa una candidate list dei migliori siti chiusi.

## Criterio di accettazione

Una mossa viene accettata soltanto quando migliora strettamente l'obiettivo maximin.

Tra più mosse migliorative, le soluzioni sono confrontate lessicograficamente tramite:

```math
\left(
\min_{j\in S}r_j,
\sum_{j\in S}r_j
\right).
```

Il primo componente è l'obiettivo reale. Il secondo serve soltanto come spareggio tra mosse che migliorano il primo.

## Multi-start

Il primo start utilizza la local search deterministica già sviluppata.

Gli start successivi utilizzano la costruzione GRASP.

L'algoritmo termina quando raggiunge:

- il numero massimo di start;
- oppure il limite di tempo.

## Parametri iniziali

| Parametro | Valore iniziale |
|---|---:|
| `alpha` | 0.30 |
| `max_starts` | 25 |
| `time_limit_seconds` | 5 |
| `candidate_list_size` | 20 |
| `max_iterations_per_start` | 50 |
| `repair_node_limit` | 100000 |
| `safety_weight` | 0.80 |
| `secondary_open_limit` | 3 |

I parametri saranno calibrati nel benchmark intermedio.


## Arresto anticipato e certificato di ottimalità

Ordinando le sicurezze dei siti in ordine decrescente:

```math
r_{(1)} \ge r_{(2)} \ge \dots \ge r_{(|J|)},
```

dovendo aprire esattamente `p` siti vale l'upper bound:

```math
z^* \le r_{(p)}.
```

Il bound ignora i vincoli di capacità, quindi può non essere raggiungibile, ma rimane valido.

Quando GRASP-VND trova una soluzione ammissibile con:

```math
z(S)=r_{(p)},
```

la soluzione è necessariamente ottima e il multi-start viene interrotto immediatamente.

Nel logging vengono registrati:

- `objective_upper_bound`;
- `upper_bound_reached`;
- `optimality_certified_by_upper_bound`.


## Logging

Per ogni esecuzione vengono registrati:

- seed algoritmico;
- start tentati, completati, riusciti e falliti;
- repair tentati e riusciti;
- mosse 1-swap e 2-swap;
- cache hit e miss;
- iterazioni VND;
- tempo al best;
- tempo totale.

Poiché H2 è randomizzato, nella campagna finale dovrà essere eseguito con più seed algoritmici per ogni istanza.

# Definizione formale del problema

## 1. Nome adottato nel progetto

Nel progetto il problema viene indicato come:

**Capacitated Multiple Maximin Obnoxious Facility Location Problem for Nuclear Power Plant Siting**.

L'applicazione considerata riguarda la localizzazione discreta di più centrali nucleari capacitate.

---

## 2. Scenario applicativo

Un'autorità deve scegliere un numero prefissato di siti nei quali costruire centrali nucleari.

Ogni comunità:

- è localizzata in un punto noto;
- presenta una domanda energetica;
- deve essere servita da una sola centrale aperta.

Ogni sito candidato:

- è localizzato in un punto noto;
- può ospitare al massimo una centrale;
- dispone di una capacità produttiva massima.

Le centrali devono complessivamente soddisfare la domanda delle comunità, ma devono essere collocate il più lontano possibile dalla popolazione.

L'obiettivo maximin protegge la comunità maggiormente esposta, massimizzando la minima distanza tra una comunità e una centrale costruita.

---

## 3. Assegnazione energetica ed esposizione

Nel problema è necessario distinguere due concetti.

### Assegnazione energetica

L'assegnazione indica quale centrale soddisfa la domanda di una comunità.

Serve per:

- garantire che ogni comunità venga servita;
- verificare il rispetto delle capacità produttive.

### Esposizione

La distanza di sicurezza non dipende dall'assegnazione energetica.

Una comunità può trovarsi vicino a una centrale anche se riceve energia da un altro impianto. Di conseguenza, la funzione obiettivo deve considerare tutte le comunità e tutte le centrali aperte.

---

## 4. Insiemi

- $I$: insieme delle comunità, indicizzate con $i$;
- $J$: insieme dei siti candidati, indicizzati con $j$.

---

## 5. Parametri

- $p$: numero di centrali da costruire;
- $q_i > 0$: domanda energetica della comunità $i$;
- $C_j > 0$: capacità produttiva della centrale costruibile nel sito $j$;
- $d_{ij} \ge 0$: distanza tra la comunità $i$ e il sito candidato $j$.

Per ogni sito candidato definiamo inoltre il suo valore di sicurezza:

```math
r_j=\min_{i\in I}d_{ij}.
```

Il parametro $r_j$ rappresenta la distanza tra il sito $j$ e la comunità ad esso più vicina.

Un upper bound naturale per la funzione obiettivo è:

```math
U=\max_{j\in J}r_j.
```

---

## 6. Variabili decisionali

### Apertura delle centrali

```math
y_j=
\begin{cases}
1 & \text{se viene costruita una centrale nel sito } j,\\
0 & \text{altrimenti.}
\end{cases}
```

### Assegnamento delle comunità

```math
x_{ij}=
\begin{cases}
1 & \text{se la comunità } i \text{ è servita dalla centrale } j,\\
0 & \text{altrimenti.}
\end{cases}
```

### Distanza minima garantita

```math
z\ge0
```

rappresenta la minima distanza tra una comunità e una centrale aperta.

---

## 7. Funzione obiettivo

L'obiettivo consiste nel massimizzare la distanza minima garantita:

```math
\max z.
```

Per un insieme di siti aperti $S\subseteq J$, il valore della soluzione è:

```math
z(S)
=
\min_{\substack{i\in I\\j\in S}}d_{ij}
=
\min_{j\in S}r_j.
```

---

## 8. Formulazione compatta PLI

```math
\max \quad z
```

soggetto a:

```math
\sum_{j\in J}y_j=p
```

```math
\sum_{j\in J}x_{ij}=1
\qquad \forall i\in I
```

```math
x_{ij}\le y_j
\qquad \forall i\in I,\ \forall j\in J
```

```math
\sum_{i\in I}q_i x_{ij}\le C_j y_j
\qquad \forall j\in J
```

```math
z\le r_j+U(1-y_j)
\qquad \forall j\in J
```

```math
0\le z\le U
```

```math
x_{ij}\in\{0,1\}
\qquad \forall i\in I,\ \forall j\in J
```

```math
y_j\in\{0,1\}
\qquad \forall j\in J.
```

---

## 9. Interpretazione dei vincoli

### Numero di centrali

```math
\sum_{j\in J}y_j=p
```

impone di costruire esattamente $p$ centrali.

### Assegnamento a singola sorgente

```math
\sum_{j\in J}x_{ij}=1
```

impone che ogni comunità venga servita da una sola centrale.

### Collegamento apertura-assegnamento

```math
x_{ij}\le y_j
```

impedisce di assegnare una comunità a un sito nel quale non è stata costruita una centrale.

### Capacità

```math
\sum_{i\in I}q_i x_{ij}\le C_j y_j
```

garantisce che la domanda totale assegnata alla centrale $j$ non superi la sua capacità.

Quando $y_j=0$, il termine destro è nullo e nessuna domanda può essere assegnata al sito.

### Definizione della distanza minima

```math
z\le r_j+U(1-y_j)
```

se $y_j=1$ diventa:

```math
z\le r_j.
```

Quindi la distanza minima garantita non può superare il valore di sicurezza di nessun sito aperto.

Se $y_j=0$, il vincolo è disattivato grazie al termine $U(1-y_j)$.

---

## 10. Formulazione equivalente sulle singole distanze

Senza pre-calcolare $r_j$, la distanza minima può essere descritta mediante:

```math
z\le d_{ij}+U(1-y_j)
\qquad \forall i\in I,\ \forall j\in J.
```

Questa formulazione è equivalente, ma contiene $|I||J|$ vincoli di distanza.

La formulazione basata sui valori $r_j$ utilizza soltanto $|J|$ vincoli ed è quindi più compatta.

---

## 11. Osservazioni sulla fattibilità

Una condizione necessaria per la fattibilità è:

```math
\sum_{j\in J_p^{\max}}C_j
\ge
\sum_{i\in I}q_i,
```

dove $J_p^{\max}$ contiene i $p$ siti con capacità maggiore.

Questa condizione non è sempre sufficiente nel caso di assegnamento a singola sorgente. Anche quando la capacità totale è sufficiente, le domande individuali potrebbero non essere distribuibili tra le $p$ centrali senza superarne la capacità.

La fattibilità effettiva deve quindi essere verificata dal modello o da una procedura di assegnamento.

---

## 12. Assunzioni della prima versione

La prima versione del progetto assume che:

- le localizzazioni siano discrete;
- il numero di centrali sia fissato;
- ogni comunità sia assegnata a una sola centrale;
- tutta la domanda debba essere soddisfatta;
- domande, capacità e distanze siano deterministiche;
- le distanze siano euclidee;
- non siano presenti costi di costruzione;
- non siano presenti costi di trasmissione;
- non sia imposto inizialmente un vincolo di distanza tra centrali;
- il problema sia statico e riferito a un solo periodo.

---

## 13. Risultato atteso sulla toy instance

Per l'istanza `toy_instance_01.json`, il risultato verificato manualmente è:

```math
S^*=\{s1,s4\}
```

e:

```math
z^*=18.0278.
```

La dimostrazione completa è disponibile nel documento:

[`toy_instance_solution.md`](toy_instance_solution.md).
# Problema di localizzazione

## Nome adottato

Il problema studiato è denominato:

> **Capacitated Multiple Maximin Obnoxious Facility Location Problem for Nuclear Power Plant Siting**

Si tratta di una variante discreta e capacitata di *facility location* nella quale devono essere aperte più strutture considerate indesiderabili, massimizzando la loro distanza minima dalle comunità.

---

## Scenario applicativo

Un’autorità deve scegliere un numero prefissato di siti nei quali costruire centrali nucleari.

Ogni comunità:

- è localizzata in un punto noto;
- presenta una domanda energetica;
- deve essere servita da una sola centrale aperta.

Ogni sito candidato:

- è localizzato in un punto noto;
- può ospitare al massimo una centrale;
- dispone di una capacità produttiva massima.

Le centrali devono soddisfare tutta la domanda energetica, rispettando le capacità disponibili, e devono essere collocate il più lontano possibile dalla popolazione.

---

## Assegnamento energetico ed esposizione

I due concetti devono essere distinti.

L’**assegnamento energetico** indica quale centrale soddisfa la domanda di una comunità. Serve a verificare:

- copertura completa della domanda;
- compatibilità tra assegnamenti e siti aperti;
- rispetto delle capacità produttive.

L’**esposizione** dipende invece dalla posizione di **tutte le centrali aperte**.

Una comunità può trovarsi vicina a una centrale anche quando riceve energia da un altro impianto. Per questo motivo la funzione obiettivo considera ogni comunità rispetto a ogni sito aperto.

> **Idea chiave:** l’assegnamento determina la fattibilità energetica, mentre l’insieme dei siti aperti determina la sicurezza.

---

## Insiemi

| Simbolo | Descrizione |
|---|---|
| $I$ | insieme delle comunità, indicizzate con $i$ |
| $J$ | insieme dei siti candidati, indicizzati con $j$ |

---

## Parametri

| Simbolo | Descrizione |
|---|---|
| $p$ | numero di centrali da costruire |
| $q_i>0$ | domanda energetica della comunità $i$ |
| $C_j>0$ | capacità produttiva del sito $j$ |
| $d_{ij}\ge 0$ | distanza tra la comunità $i$ e il sito $j$ |

### Sicurezza intrinseca di un sito

Per ogni sito candidato si definisce:

$$
r_j=\min_{i\in I} d_{ij}.
$$

Il valore $r_j$ rappresenta la distanza del sito $j$ dalla comunità più vicina.

Un upper bound valido per la funzione obiettivo è:

$$
U=\max_{j\in J} r_j.
$$

---

## Variabili decisionali

### Apertura dei siti

$$
y_j=
\begin{cases}
1, & \text{se il sito } j \text{ viene aperto},\\
0, & \text{altrimenti.}
\end{cases}
$$

### Assegnamento delle comunità

$$
x_{ij}=
\begin{cases}
1, & \text{se la comunità } i \text{ è servita dal sito } j,\\
0, & \text{altrimenti.}
\end{cases}
$$

### Distanza minima garantita

$$
z\ge 0.
$$

La variabile $z$ rappresenta la distanza minima garantita tra le comunità e le centrali aperte.

---

## Funzione obiettivo

Sia $S\subseteq J$ l’insieme dei siti aperti.

La sicurezza della soluzione è:

$$
z(S)
=
\min_{\substack{i\in I\\j\in S}} d_{ij}
=
\min_{j\in S} r_j.
$$

L’obiettivo è quindi:

$$
\max z.
$$

Il modello massimizza la sicurezza del caso peggiore, cioè la distanza minima tra una comunità e una qualunque centrale aperta.

---

## Formulazione compatta

La formulazione è una **Programmazione Lineare Intera Mista**, perché $x_{ij}$ e $y_j$ sono variabili binarie, mentre $z$ è continua.

### Funzione obiettivo

$$
\max \quad z
$$

### Vincoli

#### Numero di centrali

$$
\sum_{j\in J} y_j=p.
$$

#### Assegnamento completo

$$
\sum_{j\in J} x_{ij}=1
\qquad
\forall i\in I.
$$

#### Collegamento tra assegnamento e apertura

$$
x_{ij}\le y_j
\qquad
\forall i\in I,\ \forall j\in J.
$$

#### Capacità produttiva

$$
\sum_{i\in I} q_i x_{ij}\le C_j y_j
\qquad
\forall j\in J.
$$

#### Sicurezza dei siti aperti

$$
z\le r_j+U(1-y_j)
\qquad
\forall j\in J.
$$

#### Limiti sulla funzione obiettivo

$$
0\le z\le U.
$$

#### Dominio delle variabili

$$
x_{ij}\in\{0,1\}
\qquad
\forall i\in I,\ \forall j\in J,
$$

$$
y_j\in\{0,1\}
\qquad
\forall j\in J.
$$

---

## Interpretazione dei vincoli

| Vincolo | Significato |
|---|---|
| $\sum_{j\in J}y_j=p$ | vengono costruite esattamente $p$ centrali |
| $\sum_{j\in J}x_{ij}=1$ | ogni comunità è assegnata a una sola centrale |
| $x_{ij}\le y_j$ | una comunità può essere assegnata soltanto a un sito aperto |
| $\sum_{i\in I}q_ix_{ij}\le C_jy_j$ | la domanda assegnata non supera la capacità del sito |
| $z\le r_j+U(1-y_j)$ | ogni sito aperto impone $z\le r_j$ |

Quando $y_j=1$, il vincolo di sicurezza diventa:

$$
z\le r_j.
$$

Quando $y_j=0$, il termine $U(1-y_j)$ rende il vincolo non restrittivo.

Di conseguenza, all’ottimo:

$$
z=\min_{j:y_j=1}r_j.
$$

---

## Formulazione equivalente sulle distanze

Senza pre-calcolare $r_j$, è possibile utilizzare direttamente le distanze:

$$
z\le d_{ij}+U(1-y_j)
\qquad
\forall i\in I,\ \forall j\in J.
$$

Le due formulazioni sono equivalenti dal punto di vista della funzione obiettivo.

La formulazione diretta introduce:

$$
|I||J|
$$

vincoli di sicurezza.

La formulazione basata su $r_j$ utilizza invece soltanto:

$$
|J|
$$

vincoli di sicurezza ed è quindi più compatta.

---

## Fattibilità

Una condizione necessaria per la fattibilità è:

$$
\sum_{j\in J_p^{\max}} C_j
\ge
\sum_{i\in I} q_i,
$$

dove $J_p^{\max}$ contiene i $p$ siti con capacità maggiore.

La condizione non è sufficiente.

Poiché l’assegnamento è a singola sorgente, ogni comunità deve essere servita interamente da una sola centrale. Le singole domande potrebbero quindi non essere distribuibili tra i siti scelti, anche quando la capacità complessiva è sufficiente.

La fattibilità effettiva deve essere verificata:

- dal modello esatto;
- dalla procedura di assegnamento;
- oppure dal repair utilizzato dalle euristiche.

---

## Assunzioni

Il progetto considera:

- localizzazioni discrete;
- numero di centrali fissato;
- assegnamento a singola sorgente;
- domanda interamente soddisfatta;
- dati deterministici;
- distanze euclidee;
- un singolo periodo temporale;
- assenza di costi di costruzione;
- assenza di costi di trasmissione;
- assenza di vincoli espliciti di separazione tra centrali.

Il *nuclear siting* costituisce lo scenario applicativo del modello.

Le istanze sperimentali sono sintetiche e non rappresentano un piano reale di localizzazione di centrali nucleari.

---

## Toy instance

Per l’istanza:

```text
instances/test/toy_instance_01.json
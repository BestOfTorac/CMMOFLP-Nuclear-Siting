# Problema di localizzazione

## Nome adottato

Il problema studiato è indicato come:

**Capacitated Multiple Maximin Obnoxious Facility Location Problem for Nuclear Power Plant Siting**.

Si tratta di una variante discreta e capacitata di facility location nella quale devono essere aperte più strutture considerate indesiderabili, massimizzandone la distanza minima dalle comunità.

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

Le centrali devono soddisfare tutta la domanda, rispettando le capacità, e devono essere collocate il più lontano possibile dalla popolazione.

## Assegnamento energetico ed esposizione

I due concetti sono distinti.

L’**assegnamento energetico** indica quale centrale soddisfa la domanda di una comunità. Serve a verificare copertura e capacità.

L’**esposizione** dipende invece dalla posizione di tutte le centrali aperte. Una comunità può trovarsi vicina a una centrale anche quando riceve energia da un altro impianto. Per questo la funzione obiettivo considera ogni comunità rispetto a ogni sito aperto.

## Insiemi

- \(I\): comunità, indicizzate con \(i\);
- \(J\): siti candidati, indicizzati con \(j\).

## Parametri

- \(p\): numero di centrali da costruire;
- \(q_i>0\): domanda della comunità \(i\);
- \(C_j>0\): capacità del sito \(j\);
- \(d_{ij}\ge 0\): distanza tra comunità \(i\) e sito \(j\).

Per ciascun sito si definisce la sicurezza:

\[
r_j=\min_{i\in I} d_{ij}.
\]

Il valore \(r_j\) è la distanza del sito \(j\) dalla comunità più vicina.

Un upper bound semplice è:

\[
U=\max_{j\in J} r_j.
\]

## Variabili

### Apertura

\[
y_j=
\begin{cases}
1 & \text{se il sito }j\text{ viene aperto},\\
0 & \text{altrimenti.}
\end{cases}
\]

### Assegnamento

\[
x_{ij}=
\begin{cases}
1 & \text{se la comunità }i\text{ è servita dal sito }j,\\
0 & \text{altrimenti.}
\end{cases}
\]

### Distanza minima

\[
z\ge 0
\]

rappresenta la distanza minima garantita tra le comunità e le centrali aperte.

## Funzione obiettivo

Dato l’insieme dei siti aperti \(S\subseteq J\):

\[
z(S)
=
\min_{\substack{i\in I\\j\in S}} d_{ij}
=
\min_{j\in S} r_j.
\]

L’obiettivo è:

\[
\max z.
\]

## Formulazione compatta

\[
\max \quad z
\]

soggetto a:

\[
\sum_{j\in J} y_j=p
\]

\[
\sum_{j\in J} x_{ij}=1
\qquad \forall i\in I
\]

\[
x_{ij}\le y_j
\qquad \forall i\in I,\ \forall j\in J
\]

\[
\sum_{i\in I} q_i x_{ij}\le C_j y_j
\qquad \forall j\in J
\]

\[
z\le r_j+U(1-y_j)
\qquad \forall j\in J
\]

\[
0\le z\le U
\]

\[
x_{ij}\in\{0,1\}
\qquad \forall i\in I,\ \forall j\in J
\]

\[
y_j\in\{0,1\}
\qquad \forall j\in J.
\]

## Interpretazione dei vincoli

- \(\sum_j y_j=p\): vengono costruite esattamente \(p\) centrali;
- \(\sum_j x_{ij}=1\): ogni comunità è assegnata a una sola centrale;
- \(x_{ij}\le y_j\): un assegnamento è possibile soltanto verso un sito aperto;
- \(\sum_i q_i x_{ij}\le C_jy_j\): la domanda assegnata non supera la capacità;
- \(z\le r_j+U(1-y_j)\): ogni sito aperto impone \(z\le r_j\).

## Formulazione equivalente sulle distanze

Senza pre-calcolare \(r_j\), si può usare:

\[
z\le d_{ij}+U(1-y_j)
\qquad \forall i\in I,\ \forall j\in J.
\]

Questa formulazione è equivalente, ma introduce \(|I||J|\) vincoli di sicurezza. La formulazione tramite \(r_j\) utilizza soltanto \(|J|\) vincoli ed è quindi più compatta.

## Fattibilità

Una condizione necessaria è:

\[
\sum_{j\in J_p^{\max}} C_j
\ge
\sum_{i\in I} q_i,
\]

dove \(J_p^{\max}\) contiene i \(p\) siti di capacità maggiore.

Non è una condizione sufficiente: con assegnamento a singola sorgente, le singole domande potrebbero non essere distribuibili senza superare una capacità. La fattibilità effettiva deve essere verificata dal modello o da una procedura di assegnamento.

## Assunzioni

Il progetto considera:

- localizzazioni discrete;
- numero di centrali fissato;
- assegnamento a singola sorgente;
- domanda interamente soddisfatta;
- dati deterministici;
- distanze euclidee;
- un singolo periodo;
- assenza di costi di costruzione e trasmissione;
- assenza di vincoli espliciti tra centrali.

Il nuclear siting costituisce lo scenario applicativo del modello. Le istanze sperimentali sono sintetiche e non rappresentano un piano reale di localizzazione.

## Toy instance

Per `instances/test/toy_instance_01.json`:

\[
S^*=\{s1,s4\}
\]

e:

\[
z^*=18.0278.
\]

La verifica completa è disponibile in [toy_instance_solution.md](toy_instance_solution.md).

# Soluzione manuale della toy instance

## 1. Scopo dell'istanza

La toy instance viene utilizzata per verificare manualmente:

- la definizione della funzione obiettivo;
- il numero di centrali da costruire;
- la fattibilità degli assegnamenti;
- il rispetto delle capacità;
- la correttezza dei modelli esatti e delle euristiche che verranno sviluppati.

L'istanza contiene:

- 5 comunità;
- 4 siti candidati;
- 2 centrali da costruire;
- domanda energetica totale pari a 100.

---

## 2. Comunità

| Comunità | Coordinata x | Coordinata y | Domanda |
|---|---:|---:|---:|
| c1 | 10 | 15 | 20 |
| c2 | 20 | 40 | 25 |
| c3 | 35 | 25 | 15 |
| c4 | 50 | 60 | 20 |
| c5 | 65 | 30 | 20 |

La domanda totale è:

\[
Q = 20+25+15+20+20=100.
\]

---

## 3. Siti candidati

| Sito | Coordinata x | Coordinata y | Capacità |
|---|---:|---:|---:|
| s1 | 5 | 70 | 55 |
| s2 | 30 | 10 | 60 |
| s3 | 55 | 75 | 50 |
| s4 | 80 | 20 | 60 |

Devono essere selezionati esattamente:

\[
p=2
\]

siti candidati.

---

## 4. Calcolo delle distanze

La distanza tra la comunità \(i\) e il sito candidato \(j\) è calcolata mediante la distanza euclidea:

\[
d_{ij}
=
\sqrt{(x_i-x_j)^2+(y_i-y_j)^2}.
\]

La matrice delle distanze è:

| Comunità | s1 | s2 | s3 | s4 |
|---|---:|---:|---:|---:|
| c1 | 55.2268 | 20.6155 | 75.0000 | 70.1783 |
| c2 | 33.5410 | 31.6228 | 49.4975 | 63.2456 |
| c3 | 54.0833 | 15.8114 | 53.8516 | 45.2769 |
| c4 | 46.0977 | 53.8516 | 15.8114 | 50.0000 |
| c5 | 72.1110 | 40.3113 | 46.0977 | 18.0278 |

---

## 5. Valore di sicurezza dei siti

Per ogni sito candidato \(j\) definiamo:

\[
r_j=\min_{i\in I}d_{ij}.
\]

Il valore \(r_j\) rappresenta la distanza tra il sito \(j\) e la comunità ad esso più vicina.

| Sito | Comunità più vicina | Valore \(r_j\) |
|---|---|---:|
| s1 | c2 | 33.5410 |
| s2 | c3 | 15.8114 |
| s3 | c4 | 15.8114 |
| s4 | c5 | 18.0278 |

Il sito individualmente più sicuro è quindi `s1`.

Tuttavia, devono essere costruite due centrali. Il valore di una soluzione costituita dall'insieme di siti aperti \(S\) è:

\[
z(S)
=
\min_{j\in S}r_j
=
\min_{\substack{i\in I\\j\in S}}d_{ij}.
\]

---

## 6. Valutazione delle coppie

| Siti aperti | Valore obiettivo | Capacità totale |
|---|---:|---:|
| s1, s2 | 15.8114 | 115 |
| s1, s3 | 15.8114 | 105 |
| s1, s4 | 18.0278 | 115 |
| s2, s3 | 15.8114 | 110 |
| s2, s4 | 15.8114 | 120 |
| s3, s4 | 15.8114 | 110 |

La coppia che garantisce la distanza minima maggiore è:

\[
S^*=\{s1,s4\}.
\]

Il suo valore è:

\[
z(S^*)=\min\{r_{s1},r_{s4}\}
\]

e quindi:

\[
z(S^*)=\min\{33.5410,18.0278\}=18.0278.
\]

---

## 7. Dimostrazione dell'ottimalità

Poiché devono essere selezionati due siti, il valore della soluzione non può essere maggiore del secondo valore più alto tra tutti i valori \(r_j\).

I valori ordinati in senso decrescente sono:

\[
33.5410,\quad18.0278,\quad15.8114,\quad15.8114.
\]

Pertanto:

\[
z^*\le18.0278.
\]

La coppia \(\{s1,s4\}\) raggiunge esattamente tale valore ed è compatibile con i vincoli di capacità.

Di conseguenza:

\[
\boxed{z^*=18.0278}
\]

e:

\[
\boxed{S^*=\{s1,s4\}}.
\]

---

## 8. Assegnamento energetico ammissibile

Una possibile assegnazione è:

| Comunità | Centrale assegnata | Domanda |
|---|---|---:|
| c1 | s1 | 20 |
| c2 | s1 | 25 |
| c3 | s4 | 15 |
| c4 | s4 | 20 |
| c5 | s4 | 20 |

Il carico della centrale `s1` è:

\[
L_{s1}=20+25=45.
\]

La sua capacità è 55, quindi:

\[
45\le55.
\]

Il carico della centrale `s4` è:

\[
L_{s4}=15+20+20=55.
\]

La sua capacità è 60, quindi:

\[
55\le60.
\]

Tutte le comunità sono assegnate a una sola centrale e tutti i vincoli di capacità sono rispettati.

---

## 9. Distanza che determina l'obiettivo

Il valore della soluzione è determinato dalla distanza tra la comunità `c5` e il sito `s4`:

\[
d_{c5,s4}
=
\sqrt{(65-80)^2+(30-20)^2}.
\]

Quindi:

\[
d_{c5,s4}
=
\sqrt{225+100}
=
\sqrt{325}
\approx18.0278.
\]

---

## 10. Osservazione sull'assegnamento

L'assegnamento energetico e la distanza di sicurezza svolgono due ruoli differenti.

L'assegnamento indica quale centrale soddisfa la domanda di una comunità e serve a verificare i vincoli di capacità.

La funzione obiettivo considera invece tutte le comunità e tutte le centrali aperte, indipendentemente dagli assegnamenti.

Una comunità può infatti trovarsi vicino a una centrale anche quando riceve energia da un altro impianto.
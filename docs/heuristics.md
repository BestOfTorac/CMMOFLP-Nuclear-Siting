# Euristiche

Il progetto contiene una baseline costruttiva, una procedura di repair, una local search 1-swap e una euristica avanzata GRASP-VND.

## Sicurezza dei siti

Per ogni sito candidato:

\[
r_j=\min_{i\in I} d_{ij}.
\]

Per un insieme aperto \(S\):

\[
z(S)=\min_{j\in S}r_j.
\]

Questa quantità dipende soltanto dai siti aperti. L’assegnamento serve invece a verificare le capacità.

## Greedy capacitata

La greedy procede in due fasi.

### Selezione dei siti

I siti vengono ordinati privilegiando:

1. sicurezza maggiore;
2. capacità maggiore;
3. identificativo come spareggio.

A ogni scelta viene applicato un look-ahead: il candidato viene accettato soltanto se, usando i posti rimanenti e le capacità migliori ancora disponibili, è ancora possibile raggiungere la domanda totale.

### Assegnamento best-fit decreasing

Le comunità vengono ordinate per domanda decrescente.

Ogni comunità viene assegnata alla centrale che:

- possiede capacità residua sufficiente;
- lascia la minore capacità residua non negativa;
- usa sicurezza e identificativo come spareggi.

La greedy è rapida, ma può fallire anche quando esiste un assegnamento ammissibile.

## Repair capacitato

Il repair cerca un assegnamento per un insieme di siti già fissato.

La procedura:

1. prova una costruzione best-fit;
2. ordina le comunità per difficoltà;
3. usa backtracking limitato;
4. applica un limite al numero di nodi;
5. rispetta una deadline globale opzionale.

Il repair non modifica l’insieme di siti. Serve a stabilire se quell’insieme può sostenere un assegnamento a singola sorgente.

## Local search 1-swap

La local search parte dalla soluzione greedy o da un suo assegnamento riparato.

Un vicino si ottiene:

- rimuovendo un sito aperto;
- inserendo un sito chiuso;
- cercando nuovamente un assegnamento ammissibile.

Le soluzioni vengono confrontate lessicograficamente tramite:

\[
\left(
\min_{j\in S}r_j,
\sum_{j\in S}r_j
\right).
\]

Il primo componente è l’obiettivo reale. Il secondo è soltanto uno spareggio.

Nel benchmark finale il 1-swap isolato non ha migliorato nessuna soluzione greedy. Rimane tuttavia un componente della VND, dove viene applicato a soluzioni iniziali differenti.

## GRASP-VND

GRASP-VND è il metodo euristico principale:

```text
multi-start
→ costruzione randomizzata con RCL
→ best-fit
→ repair
→ VND con 1-swap e 2-swap mirato
→ migliore soluzione globale
```

### Costruzione randomizzata

A ogni passo:

1. vengono eliminati i candidati incompatibili con la capacità totale raggiungibile;
2. sicurezza e capacità vengono normalizzate;
3. si calcola un punteggio combinato;
4. si costruisce una Restricted Candidate List;
5. si estrae casualmente un sito.

Il parametro `alpha` controlla l’ampiezza della RCL.

### Cache degli assegnamenti

L’insieme dei siti aperti viene usato come chiave. Per uno stesso insieme non viene ripetuta inutilmente la procedura di assegnamento.

Gli insiemi interrotti dalla deadline non vengono memorizzati come non ammissibili.

### 1-swap mirato

I siti uscenti sono scelti tra quelli meno sicuri. I siti entranti sono selezionati da una lista dei candidati chiusi più promettenti.

### 2-swap mirato

Si definisce l’insieme dei siti critici:

\[
C(S)=\{j\in S:r_j=z(S)\}.
\]

Quando più siti determinano il minimo, un singolo scambio può essere insufficiente. Il 2-swap rimuove i siti critici o li combina con i siti di sicurezza immediatamente successiva, evitando l’enumerazione completa di tutte le coppie.

### Upper bound

Ordinando le sicurezze:

\[
r_{(1)}\ge r_{(2)}\ge\dots\ge r_{(|J|)},
\]

aprendo esattamente \(p\) siti vale:

\[
z^*\le r_{(p)}.
\]

Il bound ignora le capacità e può non essere raggiungibile. Quando una soluzione ammissibile raggiunge \(r_{(p)}\), l’ottimalità è certificata.

### Criteri di arresto

L’esecuzione può terminare per:

- `upper_bound`;
- `stagnation`;
- `time_limit`;
- `time_limit_no_incumbent`;
- `max_starts`.

La stagnazione viene misurata sugli start consecutivi senza miglioramento dell’obiettivo maximin.

### Parametri del benchmark finale

| Parametro | Valore |
|---|---:|
| `alpha` | 0.30 |
| start massimi | 100 |
| stagnazione | 20 start |
| time limit | 20 secondi |
| candidate list | 20 |
| limite nodi repair | 100000 |
| peso sicurezza | 0.80 |
| siti uscenti secondari | 3 |

## Logging

Per ogni run vengono registrati:

- seed;
- start tentati, completati, ammissibili e falliti;
- repair tentati e riusciti;
- mosse 1-swap e 2-swap;
- cache hit e miss;
- tempo al best;
- runtime totale;
- motivo di arresto;
- certificazione tramite upper bound.

## Configurazione operativa

Le cinque esecuzioni sono state usate per valutare stabilità e variabilità. L’ablation mostra che una singola run con seed 42 ottiene lo stesso numero di ottimi del best-of-5, con un costo molto inferiore.

Per l’uso pratico è quindi ragionevole una singola run. Il best-of-5 resta utile come misura sperimentale.

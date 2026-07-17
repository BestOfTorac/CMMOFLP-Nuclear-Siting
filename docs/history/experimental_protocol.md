# Protocollo sperimentale preliminare

Metodi:

- `compact_mip`
- `threshold_exact`
- `greedy`
- `local_search`

Indicatori per i metodi esatti:

- soluzione ammissibile;
- bound;
- gap;
- tempo;
- stato;
- nodi.

Indicatori per le euristiche:

- valore;
- fattibilità;
- tempo;
- gap rispetto all'ottimo o al best known;
- media e deviazione standard se randomizzate.

Per un problema di massimizzazione:

\[
gap_H = \frac{z^* - z_H}{z^*}\cdot 100.
\]

Ogni risultato deve essere collegato a istanza, configurazione, seed, metodo e versione del codice.

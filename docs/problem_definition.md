# Definizione preliminare del problema

## Nome

**Capacitated Multiple Maximin Obnoxious Facility Location Problem applicato alla localizzazione di centrali nucleari.**

## Scenario

Un'autorità deve scegliere un numero prefissato di siti nei quali costruire centrali nucleari. Ogni comunità presenta una domanda energetica e ogni sito candidato dispone di una capacità produttiva massima.

## Insiemi e parametri

- \(I\): comunità;
- \(J\): siti candidati;
- \(q_i\): domanda energetica;
- \(C_j\): capacità del sito;
- \(d_{ij}\): distanza comunità-sito;
- \(p\): numero di centrali.

## Decisioni

- scegliere esattamente \(p\) siti;
- assegnare ogni comunità a una centrale aperta;
- rispettare le capacità;
- massimizzare la minima distanza tra una comunità e una centrale aperta.

## Assegnazione ed esposizione

L'assegnazione energetica indica quale centrale soddisfa la domanda. La distanza di sicurezza considera invece tutte le centrali aperte.

## Assunzioni iniziali

- localizzazioni discrete;
- numero di centrali fissato;
- assegnamento a singola sorgente;
- domanda completamente soddisfatta;
- dati deterministici;
- distanze euclidee;
- nessun costo di costruzione nella prima versione.

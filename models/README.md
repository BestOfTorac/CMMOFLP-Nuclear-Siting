# Modelli matematici

La cartella contiene i due modelli AMPL esatti utilizzati nel progetto.

## `compact.mod`

Formulazione PLI compatta del CMMOFLP.

Variabili principali:

- `y[j]`: apertura del sito candidato `j`;
- `x[i,j]`: assegnamento della comunità `i` al sito `j`;
- `z`: distanza minima garantita.

Il modello:

- apre esattamente `p` centrali;
- assegna ogni comunità a una centrale aperta;
- rispetta le capacità produttive;
- massimizza la minima sicurezza dei siti aperti.

È il metodo esatto principale e viene eseguito automaticamente tramite:

```bash
python scripts/run_exact_benchmark.py --methods compact
```

## `threshold.mod`

Modello di fattibilità per una soglia di sicurezza fissata.

Data una soglia `threshold`, verifica se esiste un insieme di `p` siti:

- con sicurezza almeno pari alla soglia;
- capace di servire tutte le comunità;
- rispettando i vincoli di capacità.

Ripetendo il controllo sulle soglie candidate si ottiene un metodo esatto alternativo. È stato usato soprattutto sulla toy instance e sulle istanze pilota, perché può richiedere molti solve consecutivi.

## Requisiti

I modelli richiedono:

- AMPL;
- un solver MIP compatibile;
- dati nel formato `.dat` oppure caricati dal runner Python.

Nel progetto è stato utilizzato Gurobi. Licenze e percorsi locali non sono inclusi nel repository.

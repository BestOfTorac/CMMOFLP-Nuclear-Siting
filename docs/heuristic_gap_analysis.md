# Analisi dei gap delle euristiche

## Riferimento esatto

Il modello compatto viene utilizzato come riferimento principale, poiché nel pilot ha restituito gli stessi valori del metodo a soglia con tempi inferiori.

Per ogni istanza si indica con:

- `z*` il valore ottimo del modello compatto;
- `z_H` il valore prodotto dall'euristica.

## Gap per un problema di massimizzazione

Il gap percentuale è calcolato mediante:

```math
gap_H =
\frac{z^* - z_H}{z^*}\cdot 100.
```

Interpretazione:

- gap pari a `0%`: soluzione euristica ottima;
- gap positivo: soluzione subottima;
- euristica non ammissibile: gap non definito;
- gap negativo oltre la tolleranza: possibile incoerenza nei risultati.

## Esecuzione

```bash
python scripts/analyze_heuristic_gaps.py
```

Vengono prodotti:

```text
results/aggregated/heuristic_gaps.csv
results/aggregated/heuristic_gaps_by_class.csv
```

Il primo file contiene il confronto istanza-metodo. Il secondo aggrega qualità, robustezza e tempi per classe.

## Indicatori

Per ogni euristica vengono calcolati:

- numero di esecuzioni;
- soluzioni ammissibili;
- confronti disponibili;
- soluzioni ottime;
- soluzioni subottime;
- fallimenti;
- gap medio, mediano e massimo;
- speedup rispetto al modello esatto.

# Snapshot della campagna finale

Questa cartella contiene i dati minimi necessari per verificare i risultati riportati nel repository senza ripetere l’intera campagna AMPL/Gurobi.

## Provenienza

- benchmark: 90 istanze sintetiche;
- baseline: 180 esecuzioni;
- GRASP-VND: 450 esecuzioni, cinque seed per istanza;
- compact: 90 esecuzioni con time limit di 60 secondi.

## Cartelle

- `raw/`: dati consolidati prodotti dai runner;
- `summary/`: tabelle prodotte da `analyze_final_results.py`;
- `ablation/`: tabelle prodotte da `analyze_ablation.py`.

## Verifica

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
python scripts/generate_final_plots.py
git diff -- results/final results/plots/final
```

Dopo la rigenerazione non devono comparire differenze sostanziali nei CSV. Piccole variazioni non sono attese perché gli script elaborano dati già fissati e non eseguono algoritmi randomizzati.

Gli output di nuove campagne devono essere salvati nelle cartelle locali ignorate da Git, non in questo snapshot. I grafici definitivi derivati dallo snapshot sono pubblicati in `results/plots/final/`.

# Ablation study minimale

L'ablation viene svolta senza creare nuove varianti complesse dell'algoritmo e senza modificare H2.

## Varianti confrontate

1. `Greedy`
2. `Greedy + 1-swap`
3. `GRASP-VND seed 42`
4. `GRASP-VND best-of-5`

Questa struttura permette di misurare:

- il contributo del vicinato 1-swap usato isolatamente;
- il vantaggio di H2 rispetto alla costruzione greedy;
- il vantaggio di cinque seed rispetto a una singola esecuzione;
- il costo computazionale aggiuntivo.

Non vengono rimossi separatamente repair, cache e 2-swap, perché ciò richiederebbe nuove versioni artificiali del codice e aumenterebbe inutilmente la complessità del progetto.

## Esecuzione

```bash
python scripts/analyze_ablation.py
```

Output:

```text
results/processed/ablation/
```

## Tabelle

- `ablation_summary.csv`: fattibilità, ottimalità, gap e runtime;
- `component_effect_summary.csv`: effetto sintetico di 1-swap e multi-seed;
- `local_search_effect.csv`: confronto istanza per istanza fra greedy e 1-swap;
- `multiseed_effect.csv`: confronto fra seed 42 e best-of-5;
- `ablation_instance_detail.csv`: dettaglio completo delle quattro varianti.

## Interpretazione

I gap sono calcolati soltanto per le istanze con ottimo compact certificato.

Il runtime del best-of-5 è la somma sequenziale delle cinque esecuzioni. Questo evita confronti ingannevoli con una singola run.

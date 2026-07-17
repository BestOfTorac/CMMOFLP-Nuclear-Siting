# Comandi AMPL manuali

I file `.run` eseguono i modelli sulla toy instance. Devono essere lanciati dalla radice del repository, affinché i percorsi verso `models/` e `instances/` siano risolti correttamente.

## Modello compatto

```bash
ampl scripts/ampl/run_compact.run
```

## Verifiche a soglia

```bash
ampl scripts/ampl/run_threshold_checks.run
```

## Ricerca automatica della soglia

```bash
ampl scripts/ampl/run_threshold_search.run
```

I file utilizzano Gurobi. Per un solver differente è necessario modificare localmente l’opzione `solver`.

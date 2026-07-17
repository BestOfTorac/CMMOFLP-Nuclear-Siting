# Documentazione

Questa pagina indica l’ordine consigliato per comprendere il progetto senza seguire l’intera cronologia di sviluppo.

## Percorso essenziale

1. [Definizione formale del problema](problem_definition.md)  
   Scenario, insiemi, parametri, variabili, obiettivo e formulazione compatta.

2. [Soluzione della toy instance](toy_instance_solution.md)  
   Esempio completo usato per validare formulazione e implementazione.

3. [Euristica avanzata GRASP-VND](advanced_heuristic.md)  
   Costruzione randomizzata, repair, vicinati, upper bound e criteri di arresto.

4. [Protocollo del benchmark finale](final_benchmark_protocol.md)  
   Classi di istanze, metodi, seed, time limit e indicatori sperimentali.

5. [Analisi finale dei risultati](final_results_analysis.md)  
   Regole per aggregare i risultati e distinguere ottimi certificati da incumbent.

6. [Ablation study](ablation_study.md)  
   Confronto tra greedy, 1-swap, singola run GRASP-VND e best-of-5.

## Specifiche delle istanze

- [Formato JSON e DAT](instance_format.md)
- [Generazione delle istanze](instance_generation.md)

## Metodi esatti e metriche

- [Esperimenti esatti pilota](exact_pilot_experiments.md)
- [Metriche MIP e calibrazione XLarge](exact_mip_metrics_and_xlarge.md)
- [Gestione delle esecuzioni senza incumbent](no_incumbent_handling.md)

## Sviluppo dell’euristica

- [Esperimenti pilota GRASP-VND](grasp_vnd_pilot.md)
- [Analisi dei gap euristici](heuristic_gap_analysis.md)
- [Arresto per stagnazione e deadline](search_stopping_protocol.md)
- [Indipendenza delle istanze tra seed](fresh_instance_per_seed.md)
- [Limite di ricorsione del repair](repair_recursion_limit.md)

## Protocolli precedenti

Questi documenti descrivono passaggi intermedi e restano utili per ricostruire il percorso sperimentale:

- [Piano di sviluppo](development_plan.md)
- [Protocollo sperimentale iniziale](experimental_protocol.md)
- [Esperimenti pilota](pilot_experiments.md)
- [Benchmark intermedio](intermediate_benchmark_protocol.md)
- [Stress test XXLarge](xxlarge_calibration_protocol.md)

In una fase successiva i documenti storici verranno consolidati o spostati in una sezione dedicata, senza perdere informazioni utili.

## Relazione e slide

- [Relazione dettagliata](report/README.md)
- [Presentazione](slides/README.md)

La relazione servirà principalmente agli autori per comprendere e ripassare il progetto. Il materiale consegnato al docente sarà costituito dalle slide e dal link al repository GitHub.

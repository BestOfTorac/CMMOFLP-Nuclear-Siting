# Script

Gli script rappresentano l’interfaccia da riga di comando del progetto. Devono essere eseguiti dalla cartella principale del repository con l’ambiente virtuale attivo.

## Struttura

```text
scripts/
├── analyze_ablation.py
├── analyze_final_results.py
├── check_instance.py
├── generate_final_plots.py
├── generate_instances.py
├── inspect_instance_manifest.py
├── merge_manifests.py
├── run_baseline_benchmark.py
├── run_exact_benchmark.py
├── run_grasp_vnd.py
├── run_grasp_vnd_benchmark.py
├── run_greedy.py
├── run_local_search.py
├── ampl/
├── examples/
└── history/
```

La cartella principale contiene soltanto i comandi utili per usare, verificare e riprodurre la versione finale del progetto.

## Comandi principali

### Validare una istanza

```bash
python scripts/check_instance.py instances/test/toy_instance_01.json
```

### Generare il benchmark finale

```bash
python scripts/generate_instances.py \
  --config configs/benchmark/final_benchmark.yaml
```

Il comando genera i JSON e il `manifest.csv` in:

```text
instances/generated/final_benchmark/
```

### Eseguire le baseline

```bash
python scripts/run_baseline_benchmark.py
```

Il runner esegue, per impostazione predefinita, greedy e local search sul manifest finale e salva l’output locale in:

```text
results/raw/final_heuristics.csv
```

### Eseguire GRASP-VND

```bash
python scripts/run_grasp_vnd_benchmark.py
```

I valori predefiniti corrispondono al protocollo finale:

- seed `42`, `123`, `2026`, `31415`, `98765`;
- 100 start;
- 20 start di stagnazione;
- time limit di 20 secondi.

### Eseguire il modello compatto

```bash
python scripts/run_exact_benchmark.py
```

Il runner usa per impostazione predefinita il metodo `compact` con time limit di 60 secondi. Richiede AMPL e un solver MIP configurato localmente.

### Rigenerare le analisi pubblicate

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
```

Gli script leggono i risultati ufficiali da `results/final/raw/` e rigenerano:

```text
results/final/summary/
results/final/ablation/
```

### Rigenerare i grafici definitivi

```bash
python scripts/generate_final_plots.py
```

Il comando legge le tabelle pubblicate e riscrive i quattro PNG versionati in `results/plots/final/`.

## Esecuzioni singole

Per provare i metodi su una singola istanza:

```bash
python scripts/run_greedy.py
python scripts/run_local_search.py
python scripts/run_grasp_vnd.py \
  --instance instances/test/toy_instance_01.json \
  --seed 42 \
  --starts 25 \
  --stagnation-starts 20 \
  --time-limit 5
```

## Utilità

| Script | Funzione |
|---|---|
| `inspect_instance_manifest.py` | stima variabili, vincoli e solve a soglia |
| `merge_manifests.py` | unisce manifest generati separatamente |

## Esempi

La cartella [`examples/`](examples/README.md) contiene:

- generazione di una singola istanza uniforme;
- verifica dei due metodi esatti sulla toy instance.

## Comandi AMPL manuali

La cartella [`ampl/`](ampl/README.md) contiene tre file `.run` per eseguire manualmente compact e threshold sulla toy instance.

## Analisi storiche

La cartella [`history/`](history/README.md) conserva gli script usati nelle campagne pilota e di calibrazione. Non sono necessari per riprodurre i risultati definitivi.

## Convenzioni

- eseguire i comandi dalla radice del repository;
- non modificare manualmente i CSV grezzi;
- usare i runner finali per nuove campagne;
- usare gli script storici soltanto insieme alla relativa documentazione in `docs/history/`.

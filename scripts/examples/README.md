# Esempi

Questa cartella contiene esempi autonomi che aiutano a verificare l’installazione e comprendere il progetto.

## Generare una singola istanza

```bash
python scripts/examples/generate_sample.py
```

Parametri disponibili:

```bash
python scripts/examples/generate_sample.py --help
```

L’output predefinito è:

```text
instances/generated/sample_uniform.json
```

## Verificare i metodi esatti sulla toy instance

```bash
python scripts/examples/run_exact_toy.py
```

Il comando esegue compact e threshold tramite AMPL e verifica che entrambi restituiscano:

```text
Siti aperti: s1, s4
Obiettivo: 18.0278
```

Sono necessari AMPL e Gurobi configurati localmente.

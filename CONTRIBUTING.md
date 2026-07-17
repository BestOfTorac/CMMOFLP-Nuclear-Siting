# Linee guida per contribuire

Il branch `main` deve contenere soltanto modifiche verificate e integrate tramite pull request.

## Branch

Usare nomi brevi e descrittivi:

```text
feature/<argomento>
fix/<problema>
docs/<argomento>
```

Esempi:

```text
feature/repository-cleanup
docs/final-report
fix/result-analysis-warning
```

## Commit

I messaggi di commit sono scritti in inglese, all’imperativo e senza punto finale.

Esempi:

```text
Clarify repository structure and usage
Consolidate project documentation
Fix result aggregation warnings
```

Ogni commit deve rappresentare una modifica coerente e verificabile.

## Convenzioni linguistiche

- README, documentazione e spiegazioni in italiano;
- cartelle, file, classi, funzioni e variabili in inglese;
- commenti nel codice in italiano quando chiariscono scelte non immediate;
- messaggi di commit e nomi dei branch in inglese.

## Verifica

Prima di effettuare il push:

```bash
python -m pytest -W error::FutureWarning
git status
```

Quando sono coinvolti gli esperimenti finali, verificare anche:

```bash
python scripts/analyze_final_results.py
python scripts/analyze_ablation.py
```

## Regole sui dati

- configurazioni e seed devono essere salvati;
- i risultati grezzi non devono essere modificati manualmente;
- istanze generate e output intermedi non devono essere aggiunti senza una motivazione precisa;
- nessuna credenziale, chiave, licenza o percorso personale deve essere pubblicato;
- i file derivati devono poter essere rigenerati tramite script documentati.

## Pull request

La descrizione deve indicare:

- cosa cambia;
- perché è necessario;
- quali comandi sono stati eseguiti;
- esito dei test;
- eventuali effetti su documentazione, risultati o compatibilità.

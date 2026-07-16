# Indipendenza delle esecuzioni multi-seed

Ogni coppia `(istanza, seed algoritmico)` deve essere una prova indipendente.

La pipeline precedente caricava una sola istanza e la riutilizzava per tutti i seed. Nello stress test XXLarge questo produceva due righe con runtime quasi nullo, mentre la stessa esecuzione lanciata singolarmente richiedeva correttamente circa 20 secondi.

La pipeline ora ricarica il file JSON per ogni seed:

```text
manifest row
→ carica nuova ProblemInstance
→ esegui un seed
→ scarta l'oggetto
→ carica una nuova ProblemInstance
```

In questo modo eventuali cache o mutazioni interne non possono influenzare le esecuzioni successive.

La modifica riguarda il protocollo sperimentale, non l'euristica.

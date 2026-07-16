# Limite di ricorsione del repair

Il repair usa un backtracking ricorsivo la cui profondità massima coincide con il numero di comunità.

Nelle istanze XXLarge con 1200 comunità, il limite standard di ricorsione di Python poteva produrre:

```text
maximum recursion depth exceeded
```

La procedura ora aumenta temporaneamente il limite a:

```text
numero_comunità + 200
```

e ripristina il valore precedente al termine.

Questa è una correzione tecnica dell'implementazione, non una modifica dell'euristica o del metodo di ricerca.

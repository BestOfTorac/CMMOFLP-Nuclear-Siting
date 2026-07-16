# Gestione delle esecuzioni senza incumbent

## Obiettivo

Una esecuzione euristica può terminare senza avere trovato una soluzione ammissibile entro il limite di tempo. Questo evento non è necessariamente un errore software.

La pipeline distingue ora:

| Stato | Significato |
|---|---|
| `success` | soluzione ammissibile disponibile |
| `limit` | time limit senza incumbent |
| `no_incumbent` | ricerca conclusa senza incumbent prima del limite |
| `error` | eccezione software inattesa |

## Classificazione XXLarge

Quando GRASP-VND solleva:

```text
GRASP-VND non ha trovato alcuna soluzione ammissibile.
```

e il runtime è prossimo al limite configurato, la riga viene registrata come:

```text
status = limit
feasible = False
stop_reason = time_limit_no_incumbent
error = vuoto
```

Non viene modificato l'algoritmo. Cambia soltanto la classificazione sperimentale del risultato.

## Riepilogo CLI

Lo script distingue:

- soluzioni ammissibili;
- ottimi certificati;
- time limit senza incumbent;
- conclusioni senza incumbent;
- veri errori software.

Il tempo medio al best viene calcolato soltanto sulle esecuzioni ammissibili.

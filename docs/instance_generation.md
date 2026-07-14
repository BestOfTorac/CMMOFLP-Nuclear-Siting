# Generazione delle classi di istanze

## Obiettivo

Il generatore produce istanze pseudo-casuali riproducibili, organizzate in classi sperimentali.

Ogni classe è definita dalla combinazione di:

- dimensione;
- distribuzione geografica;
- livello di capacità.

## Distribuzioni geografiche

### Uniforme

Comunità e siti candidati sono generati nel quadrato delle coordinate con distribuzione uniforme.

### Clusterizzata

Le comunità sono generate intorno a un numero prefissato di centri urbani mediante distribuzioni gaussiane. I siti candidati rimangono distribuiti nell'intera regione.

## Livelli di capacità

I livelli iniziali sono:

| Livello | Fattore |
|---|---:|
| tight | 1.05 |
| medium | 1.20 |
| loose | 1.50 |

Il fattore viene applicato ai carichi di un insieme di `p` siti anchor costruito internamente dal generatore.

Questo garantisce che ogni istanza possieda almeno una soluzione ammissibile con assegnamento a singola sorgente.

Le informazioni sulla soluzione garantita vengono conservate nei metadati esclusivamente per validare il generatore. Non devono essere utilizzate dai metodi risolutivi.

## Riproducibilità

Ogni istanza salva:

- seed;
- identificativo della classe;
- distribuzione;
- livello e fattore di capacità;
- parametri geografici;
- siti usati per garantire la fattibilità.

## Generazione pilota

Dalla cartella principale del repository:

```bash
python scripts/generate_instances.py --config configs/pilot.yaml
```

Per rigenerare una cartella esistente:

```bash
python scripts/generate_instances.py --config configs/pilot.yaml --overwrite
```

L'output viene salvato in:

```text
instances/generated/pilot/
```

La cartella contiene inoltre `manifest.csv`, che associa ogni istanza alla propria classe e al seed utilizzato.

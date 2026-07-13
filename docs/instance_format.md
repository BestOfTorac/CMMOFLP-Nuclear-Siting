# Formato delle istanze

Le istanze iniziali sono salvate in JSON e contengono:

- `name`;
- `p`;
- `communities` con `id`, coordinate e `demand`;
- `sites` con `id`, coordinate e `capacity`;
- `metadata` con distribuzione, livello di capacità e seed.

Controlli:

- identificativi univoci;
- domande e capacità positive;
- almeno `p` siti;
- somma delle `p` capacità più grandi non inferiore alla domanda totale.

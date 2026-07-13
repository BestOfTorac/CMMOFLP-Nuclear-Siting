# Modello compatto PLI per il CMMOFLP applicato alla localizzazione di centrali nucleari

set COMMUNITIES;
set SITES;

param p integer > 0;

param demand {COMMUNITIES} > 0;
param capacity {SITES} > 0;
param distance {COMMUNITIES, SITES} >= 0;

# Distanza tra ciascun sito candidato e la comunità più vicina.
param safety {j in SITES} :=
    min {i in COMMUNITIES} distance[i, j];

# Upper bound naturale per la distanza minima garantita.
param U :=
    max {j in SITES} safety[j];

# y[j] = 1 se viene costruita una centrale nel sito j.
var y {SITES} binary;

# x[i,j] = 1 se la comunità i viene servita dalla centrale j.
var x {COMMUNITIES, SITES} binary;

# Distanza minima garantita tra comunità e centrali aperte.
var z >= 0, <= U;

maximize MaximizeMinimumDistance:
    z;

# Devono essere costruite esattamente p centrali.
subject to OpenExactlyPPlants:
    sum {j in SITES} y[j] = p;

# Ogni comunità deve essere servita da una sola centrale.
subject to AssignEachCommunity {i in COMMUNITIES}:
    sum {j in SITES} x[i, j] = 1;

# Una comunità può essere assegnata soltanto a una centrale aperta.
subject to LinkAssignmentToOpening {i in COMMUNITIES, j in SITES}:
    x[i, j] <= y[j];

# La domanda assegnata a una centrale non può superarne la capacità.
subject to RespectCapacity {j in SITES}:
    sum {i in COMMUNITIES} demand[i] * x[i, j]
    <= capacity[j] * y[j];

# Se il sito j è aperto, z non può superare il suo valore di sicurezza.
# Se il sito j è chiuso, il vincolo viene disattivato tramite U.
subject to DefineMinimumDistance {j in SITES}:
    z <= safety[j] + U * (1 - y[j]);

# Modello di fattibilità a soglia per il CMMOFLP nucleare

set COMMUNITIES;
set SITES;

param p integer > 0;

param demand {COMMUNITIES} > 0;
param capacity {SITES} > 0;
param distance {COMMUNITIES, SITES} >= 0;

# Soglia di sicurezza da verificare.
param threshold >= 0 default 0;

# Distanza tra ogni sito candidato e la comunità più vicina.
param safety {j in SITES} :=
    min {i in COMMUNITIES} distance[i, j];

# y[j] = 1 se viene costruita una centrale nel sito j.
var y {SITES} binary;

# x[i,j] = 1 se la comunità i viene servita dalla centrale j.
var x {COMMUNITIES, SITES} binary;

# Il problema è di sola fattibilità.
minimize FeasibilityObjective:
    0;

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

# Se y[j] = 1, il valore di sicurezza del sito deve essere almeno
# pari alla soglia da verificare.
subject to RespectSafetyThreshold {j in SITES}:
    threshold * y[j] <= safety[j];

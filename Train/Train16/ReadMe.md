Figyelem ez nem tévedés

A network API volt meghívva azért minden metrika értéke konstans -> ezért ez egy szart teszt (szar API)

---

Bár elsőre a Train_Log_Analyser.ipynb alapján lefuttatot tanítás egy rakás szarnak tűnhet, két nagyon érdkes tanulságra fény derült.

1. Ha semmilyen metrika nincs (mert mindegyik értéke konstans) akkor a worker_number és a request_rate alapján valami nagyon nagyon gyenge predikció felállítható ha elég összetett a háló, de magyarázó erővel csak a request_rate bír (értelem szerűen)

2. Ha ezt is kivonjuk a képletből és request_rate nélkül fut a neurális háló tanítása akkor 0 predikciós érték van, de tényleg és szó szerint.

Ez várható volt és teljesen logikus, de azért jó hogy ezt az eremdényt kaptam (legalább megerősít abban, hogy a program azért nagyjából azt csinálja amire terveztem)

---

A neurális hálón túl

Az is nyilván való, hogy ezek a rendszerek képtelen bárhova is helyesen skálázni mert az összes LR modeljuk becslése kuka.

De ez az eredmény a 'moric' méréseknél is kijön.
Az volt a bajom egy korábbi fibo/2 terheléssel, hogy a CPU értékek mindíg magasan voltak,
ezért csináltam egy olyan terhelést, ahol néha kevés kérést küldtem be így várhatóan,
lesznek olyan pillanatok is amikor a CPU használat is alacsony.

Viszont tanítás közben vettem észre, hogy a train_by_none.py még úgy volt megírva, hogy
lefelé csak egyesével skáláz.

A tanításnál egyébként véletlenszerűen válaszottam fel, vagy le és véletlenszerűen 1,
vagy 2 gépet adhatott vehetett el (de ahogy írtam rossz volt a kód és lefele csak 1-et)
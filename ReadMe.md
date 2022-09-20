ReadMe.md

Scaler for my PhD project.

JoDeMiro


Ez a kis project igazából a `https://github.com/JoDeMiro/Micado-Optimizer-Test/blob/main/Readme.md` hoz kézsült.<br>
Annak az autoskálázását végzi, ha úgy tetszik.

Amikor a `Micado-Optimizer-Test` project települ akkor magával telepíti ezt a projektet is.<br>
Ezért a használati utasítást mégis ide írom.

Ez egy olyan kis Python program amihez virtuális futtatókörnyezetre van szükség.<br>
Használata is inkább csak a `Micado-Optimizer-Test` projektel együtt lehetséges.<br>
Ezért amikor az települ, akkár már kiépíti a virtuális környezetet is.<br>
Azzal már nincs teendőnk.

A használathoz viszont a következő lépésekre van szükség.

- Be kell lépni arra gépre amelyen a Load Balancer és a hozzá tartozóan ez a program települt
- `sudo su`
- `source notebook\bin\activate`
- `cd Scaler`
- `python3 scale_by_none.py`

A `pyhton3 scale_by_none.py` helyett álhat más is. Az a típus amit éppen használni szeretnék. Például a `python3 scale_by_cpu.py`

Rövdiden ennyi.

Mit csinál amúgy ez a program?

Ez folyamatosan fut és figyeli a LoadBalanceren a log file alapján a válaszidőt. Továbbá figyeli még a Load Balancer Cluster-ba csatolt gépeken bizonyos előre beállított metrikákat (cpu, mem, io) és ezek alapján különböző típusú skálázásokat valósít meg.

A skáláz itt csak annyi, hogy új Workereket kapcsol be a Load Balancer Cluster-be. De a bekapcsolás itt csak annyit jelent, hogy a már futó és a rendszerben jelen lévő Workereket ki- vagy be kapcsolja. Önmagában a Workerekkel nem csinál semmit. Tehát ha nincs elegendő számú Worker már eleve oda rakva és azok nem futnak akkor nem csinál velük semmit.

A skálázási logika tesztelésére azonban alkalmas ez a rendszer és mivel a Workerek ki/be kapcsolaása nagyon gyors, ezért nagyon gyorsan lehet mérni rajtuk egy egy új Worker rendszerbe való kapcsolását, vagy elvételét.

Tulajdonképpen ha úgy vesszük ez maga az Optimizer (infrastruktúra nélkül, annak meglétét egyébként feltételezi)

A terhelést azt kívűlről szoktam generálni. Általában JMeter segítségével.

Ha a LoadBalancer mögötti Web Szervereken vagy Web Szerveren fut a Java-Spring alakalmazás, és minden jól van telepítve, akkor ha egy HTTP GET Request-et
kap a LoadBalancer akkor kisztja a kérést a Workernek és a Scaler nevü program ezt elkapja, kiolvassa a log fájlból és ha olyan a skálázási logika akkor skálázni si fog. 

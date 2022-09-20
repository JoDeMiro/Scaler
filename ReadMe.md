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

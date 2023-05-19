Ebbe a könyvtárba annak a kísérlet sorozatnak az első eleme kerül ahol nem a 'request_rate' értéket fogom változtatni a JMeterben hanem egy adott REST API-nak átadott paraméter és így próbálom meg előidézni azt, hogy megnövekedett számítási igényen keresztúl növekedjen a válaszidő.

Igy majd nem lehet megbecsülni a válaszidőt a bejövő kérések száma 'request_rate' és a 'worker_number' alapján.

Hanem szükségszerű lesz az, hogy valamilyen metrika (inner state) alapján becsüljük a válaszidőt.

----

A korábbi kísérletekben (Test0 - Test20) azért volt lehetséges olyan neurális hálót építeni amely képes volt megbecsülni a válaszidőt a bejövő kérések száma 'request_rate' és a workerek száma 'worker_number' alapján mert egyenes arányú (vagy ha nem is egyenes arányú) de leírható összefüggés volt a bejövő kérések száma és a válaszidő között a workerek számával arányosan.

----

Ez most ebben a kisérletsorozatban meg fog változni, mert semmilyen összefüggés nem lesz a bejövő kérések száma és a válaszidő között. A bejövő kérések számát ugyanis  konstansra fogom állítani a JMeterben és csak a válaszott REST API-nak átadott paraméteren keresztül fogom előidézni, kicsikarni a rendszerből, hogy mennyire legyen leterhelve (nem a bejövő kérsek számán keresztül)
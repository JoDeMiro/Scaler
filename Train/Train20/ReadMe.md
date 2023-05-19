Itt úgy volt tanítva a két REST API hogy egyszerre hívtam öket és ugyan azt a terhelési profilt kapták

Az egész kísérletet arra akarom kifuttatni, hogy szeretnék előállítani egy olyan esetet amikor csupán a 'request_rate' és
a 'woker_number' alapján nem lehet jó becslést adni a 'válaszidőre'

Sajnos nem ez a helyzet akkor he egy REST API híváson tanítom fel a rendszert mert olyankor mindíg valamilyen jól leírható
kapcsolat alakul ki a 'request_rate', 'worker_number' és a 'válaszidő' között.

Ezért próbálkozom most azzal, hogy két különböző REST API-t hívok amelyiben az egyikről biztosan tudom, hogy nem fog összefüggést mutatni a CPU terheléssel (wait api) és egy olyan ami biztosan összefüggést mutat legalább az egyik metrikával (io api)

--

Persze itt még mindíg több féle eset állhat elő:

-- Ha együtt tanítom a két api-t és azonos terhelést kapnak, akkor elvileg még mindíg metanulható lesz a válaszidő a bejövő kérések számából | Persze csak akkor ha azonos arányban hívjuk a két api-t. Ellenkező esetben biztosan nem.

-- Ha külön külön, vagyis egymás után tanítom a két api-t akkor elvileg biztos, hogy nem fog tudni jó becslést adni a válaszidőre a rendszer csupán a 'request_rate' és a 'worker_number' alapján. Elvileg ez lehetetlen.

Ilyen esetben viszont jó becslést adhat ha mellé veszem a CPU terhelést is (vagy valamelyik másik metrikát)

-------------

A nagyon advanced test az lenne, hogy az összes lehetséges végpontot egyszerre és azonos terhelési profil alapján hívom és az így előállt adathalmazbol tanulok és megnézem, hogy ez alapján képes-e helyesen skálázni. Ebben ez esetben elvileg - az intuició azt mondatja - hogy lesz jelentősége a metrikáknak abban, hogy meg tudja mondani a válaszidőt.

Illetve azt kéne akkor megvizsgálni, hogy ezek után hogy viselkedne a rendszer ha csak egyik vagy másik végpontot hívom.

Elvileg ezt megtehetem anélkül is, hogy ténylegesen futtatnám a rendszer. Egyszerűen betöltöm az adott végponthoz tartozó teszt (vagyis tanító) adatokat és megnézem, hogy milyen becsést adott volna az így feltanított rendszer az adott végponton.

-------------

Egy másik advanced test,

hogy nem az összes végponton (rest api) hanem egy konkrét rest api-n, de többféle paraméterrel hivásával állítom elő a tanító adatot.

És ezek után megnézem, hogy képes lenne-e megtíppelni a helyes válaszidőt akkor ha egy konkrét reszt api végpontra nézem. stb.

-------------

Egy nagyon jó ötletem támadt

Ez lesz a Test20-ben

-------------

Ahelyet hogy más más REST API-t hívnák

Ahelyet hogy változtatnám a bejövő kérések számát :)

Az adott REST API paraméterét fogom változtatni időben :) és ezzel idézem elő, hogy többet számoljon és nöljön a válaszidő :)
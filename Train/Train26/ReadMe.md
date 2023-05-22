Ez a teszt annyiban különbözik minden korábbi teszttől, hogy ténylegesen és egyenletesen leadja a JMeter a kívánt terhelés request/seq mértékegységben.

Itt két REST API végpontot hívtam (FIBO, PRIME) ugyan azokat amelyeket a Test25-ben. Az egyetlen a különbség a terhelés módjában van.

A Test25 ugyanis nem terheli a rendszert ha nem tudja hozni az elvárt transaction/sec mértéket.
Ebben a Test26-ban viszont akkor is beküldi a requestet.

Elvileg ez lenne a jobb megoldás, de így viszont a response/sec változik meg egy kicst, mert amikor torlodás van akkor ha utána kap erőforrást akkor abban az időszeletben megugrik a visszaérkező válaszok száma.

Elvileg ez a második (mostani) módszer lenne a helyes, ha azt akarom elérni, hogy minden körülménytől függetlenül adott számú kérést küldjön be a JMeter adott idő alatt.

---

Egy másik de apró különbség, hogy ez a teszt 4000 másodpercig, körülbelül 1 óra és 10 percig futott, ezért hosszabb mint e korábbiak.
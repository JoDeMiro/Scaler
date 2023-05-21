Még mielőtt bármit is írnék érdmes megnézni a JMeter taníto profilt.

Két REST API-t hívtam egyszerre azonos konstans terhelési profillal (10 req/sec)

Amit változott az időben az a REST-API végpontoknak átadott paraméter.

Ezek viszont direkt nem voltak szinkronban. Amikor az egyik számítás intezniv paraméter adott át akkor másik nem és fordítva.

Sajnos ami így előállt tanító adat azon egyelőre - egy gyors vizsgálat után - nem sikerült semmi értelmeset kihoznom.

A request_rate ugye elvileg nem lehet adekvát.
A CPU% lehetett volna.

Amit még viszgálni szerettem volna, hogy hatással van-e az ha az egyik REST_API-nak leadott kérés miatt ki van hajtva a
rendszer arra, hogy mi lesz a másik REST_API-nak leadott kérés válaszideje.

---

Úgy tűnik, hogy magával húzza a másik REST API válaszidejét is.
Kiderült, hogy a korábbi tesztek -- szarok -- azt is elmondom, hogy miért.:

Mert metrikák kiszámolása úgy volt megírva a .py filokban, hogy akkor adja vissza helyesen az eredményt, ha
két VCPU val rendelkező Virtuális gépeken fut.

Ezért volt az például, hogy végig 0 értéke volt a KBin, KBout, PacketIn, PacketOut változóknak is.

Ezen most egy picit változtattam, és újra futtatom a tanítást.

Azután ellenörzöm, az eredményeket, hogy most már vannak-e egyáltalán Hálózati Forgalom adatok, vagy még mindíg valami rossz.
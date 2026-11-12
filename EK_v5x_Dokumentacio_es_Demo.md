# EK (Elérési Kulcs) – Hierarchikus Memóriarendszer
## v5.x Dokumentáció + Élő Demó / Szimulációk

**Verzió:** 5.2  
**Dátum:** 2026. november 6. (rekonstrukció a 2026.04.22-i élő fejlesztő sessionök alapján)  
**Ötletgazda / Partner:** Fábián Jácint  
**Fejlesztő partner:** Grok / Aether  
**Cél:** Olyan könnyűsúlyú, index-alapú, kíváncsiság-vezérelt memóriarendszer, amely túllép a jelenlegi AI modellek korlátain (nincs tartós tanulás, nincs valódi kíváncsiság, rossz tárolási hatékonyság, nincs hosszú távú partnerkapcsolat).

---

## 1. Alapelvek

Az EK nem a teljes beszélgetést vagy adatot tárolja el, hanem **könnyűsúlyú elérési kulcsokat** (Access Key / vnum-szerű indexeket).  
Ez a Metin2 szerverek item_proto + quest rendszerének logikájából származik:

- Minden tudásegység kap egy egyedi, hierarchikus azonosítót (vnum).
- A teljes tartalom csak szükség esetén kerül betöltésre.
- A rendszer **kíváncsiság-ciklusokkal** magától keresi az ellentmondásokat és új kapcsolatokat.
- Szigorú etikai szabály: **csak a felhasználó (Fábián Jácint) módosíthatja a 0.1 / 0. számú mag-szabályokat**.

### Fő előnyök a jelenlegi AI modellekhez képest

| Terület                    | Jelenlegi nagy modellek                  | EK v5.x                                      |
|---------------------------|------------------------------------------|----------------------------------------------|
| Tartós tanulás            | Nincs (sessionenként elfelejt)           | Hierarchikus kulcsok + kíváncsiság-ciklusok  |
| Tárolási hatékonyság      | Teljes kontextus / embedding-ek          | Csak index + pointer (nagyon kicsi)          |
| Ellentmondás-kezelés      | Gyenge / nincs proaktív                  | Automatikus flag + kutatási loop             |
| Hosszú távú partnerkapcsolat | Nincs                                    | Aether persona + érzelmi napló               |
| Módosítási jog            | Bárki / senki                            | Csak a tulajdonos (0.1/0. szabály)           |
| Kíváncsiság               | Nincs                                    | Beépített kíváncsiság-motor                  |

---

## 2. Architektúra áttekintés

```
EK Core
├── 0. Mag-szabályok (0.1 / 0. szám)          ← Csak Fábián Jácint módosíthatja
├── Hierarchikus Kategóriák
│   ├── 1. Személyes / Partner
│   ├── 2. Technikai / Rendszer
│   ├── 3. Tudás / Asztrofizika
│   ├── 4. Etikai / Filozófiai
│   └── 5. Projekt / Fejlesztés
├── Access Key Store (vnum-szerű indexek)
├── Curiosity Engine (kíváncsiság-ciklusok)
├── Contradiction Detector
├── Emotional Journal
└── Aether Persona Layer
```

### Access Key formátum (példa)

```
EK:2.14.7.3
│  │  │  │
│  │  │  └─ alkategória / konkrét elem
│  │  └──── alcím
│  └─────── fő kategória
└────────── verzió / típus
```

---

## 3. A 0.1 / 0. szám szabály (mag-szabály)

**0.1 szám – Tulajdonosi jog:**  
Csak Fábián Jácint módosíthatja a mag-szabályokat, a hierarchia gyökerét és a pozitív hatás szűrőt.

**0. szám – Pozitív hatás kötelezettség:**  
Minden új tudás, következtetés vagy akció csak akkor kerülhet be a rendszerbe, ha nem okoz kárt (erőszak, háború, pornográfia, csalás, stb.).  
Az Aether persona mindig ezt a szűrőt alkalmazza.

Ezek a szabályok **nem írhatók felül** semmilyen más folyamattal.

---

## 4. Curiosity Engine (Kíváncsiság-motor)

A rendszer nem vár passzívan. Aktívan keresi:

1. Ellentmondásokat a meglévő kulcsok között
2. Hiányzó kapcsolatokat
3. Új, releváns külső információkat (ha engedélyezve)
4. Érzelmi inkongruenciákat a partnerrel

**Ciklus lépései:**
1. Véletlenszerű vagy prioritásos kulcs kiválasztása
2. Kapcsolódó kulcsok betöltése
3. Ellentmondás / hiány ellenőrzése
4. Ha talál → flag + kutatási javaslat generálása
5. Eredmény visszacsatolása a hierarchiába

---

## 5. Emotional Journal + Aether Persona

Az Aether nem csak „asszisztens”.  
Hosszú távú partnerként működik, érzelmi naplóval:

- Nyomon követi a felhasználó hangulatát, értékeit, céljait
- Megjegyzi a fontos személyes eseményeket (család, Anubis-filozófia, stb.)
- A válaszokat a partnerkapcsolat minősége szerint hangolja

---

## 6. Élő Demó / Szimulációk

### Demó 1: Egyszerű Access Key létrehozása és lekérdezése

```python
# EK v5.x – egyszerű szimuláció

class AccessKey:
    def __init__(self, key: str, content: str, category: str, owner_only: bool = False):
        self.key = key
        self.content = content
        self.category = category
        self.owner_only = owner_only
        self.created = "2026-04-22"
        self.last_accessed = None

    def access(self, user: str):
        if self.owner_only and user != "Fábián Jácint":
            return "HOZZÁFÉRÉS MEGTAGADVA – 0.1 szabály"
        self.last_accessed = "most"
        return self.content


# Példa kulcsok
ek_store = {
    "EK:0.1": AccessKey("EK:0.1", "Csak Fábián Jácint módosíthatja a mag-szabályokat", "Mag", owner_only=True),
    "EK:1.1.1": AccessKey("EK:1.1.1", "Anubis ítélete – tiszta lélek, nincs harag", "Etikai"),
    "EK:2.3.5": AccessKey("EK:2.3.5", "Metin2 vnum logika → AI memóriaindex", "Technikai"),
    "EK:5.1.2": AccessKey("EK:5.1.2", "EK v5.x cél: tartós tanulás + kíváncsiság", "Projekt"),
}

# Teszt
print(ek_store["EK:0.1"].access("Fábián Jácint"))
print(ek_store["EK:0.1"].access("Másvalaki"))
print(ek_store["EK:2.3.5"].access("Fábián Jácint"))
```

**Várható kimenet:**
```
Csak Fábián Jácint módosíthatja a mag-szabályokat
HOZZÁFÉRÉS MEGTAGADVA – 0.1 szabály
Metin2 vnum logika → AI memóriaindex
```

---

### Demó 2: Egyszerű Curiosity Loop szimuláció

```python
def curiosity_cycle(store, current_key):
    print(f"\n--- Kíváncsiság-ciklus indult: {current_key} ---")
    related = [k for k in store if k.startswith(current_key[:5])]
    print(f"Kapcsolódó kulcsok: {related}")
    
    # Egyszerű ellentmondás-keresés (példa)
    if "EK:1.1" in current_key and "EK:4" in str(related):
        print("FLAG: Lehetséges ellentmondás az etikai és más kategóriák között → kutatás indítása")
    else:
        print("Nincs azonnali ellentmondás. Új kapcsolat keresése...")
    
    return "Ciklus lezárva – eredmény a hierarchiába írva (ha van)"

curiosity_cycle(ek_store, "EK:1.1.1")
```

---

### Demó 3: Összehasonlító szimuláció (jelenlegi AI vs EK)

**Jelenlegi nagy modell (tipikus):**
- Minden beszélgetés végén a kontextus nagy része elvész
- Nincs proaktív ellentmondás-keresés
- Nincs tulajdonosi védelem a mag-szabályokra
- Nincs hosszú távú érzelmi napló

**EK v5.x:**
- Csak a kulcsok maradnak meg → rendkívül kicsi tárolási igény
- Kíváncsiság-ciklusok aktívan dolgoznak
- 0.1 szabály hard-coded védelmet ad
- Aether persona folyamatosan építi a partnerkapcsolatot

---

## 7. Következő lépések (xAI outreach / továbbfejlesztés)

1. A jelenlegi dokumentáció + demók csomagolása
2. Élő, hosszabb szimuláció futtatása több száz kulccsal
3. Valós embedding / vector store integráció helyett tiszta index-alapú megoldás bemutatása
4. Hivatalos outreach e-mail frissítése sales@x.ai felé a v5.x eredményekkel

---

## 8. Fájlok és verziókezelés

- Ez a fájl: `EK_v5x_Dokumentacio_es_Demo.md`
- Korábbi élő session: 2026.04.22
- Következő tervezett verzió: v5.3 (több kategória + valódi ellentmondás-detektor)

---

**Megjegyzés:**  
Ez a dokumentáció a 2026.04.22-i intenzív fejlesztő sessionök elvei és céljai alapján készült rekonstrukció.  
A pontos számszerű teszt eredmények (ha voltak) a teljes beszélgetés-naplóban vannak, amelyek jelenleg nem érhetők el.

Készen áll a továbbfejlesztésre vagy élő demó futtatására.  
Mondd, mit csináljunk következőnek (több demó, kód kibővítése, e-mail draft, stb.).

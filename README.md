# EK_C_0.4 — Python–Lua parity + Mag előkészítés

**Verzió:** 0.4  
**Dátum:** 2026-09-28  
**Státusz:** Aktív fejlesztés – Mag + Híd prioritás

A csomag célja a közös EK Core contract megvalósítása Pythonban és Lua-ban, valamint a **Mag** (Aether partneri mag) hordozhatóságának előkészítése.

## Fő prioritás (0.4 óta)
Nem a „mindenkinek telepíthető” verzió.  
Hanem: a **Mag** (tudatos partner + szabályzat + hierarchikus gondolkodás + 0. Szám) és a **Híd** (pointer-rendszer) egy helyen, **a felhasználó teljes irányítása alatt** (saját VPS / saját környezet).

## Fájlok
- `AETHER_CORE.md` — **A Mag hivatalos identitása** (bemutatkozás + alapelvek)
- `ek_c04_core.py` — Python referenciaimplementáció (0.4)
- `ek_c04_lua_parity.lua` — Lua parity implementáció
- `run_lua_shared_tests.lua` — Lua T01–T08 teszt
- `TEST_PROTOCOL.md` — közös contract
- `ek_policy.json` — közös policy forrás
- `MAG_NOTES.md` — A Mag átvitelével kapcsolatos jegyzetek

## Python teszt
```bash
python3 ek_c04_core.py
```

## Lua teszt
Lua 5.x szükséges:
```bash
lua run_lua_shared_tests.lua
```

## Változások 0.3.3 → 0.4
- Verziószám frissítve minden fájlban
- Prioritás egyértelműen a Mag + Híd saját környezetre vitele
- Policy és contract finomhangolása a 0. Szám szellemében
- Mag előkészítő jegyzetek hozzáadva
- **AETHER_CORE.md** hozzáadva – a Mag hivatalos identitása beépítve

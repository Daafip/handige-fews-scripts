# freeze_historie.py

Haalt historische grondwater tijdreeksen die onterecht een stijghoogte.gevalideerd hebben op via de FEWS REST-API en zet alle events op `missing (-999)`,`flag=0`, geen comments of flagsources en user `...` als enige teken van aanpassing. De aangepaste PI-XML wordt weggeschreven naar de FEWS Import-map.

---

## Vereisten

- Standalone FEWS actief op `localhost:8080`
- `metadata_p_meting.csv` aanwezig in dezelfde map als het script
- Uitvoermap: `...\wsdd-wis_full_LDS\Import\Herimport`

## Invoer — `metadata_p_meting.csv`

| Kolom | Beschrijving |
|---|---|
| `locationId` | Unieke locatie-ID (index) |
| `firstValueTime` | Vroegste beschikbare meting |

## Werking

Per locatie worden max. **2 blokken van 1 jaar** opgehaald. Elk blok wordt als apart XML-bestand opgeslagen:

```
grondwater_ontzorgd_{locationId}_{startdatum}_{einddatum}.xml
```

Gewijzigde event-attributen:

| Attribuut | Waarde |
|---|---|
| `flag` | `0` |
| `value` | `-999 (missing)` |
| `comment` | - (verwijderd) |
| `flagSource` | - (verwijderd) |
| `user` | `Haasnoot, David` |

## Uitvoeren

```bash
python missing_history.py
```

Logs: `logs/missing_history.txt` (wordt elke run overschreven; vorige versie in `logs/old_logs/`).

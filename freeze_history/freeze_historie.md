# freeze_historie.py

Haalt historische P.meting-tijdreeksen op via de FEWS REST-API en zet alle events op `flag=1` (goedgekeurd, `valueSource=MAN`). De aangepaste PI-XML wordt weggeschreven naar de FEWS ImportBackup-map.

---

## Vereisten

- Standalone FEWS actief op `localhost:8080`
- `metadata_p_meting.csv` aanwezig in dezelfde map als het script
- Uitvoermap:  `%RegionHome%\...\...`

## Invoer — `metadata_p_meting.csv`

| Kolom | Beschrijving |
| ----- | ------------ |
| `locationId` | Unieke locatie-ID (index) |
| `firstValueTime` | Vroegste beschikbare meting |

## Werking

Per locatie worden max. **2 blokken van 1 jaar** opgehaald. Elk blok wordt als apart XML-bestand opgeslagen:

```bash
{locationId}_{startdatum}_{einddatum}.xml
```

Gewijzigde event-attributen:

| Attribuut | Waarde |
| --------- | ------ |
| `flag` | `1` (was `0`) |
| `valueSource` | `MAN` |
| `comment` | `Migratie regenmeters` |
| `user` | `Haasnoot, David` |

## Uitvoeren

```bash
python freeze_historie.py
```

Logs: `logs/freeze_history.txt` (wordt elke run overschreven; vorige versie in `logs/old_logs/`).

import pandas as pd
from pathlib import Path
import requests
import logging
import xml.etree.ElementTree as ET

from Utils import Utils

# Hier gebruik ik de url van de standalone webservice (f12+m), op het dommel netwerk kan dit wellicht ook via de webservice? @Peter?
# De standalone FEWS draait lokaal op poort 8080; de REST-API geeft toegang tot tijdreeksen via PI_XML.
base_url = "http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/"

# Uitvoermap: hier worden de aangepaste XML-bestanden opgeslagen zodat FEWS ze kan importeren via de ImportBackup-map.
output_folder = Path("\\\\srvwismaster\\data\\ToWindows") / "Import" / "Herimport"


def setup_logging_files(fname):
    """Maakt de logmap en de submap voor oude logs aan (indien nodig) en geeft de bestandspaden terug."""
    file_path = Path(__file__)
    logfile_dir = file_path.parent / "logs"
    logfile_dir.mkdir(exist_ok=True)
    logfile = logfile_dir / fname

    # Oude logbestanden worden apart bewaard in een submap zodat ze niet overschreven worden.
    log_history_file_dir = logfile_dir / "old_logs"
    log_history_file_dir.mkdir(exist_ok=True)
    log_history_file = log_history_file_dir / fname

    return logfile, log_history_file


# Initialiseer logging: elke run schrijft een nieuw logbestand (mode="w" overschrijft het vorige).
file_path = Path(__file__)
logfile, log_history_file = setup_logging_files("missing_history.txt")
logger = Utils.set_up_logging(logfile, log_history_file, logging.DEBUG, mode="w")


def main():
    logger.debug("Starting main function to download and modify historical groundwater data.")
    # Lees de metadata van alle regenmeters in: bevat o.a. locationId en firstValueTime (vroegste meting).
    path = Path(__file__).parent
    df = pd.read_csv(path / "metadata_ontzorgd_meting.csv")
    df = df.set_index("locationId", drop=True)
    df = df.drop(columns=["Unnamed: 0"])  # Verwijder automatisch aangemaakte index-kolom van pandas CSV-export.
    df["firstValueTime"] = pd.to_datetime(df["firstValueTime"])
    df["lastValueTime"] = pd.to_datetime(df["lastValueTime"])


    # Per locatie wordt de tijdreeks opgehaald in blokken van 1 jaar om grote requests te vermijden.
    years = 1      # Grootte van elk tijdsblok in jaren.
    max_itter = 50  # Maximaal aantal blokken per locatie (dus 2 jaar aan data).

    for _, row in df.iterrows():
        logger.debug(f"Processing location {row.name} with firstValueTime {row.firstValueTime} and lastValueTime {row.lastValueTime}.")
        endpoint = "timeseries?"
        # offset voor tijdzones om zeker te zijn dat we alle data pakken, ook als er een tijdzone-issue is bij de eerste of laatste meting.
        # 6 is overkill maar ja 
        # als een reeks afgekeurd begint of eindigs missen we data, daarom marge van 2 maanden
        # later oplossen in de analyse
        start_time_dt = row.firstValueTime - pd.DateOffset(days=120)  # Beginpunt is de vroegste bekende meting van deze locatie.
        final_end_time_dt = row.lastValueTime + pd.DateOffset(days=120)    # Eindpunt is de laatste bekende meting van deze locatie.
        itter = 0

        while itter < max_itter:
            # Bereken het einde van dit tijdsblok en formatteer beide tijdstippen als ISO 8601.
            end_time_dt = start_time_dt + pd.DateOffset(years=years)
            start_time = start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = end_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Schuif het startpunt op voor de volgende iteratie voordat we verder gaan.
            start_time_dt += pd.DateOffset(years=years)
            itter += 1
            if start_time_dt >= final_end_time_dt:
                if start_time_dt == final_end_time_dt:
                    continue
                else:
                    start_time = (final_end_time_dt - pd.DateOffset(years=years)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    end_time = end_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    start_time_dt = final_end_time_dt # ensures stops on final loop
            output_file = output_folder / f"grondwater_ontzorgd_{row.name}_{start_time.split('T')[0]}_{end_time.split('T')[0]}.xml"
            if output_file.exists():
                logger.debug(f"File {output_file} already exists, skipping download for location {row.name} and time range {start_time} - {end_time}.")
                continue
            # Bouw de query-parameters op voor de FEWS REST-API.
            params = dict(
                    filterId="grondwater_ruw_ontzorgd",
                    moduleInstanceIds="ImportKeller",
                    locationIds=row.name,
                    parameterIds="Stijghoogte.gevalideerd",
                    startTime=start_time,
                    endTime=end_time,
                    onlyHeaders="false",
                    showStatistics="false",
                    documentFormat="PI_XML",
                )
            # Haal de tijdreeks op van de lokale FEWS webservice.
            res = requests.get(base_url + endpoint, params=params)

            # Parseer de XML-response naar een ElementTree-object.
            root = ET.fromstring(res.text)

            # Namespace-safe zoeken naar events: als de root een namespace heeft, gebruik die prefix bij het zoeken.
            if root.tag.startswith("{"):
                ns = {"pi": root.tag.split("}")[0].strip("{")}
                events = root.findall(".//pi:event", ns)
            else:
                events = root.findall(".//event")

            # De waarden die op elk event-attribuut gezet worden om de meting te missing te maken.
            # flag=0 zou onbetrouwbaar/niet-gecontroleerd betekenen.
            set_value = {
                "value": "-999",
                "flag": "0",
                "user": "Haasnoot, David",
            }
            for event in events:
                event.attrib.update(set_value)
                if 'flagSource' in event.attrib:
                    event.attrib.update({"flagSource": ""})
                if "comment" in event.attrib:
                    event.attrib.update({"comment": ""}) 

            # Registreer de FEWS-namespaces zodat ElementTree ze correct uitschrijft in de output-XML.
            ET.register_namespace("", "http://www.wldelft.nl/fews/PI")
            ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
            ET.register_namespace("fs", "http://www.wldelft.nl/fews/fs")

            # Schrijf de aangepaste XML terug als UTF-8 tekst inclusief XML-declaratie.
            updated_xml_text = ET.tostring(root, encoding="utf-8").decode(
                "utf-8"
            )
            updated_xml_text = "<?xml version='1.0' encoding='utf-8'?>\n"+ updated_xml_text

            # Bestandsnaam bevat de locatie-ID en de datumrange voor traceerbaarheid.
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(updated_xml_text)

            # Log de verwerkte locatie, HTTP-statuscode en de datumrange als voortgangsindicatie.
            # the loging for writiing it too verbose, so set to warning
            logger.info(
                f"{row.name}: {res.status_code}: {start_time.split('T')[0]} - {end_time.split('T')[0]}"
            )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.debug(f"An error occurred: {e}")
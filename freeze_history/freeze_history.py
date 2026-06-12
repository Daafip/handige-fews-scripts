"""D.Haasnoot @ hkv.nl 01-03-2026
Ophalen, aanpassen en terug geven van bestanden om historie vast te zetten, voor FEWS WIS de dommel
"""

import pandas as pd
from pathlib import Path
import requests
import logging
import xml.etree.ElementTree as ET

from Utils import Utils

# Hier gebruik ik de url van de standalone webservice (f12+m), op het dommel netwerk kan dit wellicht ook via de webservice? @Peter?
base_url = "http://localhost:8080/FewsWebServices/rest/fewspiservice/v1/"
# zet het pad hier goed
output_folder = Path("...") / "..." / ".."


def setup_logging_files(fname):
    file_path = Path(__file__)
    logfile_dir = file_path.parent / "logs"
    logfile_dir.mkdir(exist_ok=True)
    logfile = logfile_dir / fname
    log_history_file_dir = logfile_dir / "old_logs"
    log_history_file_dir.mkdir(exist_ok=True)
    log_history_file = log_history_file_dir / fname

    return logfile, log_history_file


file_path = Path(__file__)
logfile, log_history_file = setup_logging_files("freeze_history.txt")
logger = Utils.set_up_logging(logfile, log_history_file, logging.INFO, mode="w")


def main():
    path = Path(__file__).parent
    df = pd.read_csv(path / "metadata_p_meting.csv")
    df = df.set_index("locationId", drop=True)
    df = df.drop(columns=["Unnamed: 0"])
    df["firstValueTime"] = pd.to_datetime(df["firstValueTime"])

    years = 1
    max_itter = 50
    for _, row in df.iterrows():
        logger.info(f'starting {row.name} ')
        endpoint = "timeseries?"
        start_time_dt = row.firstValueTime
        itter = 0
        while itter < max_itter :
            # set next itter start and end time
            end_time_dt = start_time_dt + pd.DateOffset(years=years)
            start_time = start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = end_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            start_time_dt += pd.DateOffset(years=years)
            itter += 1
            if start_time_dt >= pd.Timestamp.now():
                if start_time_dt == pd.Timestamp.now():
                    continue
                else:
                    start_time = (start_time_dt - pd.DateOffset(years=years)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    end_time = pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                    start_time_dt = pd.Timestamp.now()
            # skip is already exists to save time. 
            output_file = output_folder / f"{row.name}_{start_time.split('T')[0]}_{end_time.split('T')[0]}.xml"
            if output_file.exists():
                continue
            params = dict(
                moduleInstanceIds="Bewerk_KETEN",
                locationIds=row.name,
                parameterIds="P.meting",
                # startTime=row.firstValueTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                startTime=start_time,
                endTime=end_time,
                onlyHeaders="false",
                showStatistics="false",
                documentFormat="PI_XML",
            )
            logger.debug('starting retrieval')
            res = requests.get(base_url + endpoint, params=params)
            if res.status_code == 200:
                root = ET.fromstring(res.text)
            else:
                logger.error(res.text)
                raise UserWarning('failed to retrieve data')
            logger.debug('finished retrieval')
            # Namespace-safe zoeken naar events
            if root.tag.startswith("{"):
                ns = {"pi": root.tag.split("}")[0].strip("{")}
                events = root.findall(".//pi:event", ns)
            else:
                events = root.findall(".//event")
            # 'flag': '0'
            set_value = {
                "valueSource": "MAN",
                "flag": "1", # moet 1 zijn
                "user": "...",
            }
            for event in events:
                event.attrib.update(set_value)
            # Zorg dat ElementTree de FEWS namespaces netjes uitschrijft
            ET.register_namespace("", "http://www.wldelft.nl/fews/PI")
            ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
            ET.register_namespace("fs", "http://www.wldelft.nl/fews/fs")

            updated_xml_text = ET.tostring(root, encoding="utf-8").decode(
                "utf-8"
            )
            updated_xml_text = "<?xml version='1.0' encoding='utf-8'?>\n"+ updated_xml_text
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(updated_xml_text)

            # the loging for writiing it too verbose, so set to warning
            logger.info(
                f"{row.name}: {res.status_code}: {start_time.split('T')[0]} - {end_time.split('T')[0]}"
            )

if __name__ == "__main__":
    main()

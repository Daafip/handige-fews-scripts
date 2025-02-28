"""
The names of the files changed...
For the initialisation period of the transderfucntion (1990-2018) they muste be named like this:
evaporation_YYYYMMDDHHMMSS.asc
After (i.e. the running of the model) they must be named like this:
evaporation_YYYYMMDDHHMM.asc
This script renames and moves zipped meteo files correctly for the Digiflow model to use
D.B. Haasnoot, HKV dec 2024
"""

from pathlib import Path
import sys
from datetime import datetime
from fewslogger import logger

if len(sys.argv) > 1:
    directory_str = sys.argv[1]

    try:
        directory = Path(directory_str)
        output_path = Path(directory_str)
        for years in directory.iterdir():
            for months in years.iterdir():
                files = list(months.glob("*.asc"))
                for index, file in enumerate(files):
                    output_folder = file.parent
                    file_name = file.name
                    if file_name.startswith("evaporation_"):
                        file_name_parts = file_name.split("_")
                        date_str = file_name_parts[1].split(".")[0][:8]
                        dt = datetime.fromisoformat(date_str)
                        new_file_name = f"evaporation_{dt.year}{dt.month:02d}{dt.day:02d}{dt.hour:02d}{dt.minute:02d}{dt.second:02d}.asc"
                        if int(dt.year) > 2018:
                            new_file_name = f"evaporation_{dt.year}{dt.month:02d}{dt.day:02d}{dt.hour:02d}{dt.minute:02d}.asc"
                        if new_file_name != file_name:
                            new_file = output_folder / new_file_name
                            # overwrite file if exists
                            if new_file.exists():
                                new_file.unlink()
                            file.rename(new_file)

                    elif file_name.startswith("NSL_"):
                        file_name_parts = file_name.split("_")
                        date_str = file_name_parts[1].split(".")[0][:8]
                        hours = file_name_parts[2].split(".")[0]
                        date_time = f"{date_str}T{hours}:00"
                        dt = datetime.fromisoformat(date_time)
                        new_file_name = f"precipitation_{dt.year}{dt.month:02d}{dt.day:02d}{dt.hour:02d}{dt.minute:02d}{dt.second:02d}.asc"
                        if int(dt.year) > 2018:
                            new_file_name = f"precipitation_{dt.year}{dt.month:02d}{dt.day:02d}{dt.hour:02d}{dt.minute:02d}.asc"
                        if new_file_name != file_name:
                            new_file = output_folder / new_file_name
                            # overwrite file if exists
                            if new_file.exists():
                                new_file.unlink()
                            file.rename(new_file)

                    else:
                        pass

    except Exception as e:
        logger.warning(f"Problem parsing settings: {e}")


else:
    logger.warning("Missing arguments")

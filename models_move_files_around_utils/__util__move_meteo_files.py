"""
In the model update in dec the digiflow model wants meteo files per year, per month.
This script renames and moves zipped meteo files correctly for the Digiflow model to use
D.B. Haasnoot, HKV dec 2024
"""

from pathlib import Path
import sys
from datetime import datetime
from fewslogger import logger
import os

if len(sys.argv) > 1:
    directory_str = sys.argv[1]

    try:
        directory = Path(directory_str)
        output_path = Path(directory_str)

        files = list(directory.glob("*.asc"))
        for index, file in enumerate(files):
            file_name = file.name
            if file_name.startswith("MB_"):
                file_name_parts = file_name.split("_")
                date_str = file_name_parts[2].split(".")[0]
                dt = datetime.fromisoformat(date_str)
            if file_name.startswith("NSL_"):
                file_name_parts = file_name.split("_")
                date_str = file_name_parts[1]
                dt = datetime.fromisoformat(date_str)

            output_folder = output_path / f"{dt.year}" / f"{dt.month:02d}"
            os.makedirs(output_folder, exist_ok=True)
            new_file = output_folder / file_name
            # overwrite file if exists
            if new_file.exists():
                new_file.unlink()
            file.rename(new_file)

    except Exception as e:
        logger.warning(f"Problem parsing settings: {e}")


else:
    logger.warning("Missing arguments")

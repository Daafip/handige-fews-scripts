"""
This scripts moves stored results back into the results folder temporarily for import
D.B. Haasnoot, HKV dec 2024
"""

from pathlib import Path
import shutil
import sys
from fewslogger import logger

if len(sys.argv) > 1:
    directory_str = sys.argv[1]
    output_path_str = sys.argv[2]

    try:
        directory = Path(directory_str)
        output_path = Path(output_path_str)

        files = list(directory.glob("Init_*"))
        for index, file in enumerate(files):
            subfolder = file / "BASIS1_TA-MF6-UNCONF-TF-HIST"
            logger.info(f"{subfolder}")
            state_files = list(subfolder.glob("*.IDF"))
            for state_file in state_files:
                shutil.copy(state_file, output_path / state_file.name)
                
    except Exception as e:
        logger.warning(f"Problem parsing settings: {e}")


else:
    logger.warning("Missing arguments")
"""
To Run:
"F:\Digiflow\Digiflow50_v2\deltaforge\python.exe" "__util__move_saved_states_import.py"  "F:\Digiflow\Digiflow50_v2\RUNFILES\BASIS1\BASIS1_TA-MF6-UNCONF-TF-HIST\TF_Output" "F:\Digiflow\Digiflow50_v2\RESULTS\BASIS1\TA-MF6-UNCONF-TF-HIST\GWF_1\MODELOUTPUT\HEAD\HEAD"
"""
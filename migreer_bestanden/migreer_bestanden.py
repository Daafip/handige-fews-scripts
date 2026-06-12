"""D.Haasnoot @ hkv.nl 09-04-2025
Maak kopieën van bestanden van de bron naar de doelmap
voor migratie van bestanden naar nieuwe locatie op netwerk van de dommel
"""

from pathlib import Path
import logging
from Utils import Utils
import sys
import shutil

def setup_logging_files(fname):
    file_path = Path(__file__)
    logfile_dir = file_path.parent / 'logs'
    logfile_dir.mkdir(exist_ok=True)
    logfile = logfile_dir / fname
    log_history_file_dir = logfile_dir / 'old_logs'
    log_history_file_dir.mkdir(exist_ok=True)
    log_history_file = log_history_file_dir/ fname

    return logfile, log_history_file

def delete_files_in_directory(from_path, to_path):
    to_files = [file.name for file in to_path.glob('*')]
    from_files = [file.name for file in from_path.glob('*')]
    dict_map_to_files = {file.name: file for file in to_path}

    files_to_delete = set(to_files).difference(from_files)
    for file in files_to_delete:
        if file in dict_map_to_files:
            dict_map_to_files[file].unlink()
        else:
            logger.warning(f"Skipping {file.name}, no file found in the target directory")

def move_files(from_dir, to_dir):
    from_path, to_path = Path(from_dir), Path(to_dir)

    #  kopieer bestanden van de bron naar de doelmap
    files = list(from_path.glob('*'))
    to_files = [file.name for file in to_path.glob('*')]
    dict_map_to_files = {file.name: file for file in to_path.glob('*')}
    
    for file in files:
        if file.is_file():
            # copy if not exists 
            if file.name not in to_files:
                shutil.copy(file, to_path / file.name)
            # copy if exists and is older
            elif file.stat().st_mtime > dict_map_to_files[file.name].stat().st_mtime:
                shutil.copy(file, to_path / file.name)
        else:
            sub_to_path = file.as_posix().replace(from_dir, to_dir)
            Path(sub_to_path).mkdir(exist_ok=True)
            # verwijder bestanden in de doel map die niet in de bron map staan
            delete_files_in_directory(sub_to_path, from_path)
            # verplaats bestaande files van bron naar doel
            move_files(file.as_posix(), to_path)


if __name__ == "__main__":
    file_path = Path(__file__)
    logfile, log_history_file = setup_logging_files('migreer_bestanden.txt')
    logger = Utils.set_up_logging(logfile, log_history_file, logging.INFO, mode='w')
    
    if len(sys.argv) > 1:
        try:
            from_dir = sys.argv[1]
            to_dir = sys.argv[2]
            try:
                logger.info(f" {file_path.name} - starting")
                move_files(from_dir, to_dir)
                logger.info(f" {file_path.name} - Completed")
            except Exception as e:
                logger.warning(f" {file_path.name} - Problem processing data: {e}")
        except Exception as e:
            logger.warning(f" {file_path.name} - Problem passing arguments: {e}: {sys.argv}")
    else:
        logger.warning(f" {file_path.name} - Missing arguments")
from typing import List
from pathlib import Path
import glob

def case_insensitive_glob(filepath: str, fileextension: str) -> List[Path]:
    """Find files in given path with given file extension (case insensitive)

    Arguments:
        filepath (str): path to files
        fileextension (str): file extension to use as a filter (example .gef or .csv)

    Returns:
        List(str): list of files
    """
    p = Path(filepath)
    result = []
    for filename in p.glob('**/*'):
        if str(filename.suffix).lower() == fileextension.lower():
            result.append(filename.absolute())
    return result

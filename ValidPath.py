from pathlib import Path
import tempfile
from typing import Iterable, Sequence, Optional, NoReturn
'''
This module is used to check that user input path names are valid.
The function check_valid_paths performs all of the checks. The rest
of the functions are helper functions that perform single checks.
'''


def verify_num_paths(paths_to_refactor: Sequence[Path], new_paths: Sequence[Path]) -> Optional[NoReturn]:
    """
    Checks: that the user did not delete or add any lines while in the vim session.
      - Verifies that the number of filenames passed in, is the same as the number of file
        names that were returned from the vim session.

    :param paths_to_refactor: paths that existed prior to being edited
    :param new_paths: refactored paths
    """

    if len(paths_to_refactor) != len(new_paths):
        raise Exception("You cannot remove lines during a refactoring session.")


def verify_no_duplicates(dir: Path, paths_to_refactor, new_paths) -> Optional[NoReturn]:
    """
    Verify there aren't any duplicate paths.
     - checks for duplicate entries in new_paths
     - checks for files in new_path that already exist in the directory

     :param dir: directory whose contents are being refactored
     :param paths_to_refactor: paths that have been staged to be refactored
     :param new_paths: new path names to use for refactoring
    """
    if len(set(new_paths)) != len(new_paths) or len(
            set(dir.iterdir()) - set(paths_to_refactor) &
            set(new_paths)
            ) != 0:

        raise Exception("You cannot create duplicate paths.")


def verify_valid_names(new_paths: Iterable[Path]) -> Optional[NoReturn]:
    """
    Verify file names are valid.
     - Create every file name in a temporary directory
       and throws an error if a file name could not be created.

    :param new_paths: refactored path names

    :return None: if the new path names are valid
    """
    temp_dir = tempfile.mkdtemp()
    path_temp_dir = Path(temp_dir)
    try:

        for np in new_paths:

            temp_path = path_temp_dir / np.name
            temp_path.touch()
            temp_path.unlink()

    except Exception as e:

        path_temp_dir.rmdir()
        raise Exception("Valid file names were not used.\n" + str(e))

    path_temp_dir.rmdir()


def check_valid_paths(direc: Path, paths_to_refactor: Iterable[Path], new_paths: Iterable[Path]) -> bool:
    """
    This function is used to verify that new_paths contains valid file names that can
    be used to refactor the file names in paths_to_refactor.

    :param direc: directory whose contents will be refactored
    :param paths_to_refactor: paths in direc whose contents will be refactored
    :param new_paths: new path names that will be used to refactor contents of paths_to_refactor

    :return: indicates whether new_paths are valid
    """

    try:

        # verifies the proper number of paths_to_refactor is contained in new_paths
        verify_num_paths(paths_to_refactor, new_paths)

        # verifies no duplicate paths will be created
        verify_no_duplicates(direc, paths_to_refactor, new_paths)

        # verifies new_path contains valid file names
        verify_valid_names(new_paths)

    except Exception as e:
        print(f"* Exception found when modifying directory: {direc}")
        print("* Files were not refactored.")
        print(e, end="\n\n")
        return False

    return True

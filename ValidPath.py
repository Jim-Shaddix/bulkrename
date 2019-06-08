from pathlib import Path
import tempfile
'''
This module is used to check that user input path names are valid.
The function check_valid_paths performs all of the checks. The rest
of the functions are helper functions that perform single checks.

* more information on checking for proper paths:
https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
'''


def verify_num_paths(paths, new_paths):
    """
        Verify that lines were not deleted or added during one of the vim refactoring sessions.
    """

    if len(paths) != len(new_paths):
        raise Exception("You cannot remove lines during a refactoring session.")


def verify_no_duplicates(dir, paths, new_paths):
    """
    Verify there aren't any duplicate paths.
     - checks for duplicate entries in new_paths
     - checks for files in new_path that already exist in the directory
    """
    if len(set(new_paths)) != len(new_paths) or len(
            set(dir.iterdir()) - set(paths) &
            set(new_paths)
            ) != 0:

        raise Exception("You cannot create duplicate paths.")


def verify_valid_names(paths, new_paths):
    """
    Verify file names are valid.
    - Create every file name in a temporary directory
      and throws an error if a file name could not be created.
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


def check_valid_paths(direc, paths, new_paths):
    """
    This function is used to verify that new_paths contains valid file names that can
    be used to refactor the file names in paths.

    :param direc: (Path) whose contents will be refacotred
    :param paths: (list(Path)) paths in direc whose contents will be refactored
    :param new_paths: list(Path) new path names that will be used to refactor contents of paths
    :return:
    """

    try:

        # verifies the proper number of paths is contained in new_paths
        verify_num_paths(paths, new_paths)

        # verifies no duplicate paths will be created
        verify_no_duplicates(direc, paths, new_paths)

        # verifies new_path contains valid file names
        verify_valid_names(paths, new_paths)

    except Exception as e:
        print(f"* Exception found when modifying directory: {direc}")
        print("* Files were not refactored.")
        print(e, end="\n\n")
        return False

    return True

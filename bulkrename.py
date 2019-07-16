import click
import sys
from pathlib import Path
from ValidPath import check_valid_paths
from typing import Iterable, List, NoReturn, Optional, Callable
"""
    This is a program for refactoring filenames using a text editor (such as vim)
    - for a description on how to use this program, you can look in the docs in
      the cli function, or run this program with the --help flag. 
    - The cli function is the entry point into the script.
"""


def check_provided_path_valid(dir_path: Path) -> Optional[NoReturn]:
    """
        checks whether the program was run with an
        appropriate path argument.

        :param dir_path: [Path] to check
        :return None
    """
    try:

        # CHECK: Exists
        if not dir_path.exists():
            raise Exception("The path provided does not exist ... ")

        # CHECK: Is directory
        if not dir_path.is_dir():
            raise Exception("The path specified was not a directory.")

    except Exception as e:
        print(e)
        sys.exit(1)


def refactor_checker(file_path: Path, file_flag: bool, dot_file_flag: bool,
                     dir_flag: bool, dot_dir_flag: bool) -> bool:
    """
    Determines whether or not a file should be refactored

    :param file_path:     [Path] file to be checked.
    :param file_flag:     [bool] whether to refactor files
    :param dot_file_flag: [bool] whether to refactor dot files
    :param dir_flag:      [bool] whether to refactor directories
    :param dot_dir_flag:  [bool] whether to refactor dot directories

    :return: [bool] indicates whether file_path should be refactored
    """

    # alias
    p = file_path

    # if a flag is set, and file_path is associated with
    # the flag, the file_path is scheduled to be refactored.
    if file_flag and p.is_file() and str(p.name)[0] != ".":
        return True

    if dot_file_flag and p.is_file() and str(p.name)[0] == ".":
        return True

    if dir_flag     and p.is_dir()  and str(p.name)[0] != ".":
        return True

    if dot_dir_flag and p.is_dir()  and str(p.name)[0] == ".":
        return True

    # none of the checks were passed
    return False


def recurse_checker(file_path: Path, recursive_flag: bool, recursive_dot_flag: bool) -> bool:
    """
    :param file_path: file to be checked.
    :param recursive_flag: whether to recursively refactor directories.
    :param recursive_dot_flag: whether to recursively refactor dot directories.
    :return: bool, that determines whether or not a path should be recursed upon.
    """

    # alias
    p = file_path

    # if a flag is set, and file_path is associated with
    # the flag, the file_path is scheduled to be recursed upon.
    if recursive_flag     and p.is_dir() and p.name[0] != '.': return True
    if recursive_dot_flag and p.is_dir() and p.name[0] == '.': return True

    # None of the checks were passed
    return False


def print_verbose(dir_path: Path, paths_to_refactor: Iterable[Path],
                  refactored_paths: Optional[Iterable[Path]]) -> None:
    """
    :param dir_path: Directory path whose contents will be refactored
    :param paths_to_refactor: paths that will be refactored
    :param refactored_paths: refactored paths

    :return: None
    """

    print(f"Directory: {dir_path}")

    # Check: editor was closed properly
    if refactored_paths is None:

        print("No paths were refactored")

    else:

        # Get: file names from paths
        names = [p.name for p in paths_to_refactor]
        refactored_names = [p.name for p in refactored_paths]

        # Get: maximum file name length
        max_len = max(len(p) for p in names)

        # Display: name -> refactored_name
        for n, rn in zip(names, refactored_names):
            print(f"{n:>{max_len}} -> {rn}")

    print()


def refactor(current_dir: Path, paths_to_refactor: Iterable[Path]) -> List[Path]:
    """
    * refactors all of the provided paths.
    * checks that the refactored paths are valid.
        - prompts the user to try again or quit the program if the
          paths were not refactored appropriately, or the editor was
          closed before saving.

    :param current_dir: [Path] to the current directory
    :param paths_to_refactor: [List(Path)] to refactor

    :return: list(Path) with refactored names.
             - or None, if the editor was not closed properly
    """

    # GET: new file names
    # - new_names_str will be equal to None, if the editor is closed
    #   before saving the file.
    names_list = [f.name for f in paths_to_refactor]
    new_names_str = click.edit(f"Directory: {str(current_dir)}\n" +
                               "\n".join(names_list))

    # CHECK: if editor was saved
    if new_names_str is not None:

        # GET: list of names to perform refactoring on.
        # - ignores the first line in the file that contains
        #   the directories name.
        new_names_list = new_names_str.split("\n")[1:]

        # GET: new paths
        refactored_paths = [ptr.parent / nnl for ptr, nnl in
                                zip(paths_to_refactor, new_names_list)]

        # CHECK: to see if the new paths are valid
        valid = check_valid_paths(current_dir,
                                  paths_to_refactor,
                                  refactored_paths)

    # Prompt user when:
    # 1. Valid file names were not provided
    # 2. The editor was not saved
    if new_names_str is None or not valid:

        given = "default"
        while given not in "rcx":
            given = click.prompt("[Retry|Continue|Exit]? [r|c|x]")
            print()

        if given == "r":
            return refactor(current_dir, paths_to_refactor)

        elif given == "x":
            click.echo(click.style(f'Aborted Refactoring: {current_dir}', fg='red'))
            sys.exit(0)

        else:
            return

    return refactored_paths


def refactor_recursive(current_dir: Path, refactor_check: Callable[[Path], bool],
                       recurse_check: Callable[[Path], bool], verbose: bool, dry_run: bool) -> None:
    """
    recursively refactors files starting from the directory passed in.

    :param current_dir: directory to refactor
    :param refactor_check: whether to refactor a path.
    :param recurse_check:  whether to recurse upon a path.
    :param verbose:  prints refactorings that take place.
    :param dry_run:  whether or not to perform refactorings.
    :return: None
    """

    # Get: paths to refactor
    paths_to_refactor = [p for p in current_dir.iterdir() if refactor_check(p)]

    # refactor paths
    # - if None is returned, that is an indication that the editor session
    #   was not saved, and nothing needs to be refactored in this directory.
    refactored_paths = refactor(current_dir, paths_to_refactor)

    # print (original_file -> new_file)
    if verbose or dry_run:
        print_verbose(current_dir, paths_to_refactor, refactored_paths)

    if refactored_paths is not None:

        # refactor paths
        if not dry_run:
            for path, rpath in zip(paths_to_refactor, refactored_paths):
                path.replace(rpath)

    # list of valid directories
    new_directories = (d for d in current_dir.iterdir() if recurse_check(d))

    # recursively refactor upon each of the valid directories.
    for d in new_directories:
        refactor_recursive(d, refactor_check, recurse_check, verbose, dry_run)


@click.command()
@click.argument("path", default=".", required=False)
@click.option("-f", "--files", "file_flag",
              default=True,  is_flag=True,
              help="[Default = True]  refactor files.")
@click.option("-dotf", "--dot-files", "dot_file_flag",
              default=False, is_flag=True,
              help="refactor dot files.")
@click.option("-d", "--directories", "dir_flag",
              default=False, is_flag=True,
              help="refactor directories.")
@click.option("-dotd", "--dot-direc", "dot_dir_flag",
              default=False, is_flag=True,
              help="refactor dot directories.")
@click.option("-r", "--recursive", "recursive_flag",
              default=False, is_flag=True,
              help="recursively refactor through directories.")
@click.option("-dotr", "--recursive-dot", "recursive_dot_flag",
              default=False, is_flag=True,
              help="recursively refactor through dot directories.")
@click.option("-v", "--verbose",
              default=False, is_flag=True,
              help="Display what each relative file path was changed to.")
@click.option("-dr", "--dry-run",
              default=False, is_flag=True,
              help="Display what each file path will be changed to, without performing the changes.")
def cli(path, file_flag, dot_file_flag, dir_flag, dot_dir_flag, recursive_flag, recursive_dot_flag, verbose, dry_run):
    """
    Refactors all of file names in the provided directory. By default,
    refactoring is done on the current directory, and is only done on non-dot files.
    """

    # path to start search from
    dir_path = Path(path)

    # Check: provided path is valid
    check_provided_path_valid(dir_path)

    # Closure Function, that indicates whether or not a path should be refactored
    refactor_check = lambda f: refactor_checker(f, file_flag, dot_file_flag, dir_flag, dot_dir_flag)

    # Closure Function, that indicates whether or not a directory should be recursed upon.
    recurse_check = lambda f: recurse_checker(f, recursive_flag, recursive_dot_flag)

    # refactor files recursively in dir_path
    refactor_recursive(dir_path, refactor_check, recurse_check, verbose, dry_run)


if __name__ == '__main__':
    cli()

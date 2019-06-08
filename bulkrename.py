import click
import sys
from pathlib import Path
from ValidPath import check_valid_paths
"""
    This is a program for refactoring filenames useing a text editor (i.e vim)
    - for a description on how to use this program, you can look in the docs in
      the cli function, or run this program with the --help flag
"""


def check_provided_path_valid(dir_path):
    """
        checks whether or not the program was run with an
        appropriate path argument.
    """
    try:

        # CHECK: Exists
        if not dir_path.exists():
            raise Exception("The path provided does not exist ... ")

        # CHECK: Is directory
        if not dir_path.is_dir():
            raise Exception("This path specified was not a directory.")

    except Exception as e:
        print(e)
        sys.exit(1)


def get_refactor_checker(file_flag, dot_file_flag, dir_flag, dot_dir_flag):
    """
    :param file_flag:     [boolean] determines whether or not to refactor files
    :param dot_file_flag: [boolean] determines whether or not to refactor dot files
    :param dir_flag:      [boolean] determines whether or not to refactor directories
    :param dot_dir_flag:  [boolean] determines whether or not to refactor dot directories

    :return: a function that takes a path as an argument, and that returns a boolean that
             indicates whether or not the path should be refactored
    """
    checks = []
    if file_flag:     checks.append(lambda x: x.is_file() and str(x.name)[0] != ".")
    if dot_file_flag: checks.append(lambda x: x.is_file() and str(x.name)[0] == ".")
    if dir_flag:      checks.append(lambda x: x.is_dir()  and str(x.name)[0] != ".")
    if dot_dir_flag:  checks.append(lambda x: x.is_dir()  and str(x.name)[0] == ".")
    return lambda file_path: any([f(file_path) for f in checks])


def get_recurse_checker(recursive_flag, recursive_dot_flag):
    """
    :param recursive_flag: determines whether or not I should recursively refactor directories.
    :param recursive_dot_flag: determines whether or not I should recursively refactor dot directories.
    :return: function, that determines whether or not a path should be recursed upon.
    """

    # create
    checks = []
    if recursive_flag:     checks.append(lambda p: p.is_dir() and p.name[0] != '.')
    if recursive_dot_flag: checks.append(lambda p: p.is_dir() and p.name[0] == '.')
    return lambda direc: any([c(direc) for c in checks])


def print_verbose(dir_path, paths_to_refactor, refactored_paths):
    """
    :param dir_path: Directory path whose contents will be refactored
    :param paths_to_refactor: paths that will be refactored
    :param refactored_paths: refactored paths

    :return: None
    """

    print(f"Directory: {dir_path}")

    names = [p.name for p in paths_to_refactor]
    refactored_names = [p.name for p in refactored_paths]

    max_len = max(len(p) for p in names)

    for n, rn in zip(names, refactored_names):
        print(f"{n:>{max_len}} -> {rn}")

    print()


def refactor(current_dir, paths_to_refactor):
    """
    * refactors all of the provided paths.
    * checks that the refactored paths are valid.
        - prompts the user to try again or quit the program if the
          paths were not refactored appropriately.

    :param current_dir: [Path] to the current directory
    :param paths_to_refactor: [List(Path)] to refactor

    :return: list(Path) with refactored names.
    """

    # GET: new file names
    names_list = [f.name for f in paths_to_refactor]
    new_names_str = click.edit(f"Directory: {str(current_dir)}\n" +
                               "\n".join(names_list))

    # CHECK: if editor was closed improperly
    if new_names_str is None:
        return

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

    if not valid:

        # prompt to continue you or exit.
        if click.confirm('Would you like try renaming files from this directory again?', abort=True):
            refactor(current_dir, paths_to_refactor)
        else:
            click.confirm('Do you want to continue?', abort=True)

    return refactored_paths


def refactor_recursive(current_dir, refactor_check, recurse_check, verbose, dry_run):
    """
    recursively refactors files starting from the directory passed in.

    :param current_dir: (Path) directory to refactor
    :param refactor_check: (Func(Path) -> boolean) whether to refactor a path.
    :param recurse_check:  (Func(Path) -> boolean) whether to recurse upon a path.
    :param verbose: (bool) prints refactorings that take place.
    :param dry_run: (bool) whether or not to perform refactorings.
    :return: None
    """

    # Get: paths to refactor
    paths_to_refactor = [p for p in current_dir.iterdir() if refactor_check(p)]

    # refactor paths
    # - if None is returned, that is an indication that the editor session
    #   was not saved, and nothing needs to be refactored in this directory.
    refactored_paths = refactor(current_dir, paths_to_refactor)

    if refactored_paths is not None:

        # print (original_file -> new_file)
        if verbose or dry_run:
            print_verbose(current_dir, paths_to_refactor, refactored_paths)

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
@click.option("-f", "--files", "file_flag", default=True,  is_flag=True,
              help="[Default = True]  refactor files.")
@click.option("-dotf", "--dot-files", "dot_file_flag", default=False, is_flag=True,
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

    # Function, that indicates whether or not a path should be refactored
    refactor_check = get_refactor_checker(file_flag, dot_file_flag, dir_flag, dot_dir_flag)

    # Function, that indicates whether or not a directory should be recursed upon.
    recurse_check = get_recurse_checker(recursive_flag, recursive_dot_flag)

    # reactor files recursively in dir_path
    refactor_recursive(dir_path, refactor_check, recurse_check, verbose, dry_run)


if __name__ == '__main__':
    cli()

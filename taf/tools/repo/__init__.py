import click
import json
import taf.developer_tool as developer_tool
from taf.constants import DEFAULT_RSA_SIGNATURE_SCHEME
from taf.updater.updater import update_repository, validate_repository, UpdateType


def attach_to_group(group):

    @group.group()
    def repo():
        pass

    @repo.command()
    @click.argument("path")
    @click.option("--keys-description", help="A dictionary containing information about the "
                  "keys or a path to a json file which stores the needed information")
    @click.option("--keystore", default=None, help="Location of the keystore files")
    @click.option("--commit", is_flag=True, default=False, help="Indicates if the changes should be "
                  "committed automatically")
    @click.option("--test", is_flag=True, default=False, help="Indicates if the created repository "
                  "is a test authentication repository")
    def create(path, keys_description, keystore, commit, test):
        """
        \b
        Create a new authentication repository at the specified location by registering
        signing keys and generating initial metadata files. Information about the roles
        can be provided through a dictionary - either specified directly or contained
        by a .json file whose path is specified when calling this command. This allows
        definition of:
            - total number of keys per role
            - threshold of signatures per role
            - should keys of a role be on Yubikeys or should keystore files be used
            - scheme (the default scheme is rsa-pkcs1v15-sha256)
            - keystore path, if not specified via keystore option

        \b
        For example:
        {
            "roles": {
                "root": {
                    "number": 3,
                    "length": 2048,
                    "passwords": ["password1", "password2", "password3"],
                    "threshold": 2,
                    "yubikey": true
                },
                "targets": {
                    "length": 2048
                },
                "snapshot": {},
                "timestamp": {}
            },
            "keystore": "keystore_path"
        }

        In cases when this dictionary is not specified, it is necessary to enter the needed
        information when asked to do so, or confirm that default values should be used.
        If keys should be stored in keystore files, it is possible to either use already generated
        keys (stored in keystore files located at the path specified using the keystore option),
        or to generate new one.

        If the test flag is set, a special target file will be created. This means that when
        calling the updater, it'll be necessary to use the --authenticate-test-repo flag.
        """
        developer_tool.create_repository(path, keystore, keys_description, commit, test)

    @repo.command()
    @click.argument("path")
    @click.option("--library-dir", default=None, help="Directory where target repositories and, "
                  "optionally, authentication repository are located. If omitted it is "
                  "calculated based on authentication repository's path. "
                  "Authentication repo is presumed to be at library-dir/namespace/auth-repo-name")
    @click.option("--namespace", default=None, help="Namespace of the target repositories. "
                  "If omitted, it will be assumed that namespace matches the name of the "
                  "directory which contains the authentication repository")
    @click.option("--targets-rel-dir", default=None, help="Directory relative to which "
                  "urls of the target repositories are calculated. Only useful when "
                  "the target repositories do not have remotes set")
    @click.option("--custom", default=None, help="A dictionary containing custom "
                  "targets info which will be added to repositories.json")
    @click.option("--use-mirrors", is_flag=True, help="Whether to generate mirrors.json or not")
    def generate_repositories_json(path, library_dir, namespace, targets_rel_dir, custom, use_mirrors):
        """
        Generate repositories.json. This file needs to be one of the authentication repository's
        target files or the updater won't be able to validate target repositories.
        repositories.json is generated by traversing through all targets and adding an entry
        with the namespace prefixed name of the target repository as its key and the
        repository's url and custom data as its value.

        Target repositories are expected to be inside a directory whose name is equal to the specified
        namespace and which is located inside the root directory. If root directory is E:\\examples\\root
        and namespace is namespace1, target repositories should be in E:\\examples\\root\\namespace1.
        If the authentication repository and the target repositories are in the same root directory and
        the authentication repository is also directly inside a namespace directory, then the common root
        directory is calculated as two repositories up from the authentication repository's directory.
        Authentication repository's namespace can, but does not have to be equal to the namespace of target,
        repositories. If the authentication repository's path is E:\\root\\namespace\\auth-repo, root
        directory will be determined as E:\\root. If this default value is not correct, it can be redefined
        through the --library-dir option. If the --namespace option's value is not provided, it is assumed
        that the namespace of target repositories is equal to the authentication repository's namespace,
        determined based on the repository's path. E.g. Namespace of E:\\root\\namespace2\\auth-repo
        is namespace2.

        The url of a repository corresponds to its git remote url if set and to its location on the file
        system otherwise. Test repositories might not have remotes. If targets-rel-dir is specified
        and a repository does not have remote url, its url is calculated as a relative path to the
        repository's location from this path. There are two options of defining urls:
        1. Directly specifying all urls of all repositories directly inside repositories.json
        2. Using a separate mirrors.json file. This file will be generated only if use-mirrors flag is provided.
        The mirrors file consists of a list of templates which contain namespace (org name) and repo name as arguments.
        E.g. "https://github.com/{org_name}/{repo_name}.git". If a target repository's namespaced name
        is namespace1/target_repo1, its url will be calculated by replacing {org_name} with namespace1
        and {repo_name} with target_repo1 and would result in "https://github.com/namespace1/target_repo1.git"

        While urls are the only information that the updater needs, it is possible to add
        any other data using the custom option. Custom data can either be specified in a .json file
        whose path is provided when calling this command, or directly entered. Keys is this
        dictionary are names of the repositories whose custom data should be set and values are
        custom data dictionaries. For example:

        \b
        {
            "test/html-repo": {
                "type": "html"
            },
            "test/xml-repo": {
                "type": "xml"
            }
        }

        Note: this command does not automatically register repositories.json as a target file.
        It is recommended that the content of the file is reviewed before doing so manually.
        """
        developer_tool.generate_repositories_json(
            path, library_dir, namespace, targets_rel_dir, custom, use_mirrors
        )

    @repo.command()
    @click.argument("path")
    @click.option("--library-dir", default=None, help="Directory where target repositories and, "
                  "optionally, authentication repository are located. If omitted it is "
                  "calculated based on authentication repository's path. "
                  "Authentication repo is presumed to be at library-dir/namespace/auth-repo-name")
    @click.option("--namespace", default=None, help="Namespace of the target repositories. "
                  "If omitted, it will be assumed that namespace matches the name of the "
                  "directory which contains the authentication repository")
    @click.option("--targets-rel-dir", default=None, help="Directory relative to which "
                  "urls of the target repositories are calculated. Only useful when "
                  "the target repositories do not have remotes set")
    @click.option("--custom", default=None, help="A dictionary containing custom "
                  "targets info which will be added to repositories.json")
    @click.option("--use-mirrors", is_flag=True, help="Whether to generate mirrors.json or not")
    @click.option("--add-branch", default=False, is_flag=True, help="Whether to add name of "
                  "the current branch to target files")
    @click.option("--keystore", default=None, help="Location of the keystore files")
    @click.option("--keys-description", help="A dictionary containing information about the "
                  "keys or a path to a json file which stores the needed information")
    @click.option("--commit", is_flag=True, help="Indicates if the changes should be "
                  "committed automatically")
    @click.option("--test", is_flag=True, default=False, help="Indicates if the created repository "
                  "is a test authentication repository")
    @click.option("--scheme", default=DEFAULT_RSA_SIGNATURE_SCHEME, help="A signature scheme used for signing.")
    def initialize(path, library_dir, namespace, targets_rel_dir, custom, use_mirrors, add_branch, keystore,
                   keys_description, commit, test, scheme):
        """
        \b
        Create and initialize a new authentication repository:
            1. Create an authentication repository (generate initial metadata files)
            2. Commit initial metadata files if commit == True
            3. Add target files corresponding to target repositories
            4. Generate repositories.json
            5. Update metadata files
            6. Commit the changes if commit == True
        Combines create, generate_repositories_json, update_repos and targets sign commands.
        In order to have greater control over individual steps and be able to review files created
        in the initialization process, execute the mentioned commands separately.
        """
        developer_tool.init_repo(path, library_dir, namespace, targets_rel_dir, custom, use_mirrors,
                                 add_branch, keystore, keys_description, commit, test, scheme)

    @repo.command()
    @click.argument("url")
    @click.option("--clients-auth-path", default=None, help="Directory where authentication repository is located.")
    @click.option("--clients-library-dir", default=None, help="Directory where target repositories and, "
                  "optionally, authentication repository are located. If omitted it is "
                  "calculated based on authentication repository's path. "
                  "Authentication repo is presumed to be at root-dir/namespace/auth-repo-name")
    @click.option("--default-branch", default="main", help="Name of the default branch, like mian or master")
    @click.option("--from-fs", is_flag=True, default=False, help="Indicates if the we want to clone a "
                  "repository from the filesystem")
    @click.option("--expected-repo-type", default="either", type=click.Choice(["test", "official", "either"]),
                  help="Indicates expected authentication repository type - test or official. If type is set to either, "
                  "the updater will not check the repository's type")
    @click.option("--scripts-root-dir", default=None, help="Scripts root directory, which can be used to move scripts "
                  "out of the authentication repository for testing purposes (avoid dirty index). Scripts will be expected "
                  "to be located in scripts_root_dir/repo_name directory")
    @click.option("--profile", is_flag=True, help="Flag used to run profiler and generate .prof file")
    @click.option('--format-output', is_flag=True, help='Return formatted output which includes information '
                  'on if build was successful and error message if it was raised')
    def update(url, clients_auth_path, clients_library_dir, default_branch, from_fs, expected_repo_type, scripts_root_dir, profile, format_output):
        """
        Update and validate local authentication repository and target repositories. Remote
        authentication's repository url needs to be specified when calling this command. If the
        authentication repository and the target repositories are in the same root directory,
        locations of the target repositories are calculated based on the authentication repository's
        path. If that is not the case, it is necessary to redefine this default value using the
        --clients-library-dir option. This means that if authentication repository's path is
        E:\\root\\namespace\\auth-repo, it will be assumed that E:\\root is the root direcotry
        if clients-library-dir is not specified.
        Names of target repositories (as defined in repositories.json) are appended to the root repository's
        path thus defining the location of each target repository. If names of target repositories
        are namespace/repo1, namespace/repo2 etc and the root directory is E:\\root, path of the target
        repositories will be calculated as E:\\root\\namespace\\repo1, E:\\root\\namespace\\root2 etc.

        If remote repository's url is a file system path, it is necessary to call this command with
        --from-fs flag so that url validation is skipped. When updating a test repository (one that has
        the "test" target file), use --authenticate-test-repo flag. An error will be raised
        if this flag is omitted in the mentioned case. Do not use this flag when validating a non-test
        repository as that will also result in an error.

        Scripts root directory option can be used to move scripts out of the authentication repository for
        testing purposes (avoid dirty index). Scripts will be expected  o be located in scripts_root_dir/repo_name directory
        """
        if clients_auth_path is None and clients_library_dir is None:
            raise click.UsageError('Must specify either authentication repository path or library directory!')

        if profile:
            import cProfile
            import atexit

            print("Profiling...")
            pr = cProfile.Profile()
            pr.enable()

            def exit():
                pr.disable()
                print("Profiling completed")
                filename = 'updater.prof'  # You can change this if needed
                pr.dump_stats(filename)

            atexit.register(exit)

        try:
            update_repository(
                url,
                clients_auth_path,
                clients_library_dir,
                default_branch,
                from_fs,
                UpdateType(expected_repo_type),
                scripts_root_dir=scripts_root_dir
            )
            if format_output:
                print(json.dumps({
                    'updateSuccessful': True
                }))
        except Exception as e:
            if format_output:
                error_data = {
                    'updateSuccessful': False,
                    'error': str(e)
                }
                print(json.dumps(error_data))
            else:
                raise e

    @repo.command()
    @click.argument("clients-auth-path")
    @click.option("--clients-library-dir", default=None, help="Directory where target repositories and, "
                  "optionally, authentication repository are located. If omitted it is "
                  "calculated based on authentication repository's path. "
                  "Authentication repo is presumed to be at library-dir/namespace/auth-repo-name")
    @click.option("--default-branch", default="main", help="Name of the default branch, like mian or master")
    @click.option("--from-commit", default=None, help="First commit which should be validated.")
    def validate(clients_auth_path, clients_library_dir, default_branch, from_commit):
        """
        Validates an authentication repository which is already on the file system
        and its target repositories (which are also expected to be on the file system).
        Does not clone repositories, fetch changes or merge commits.
        """
        validate_repository(clients_auth_path, clients_library_dir, default_branch, from_commit)

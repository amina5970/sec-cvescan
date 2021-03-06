import os
import re

from cvescan.errors import ArgumentError

FMT_CSV_OPTION = "--csv"
FMT_CVE_OPTION = "-c|--cve"
FMT_EXPERIMENTAL_OPTION = "-x|--experimental"
FMT_FILE_OPTION = "-f|--file"
FMT_JSON_OPTION = "--JSON"
FMT_MANIFEST_OPTION = "-m|--manifest"
FMT_NAGIOS_OPTION = "-n|--nagios"
FMT_SHOW_LINKS_OPTION = "--show-links"
FMT_DB_FILE_OPTION = "--db"
FMT_PRIORITY_OPTION = "-p|priority"
FMT_SILENT_OPTION = "-s|--silent"
FMT_UNRESOLVED_OPTION = "--unresolved"
FMT_VERBOSE_OPTION = "-v|--verbose"

MANIFEST_URL_TEMPLATE = (
    "https://cloud-images.ubuntu.com/%s/current/%s-server-cloudimg-amd64.manifest"
)


class Options:
    def __init__(self, args):
        raise_on_invalid_args(args)

        self._set_mode(args)
        self._set_db_file_options(args)
        self._set_manifest_file_options(args)

        self.csv = args.csv
        self.cve = args.cve
        self.json = args.json
        self.priority = args.priority if args.priority else "high"
        self.unresolved = args.unresolved

        self.show_links = args.show_links

    def _set_mode(self, args):
        self.manifest_mode = True if args.manifest else False
        self.experimental_mode = args.experimental
        self.nagios_mode = args.nagios

    def _set_db_file_options(self, args):
        if args.db:
            self.download_uct_db_file = False
            self.db_file = args.db
        else:
            self.download_uct_db_file = True
            self.db_file = "uct.json"

    def _set_manifest_file_options(self, args):
        self.manifest_file = os.path.abspath(args.manifest) if args.manifest else None


def raise_on_invalid_args(args):
    raise_on_invalid_cve(args)
    raise_on_invalid_combinations(args)
    raise_on_missing_manifest_file(args)
    raise_on_missing_db_file(args)


def raise_on_invalid_cve(args):
    cve_regex = r"^CVE-[0-9]{4}-[0-9]{4,}$"
    if (args.cve is not None) and (not re.match(cve_regex, args.cve)):
        raise ValueError("Invalid CVE ID (%s)" % args.cve)


def raise_on_invalid_combinations(args):
    raise_on_invalid_nagios_options(args)
    raise_on_invalid_silent_options(args)
    raise_on_invalid_unresolved_options(args)
    raise_on_invalid_csv_options(args)
    raise_on_invalid_cve_options(args)
    raise_on_invalid_json_options(args)


def raise_on_invalid_nagios_options(args):
    if not args.nagios:
        return

    if args.cve:
        raise_incompatible_arguments_error(FMT_NAGIOS_OPTION, FMT_CVE_OPTION)

    if args.silent:
        raise_incompatible_arguments_error(FMT_NAGIOS_OPTION, FMT_SILENT_OPTION)

    if args.unresolved:
        raise_incompatible_arguments_error(FMT_NAGIOS_OPTION, FMT_UNRESOLVED_OPTION)

    if args.show_links:
        raise_incompatible_arguments_error(FMT_NAGIOS_OPTION, FMT_SHOW_LINKS_OPTION)


def raise_on_invalid_silent_options(args):
    if not args.silent:
        return

    if not args.cve:
        raise ArgumentError(
            "Cannot specify %s argument without %s."
            % (FMT_SILENT_OPTION, FMT_CVE_OPTION)
        )

    if args.verbose:
        raise_incompatible_arguments_error(FMT_SILENT_OPTION, FMT_VERBOSE_OPTION)

    if args.show_links:
        raise_incompatible_arguments_error(FMT_SILENT_OPTION, FMT_SHOW_LINKS_OPTION)


def raise_on_invalid_unresolved_options(args):
    if args.unresolved and args.cve:
        raise_incompatible_arguments_error(FMT_UNRESOLVED_OPTION, FMT_CVE_OPTION)

    if args.unresolved and args.nagios:
        raise_incompatible_arguments_error(FMT_UNRESOLVED_OPTION, FMT_NAGIOS_OPTION)


def raise_on_invalid_csv_options(args):
    if not args.csv:
        return

    if args.silent:
        raise_incompatible_arguments_error(FMT_CSV_OPTION, FMT_SILENT_OPTION)

    if args.cve:
        raise_incompatible_arguments_error(FMT_CSV_OPTION, FMT_CVE_OPTION)

    if args.json:
        raise_incompatible_arguments_error(FMT_CSV_OPTION, FMT_JSON_OPTION)

    if args.nagios:
        raise_incompatible_arguments_error(FMT_CSV_OPTION, FMT_NAGIOS_OPTION)


def raise_on_invalid_cve_options(args):
    if not args.cve:
        return

    if args.json:
        raise_incompatible_arguments_error(FMT_CVE_OPTION, FMT_JSON_OPTION)

    if args.priority is not None:
        raise_incompatible_arguments_error(FMT_CVE_OPTION, FMT_PRIORITY_OPTION)

    if args.show_links:
        raise_incompatible_arguments_error(FMT_CVE_OPTION, FMT_SHOW_LINKS_OPTION)


def raise_on_invalid_json_options(args):
    if not args.json:
        return

    if args.nagios:
        raise_incompatible_arguments_error(FMT_JSON_OPTION, FMT_NAGIOS_OPTION)


def raise_incompatible_arguments_error(arg1, arg2):
    raise ArgumentError(
        "The %s and %s options are incompatible and may not "
        "be specified together." % (arg1, arg2)
    )


def raise_on_missing_manifest_file(args):
    raise_on_missing_file(args.manifest)


def raise_on_missing_db_file(args):
    raise_on_missing_file(args.db)


def raise_on_missing_file(file_path):
    if not file_path:
        return

    file_abs_path = os.path.abspath(file_path)
    if not os.path.isfile(file_abs_path):
        # TODO: mention snap confinement in error message
        raise ArgumentError(
            'Cannot find file "%s". Current '
            'working directory is "%s".' % (file_abs_path, os.getcwd())
        )

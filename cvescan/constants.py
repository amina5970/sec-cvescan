CVESCAN_DESCRIPTION = "Use this script to use the Ubuntu security OVAL files."

CVE_HELP = "Report if this system is vulnerable to a specific CVE."

PRIORITY_HELP = ("'critical' = show only critical CVEs.\n'high'     = show "
        "critical and high CVEs (default)\n'medium'   = show critical and "
        "high and medium CVEs\n'all'      = show all CVES (no filtering "
        "based on priority)")

SILENT_HELP = ("Enable script/Silent mode: To be used with "
        "'-c <cve-identifier>'.\nDo not print text output; exit 0 if not "
        "vulnerable, exit 1 if vulnerable.")

MANIFEST_HELP = ("Enable manifest mode. Do not scan localhost.\nInstead run a "
        "scan against a Ubuntu Official Cloud Image package manifest file.\n"
        "The script will use a server manifest file.")

FILE_HELP = ("Used with '-m' option to override the default behavior. Specify\n "
        "a manifest file to scan instead of downloading an OCI manifest.\n "
        "The file needs to be readable under snap confinement.\n User's home "
        "will likely work, /tmp will likely not work.")

NAGIOS_HELP = ("Enable Nagios mode for use with NRPE.\nTypical nagios-style "
        "\"OK|WARNING|CRITICAL|UNKNOWN\" messages\n and exit codes of 0, 1, "
        "2, or 3.\n0/OK = not vulnerable to any known and patchable CVEs of "
        "the\n specified priority or higher.\n1/WARNING = vulnerable to at "
        "least one known CVE of the specified\n priority or higher for which "
        "there is no available update.\n2/CRITICAL = vulnerable to at least "
        "one known and patchable CVE of\n the specified priority or higher.\n"
        "3/UNKNOWN = something went wrong with the script, or oscap.")

LIST_HELP = ("Disable links. Show only CVE IDs instead of URLs.\nDefault is to "
        "output URLs linking to the Ubuntu CVE tracker.")

REUSE_HELP = ("re-use zip, oval, xml, and htm files from cached versions if "
        "possible.\nDefault is to redownload and regenerate everything.\n"
        "Warning: this may produce inaccurate results.")

TEST_HELP = ("Test mode, use test OVAL data to validate that cvescan and oscap "
        "are\n working as expected. In test mode, files are not downloaded.\n"
        "In test mode, the remove and verbose options are enabled automatically.")

UPDATES_HELP = ("Only show CVEs affecting packages if there is an update "
        "available.\nDefault: show only CVEs affecting this system or "
        "manifest file.")

VERBOSE_HELP = ("Enable verbose messages.")

EXPERIMENTAL_HELP = ("Enable eXperimental mode.\nUse experimental (also called "
        "\"alpha\") OVAL data files.\nThe alpha OVAL files include "
        "information about package updates\n available for users of Ubuntu "
        "Advantage running systems with ESM\n Apps enabled.")

DEBUG_LOG = "debug.log"
DEFAULT_MANIFEST_FILE = "manifest"

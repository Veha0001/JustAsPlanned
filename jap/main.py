#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "demodapk",
# ]
# ///

"""Main Patcher"""

import os
from types import SimpleNamespace

import rich_click as click
from demodapk import __version__
from demodapk.mods import dowhat, runsteps
from demodapk.utils import show_logo

SCRIPTS_PATH = os.path.abspath("scripts")
CONFIG_DATA = {
    "apps": {
        "com.prpr.musedash": {
            "apkeditor": {"javaopts": "-Xmx1G", "output": "./build/MUSEDASH"},
            "app_name": "MUSEDASH",
            "commands": {
                "quietly": True,
                "begin": [
                    {
                        "run": "hexsaly open $BASE_LIB/arm64-v8a/libil2cpp.so -i 0",
                        "title": "Hexsaly > [cyan3]Just As Planned [black](Android ARM64)",
                    },
                    {
                        "run": "python genicons.py assets/rin.png $BASE_RESDIR -rf",
                        "title": "Updated new icons",
                    },
                    "rm -rf $BASE/root/lib/armeabi-v7a",
                ],
                "end": [
                    {
                        "run": "apksigner sign --key ./assets/android.pk8 --cert ./assets/android.x509.pem $BUILD",
                        "title": "Signing Build",
                    }
                ],
            },
            "level": 2,
            "package": "com.prpr.musedashjap",
            "manifest": {"remove_metadata": ["com.google.android.gms.games.APP_ID"]},
        }
    }
}

os.environ["PATH"] = SCRIPTS_PATH + os.pathsep + os.environ.get("PATH", "")


@click.command()
@click.help_option("-h", "--help")
@click.argument(
    "apk_dir",
    required=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=str),
    metavar="<apk>",
)
@click.option(
    "-i",
    "--in",
    "index",
    type=int,
    default=None,
    metavar="<int>",
    help="Index of package configured.",
)
@click.option(
    "-sc",
    "--schema",
    is_flag=True,
    help="Apply schema to the config.",
)
@click.option(
    "-S",
    "--single-apk",
    is_flag=True,
    default=False,
    help="Keep only the rebuilt APK.",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Force to overwrite.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, file_okay=True, dir_okay=True, path_type=str),
    metavar="<path>",
    help="Path to writes decode and build.",
)
@click.option(
    "-ua",
    "--update-apkeditor",
    is_flag=True,
    help="Update APKEditor latest version.",
)
@click.option(
    "-dex",
    "--raw-dex",
    is_flag=True,
    default=False,
    help="Decode with raw dex.",
)
@click.option(
    "-nn",
    "--no-rename",
    is_flag=True,
    help="Keep manifest names.",
)
@click.option(
    "-nfb",
    "--no-facebook",
    is_flag=True,
    help="Skip Facebook API update.",
)
@click.option(
    "-nas",
    "--rename-smali",
    is_flag=True,
    help="Rename package in smali files and directories.",
)
@click.version_option(
    __version__,
    "-v",
    "--version",
)
def main(**kwargs):
    """patch: Just As Planned"""
    args = SimpleNamespace(**kwargs)
    packer = CONFIG_DATA.get("apps", {})
    show_logo("MUSE JAP")
    dowhat(args, click)
    runsteps(args, packer)


if __name__ == "__main__":
    main()

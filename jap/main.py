# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "demodapk==1.1.17",
# ]
# ///
"""
Copyright (c) 2025 @Veha0001. All Rights Reserved.
"""

import sys
from types import SimpleNamespace

import rich_click as click
from demodapk import __version__
from demodapk.mark import update_apkeditor
from demodapk.mods import runsteps
from demodapk.utils import show_logo

CONFIG_DATA: dict = {
    "com.prpr.musedash": {
        "apkeditor": {"output": "./build/MUSEDASH"},
        "app_name": "MUSEDASH",
        "level": 2,
        "package": "com.prpr.musedashjap",
        "hex": [
            {
                "path": "root/lib/arm64-v8a/libil2cpp.so",
                "patch": [
                    "00 18 40 F9 60 00 00 B4 E2 03 1F 2A | 1F 20 03 D5",
                    (
                        "F4 4F BE A9 FD 7B 01 A9 FD 43 00 91 ?? ?? ?? ?? ?? ?? ?? ?? E8 "
                        "00 00 37 ?? ?? ?? ?? ?? ?? ?? ?? 00 01 40 B9 ?? ?? ?? ?? E8 03 "
                        "00 32 68 ?? ?? 39 ?? ?? ?? ?? ?? ?? ?? ?? 60 02 40 F9 ?? ?? ?? "
                        "?? ?? ?? ?? ?? 08 E0 40 B9 48 00 00 35 ?? ?? ?? ?? ?? ?? ?? ?? "
                        "?? ?? ?? ?? E8 00 00 35 ?? ?? ?? ?? ?? ?? ?? ?? 00 01 40 B9 ?? "
                        "?? ?? ?? E8 03 00 32 88 ?? ?? 39 60 02 40 F9 ?? ?? ?? ?? ?? ?? "
                        "?? ?? 08 E0 40 B9 68 00 00 35 ?? ?? ?? ?? 60 02 40 F9 ?? ?? ?? "
                        "?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 08 E0 40 B9 "
                        "?? ?? ?? ?? ?? ?? ?? ?? 21 00 00 94 ?? ?? ?? ?? 60 02 40 F9 ?? "
                        "?? ?? ?? ?? ?? ?? ?? 08 E0 40 B9 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? "
                        "?? ?? ?? ?? ?? ?? 69 02 40 F9 ?? ?? ?? ?? F4 03 00 AA ?? ?? ?? "
                        "?? 08 01 40 F9 | 20 00 80 D2 C0 03 5F D6"
                    ),
                    (
                        "F5 0F 1D F8 F4 4F 01 A9 FD 7B 02 A9 FD 83 00 91 ?? ?? ?? ?? ?? "
                        "?? ?? ?? E8 00 00 37 ?? ?? ?? ?? ?? ?? ?? ?? 00 01 40 B9 ?? ?? "
                        "?? ?? E8 03 00 32 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 80 02 40 "
                        "F9 ?? ?? ?? ?? 40 04 00 B4 ?? ?? ?? ?? ?? ?? ?? ?? E2 03 1F AA "
                        "A1 02 40 F9 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? E2 03 1F AA 61 "
                        "02 40 F9 ?? ?? ?? ?? ?? ?? ?? ?? 80 02 40 F9 ?? ?? ?? ?? ?? ?? "
                        "?? ?? A1 02 40 F9 E2 03 1F AA | 20 00 80 D2 C0 03 5F D6"
                    ),
                ],
            }
        ],
        "path": {
            "rm": "root/lib/armeabi-v7a",
            "add": "./assets/res/ resources/package_1/res",
        },
    },
}


# INFO: https://click.palletsprojects.com/en/stable/api/
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
    "--id",
    "index",
    type=int,
    hidden=True,
    default=0,  # Skip inquirer
    metavar="<int>",
    help="Index of package configured.",
)
@click.option(
    "-p",
    "--package",
    type=str,
    default=None,
    metavar="<str>",
    help="Change name of package.",
)
@click.option(
    "-S",
    "--single-apk",
    is_flag=True,
    default=False,
    help="Keep only the rebuilt APK.",
)
@click.option(
    "-s",
    "--skip",
    "skip_list",
    metavar="<key>",
    type=click.Choice(["fb", "rename"]),
    multiple=True,
    help="Skip specific JSON config keys.",
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
    "--getup",  # Wake Up!
    "update_apkeditor",
    is_flag=True,
    help="Update APKEditor latest version.",
)
@click.option(
    "-fb",
    "--fbapi",
    type=str,
    default=None,
    metavar="<str>",
    help="Facebook api update.",
)
@click.option(
    "-dex",
    "--raw-dex",
    is_flag=True,
    default=False,
    help="Decode with raw dex.",
)
@click.option(
    "-sm",
    "--xsmali",
    is_flag=True,
    help="Rename package in smali files and directories.",
)
@click.option(
    "-m",
    "--master",
    is_flag=True,
    default=False,
    help="All master unlocked.",
)
@click.option(
    "-res",
    "--res-dir",
    metavar="<str>",
    type=click.Path(exists=True, path_type=str),
    default="./assets/res/",
    help="Path to JAP resources.",
)
@click.option("-ez", "--easy", is_flag=True, help="Easy original res.")
@click.version_option(
    __version__,
    "-v",
    "--version",
    message="Muse, demodapk v%(version)s",
)
def main(**kwargs):
    """Just As Planned: APK patcher"""
    args = SimpleNamespace(**kwargs)
    packer: dict = CONFIG_DATA
    show_logo("MUSE.JAP")
    # New Optional...
    if getattr(args, "fbapi", None):
        try:
            app_id, client_token = str(args.fbapi).split(":", 1)
            packer["com.prpr.musedash"].setdefault("facebook", {}).update(
                {"app_id": app_id.strip(), "client_token": client_token.strip()}
            )
        except ValueError as e:
            raise click.UsageError(
                f"Invalid format for --fbapi, Use <app_id:client_token>.\n{e}"
            )
    if args.package:
        packer["com.prpr.musedash"]["package"] = args.package
    if args.master:
        master_patch = (
            "F5 0F 1D F8 F4 4F 01 A9 FD 7B 02 A9 FD 83 00 91 "
            "?? ?? ?? ?? ?? ?? ?? ?? E8 00 00 37 ?? ?? ?? ?? ?? ?? ?? ?? 00 01 40 B9 ?? ?? ?? "
            "?? E8 03 00 32 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 88 00 "
            "08 36 ?? ?? ?? ?? 48 00 00 35 ?? ?? ?? ?? ?? ?? ?? ?? C0 00 00 36 ?? ?? ?? ?? ?? "
            "?? ?? ?? E0 03 00 32 ?? ?? ?? ?? C0 03 5F D6 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? "
            "?? ?? ?? ?? 88 00 08 36 08 E0 40 B9 48 00 00 35 "
            "| 20 00 80 D2 C0 03 5F D6"
        )
        packer["com.prpr.musedash"]["hex"][0]["patch"].append(master_patch)

    if args.res_dir is not None:
        packer["com.prpr.musedash"]["path"]["add"] = (
            args.res_dir + " resources/package_1/res"
        )
    if args.easy:
        packer["com.prpr.musedash"]["path"].pop("add", None)

    # Awe!
    if args.update_apkeditor:
        update_apkeditor()
        sys.exit(0)
    apk_dir = getattr(args, "apk_dir", None)
    if apk_dir is None:
        ctx = click.RichContext(main)
        click.echo(main.get_help(ctx))
        sys.exit(0)

    runsteps(args, packer)


if __name__ == "__main__":
    main()

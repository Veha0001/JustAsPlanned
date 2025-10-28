# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "demodapk",
#     "pillow",
# ]
# ///
"""Main Patcher"""

import os
import platform
import shutil
import sys
from types import SimpleNamespace
from typing import Any

import rich_click as click
from demodapk import __version__
from demodapk.mark import msg
from demodapk.mods import (
    ConfigHandler,
    UpdateContext,
    dowhat,
    get_demo,
    get_finish,
    get_the_inputs,
    get_updates,
)
from demodapk.utils import console, show_logo
from genicons import update_existing_mipmaps, validate_image
from rich.panel import Panel

HEXSALY_NO_DELAY = "-k" if os.name == "nt" or platform.system() == "Windows" else ""
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
                        "run": "hexsaly open $BASE_LIB/arm64-v8a/libil2cpp.so"
                        f" {HEXSALY_NO_DELAY} ",
                        "title": "Hexsaly > [cyan3]Just As Planned [black](Android ARM64)",
                    }
                ],
                "end": [
                    {
                        "run": "apksigner sign --key ./assets/android.pk8"
                        " --cert ./assets/android.x509.pem $BUILD",
                        "title": "Signing Build",
                    }
                ],
            },
            "level": 2,
            "package": "com.prpr.musedashjap",
        }
    }
}

os.environ["PATH"] = SCRIPTS_PATH + os.pathsep + os.environ.get("PATH", "")


def get_path_build(decoded_dir: str):
    """
    Get correct path output

    :return: output_apk_path, output_apk_file
    """
    decoded_dir = os.path.abspath(decoded_dir)
    output_apk_name = os.path.basename(decoded_dir.rstrip("/"))
    output_apk_path = os.path.join(decoded_dir, output_apk_name + ".apk")
    output_apk_file = decoded_dir + ".apk"
    return output_apk_path, output_apk_file


def get_customize(src_icon: str = "./assets/rin.png", uicon: bool = False):
    """
    Custom Update: remove arm32, apply new icons
    """
    base_lib = os.environ.get("BASE_LIB")
    libarm = os.path.join(f"{base_lib}/armeabi-v7a")
    if os.path.exists(libarm):
        shutil.rmtree(libarm)
        msg.progress(f"Removed [royal_blue1]{os.path.basename(libarm)}")

    base_resdir = os.environ.get("BASE_RESDIR")
    if os.path.exists(src_icon) and not uicon:
        src_image = validate_image(src_icon)
        update_existing_mipmaps(base_resdir, src_image, quiet=True)
        msg.progress("Updated new icons")


def runsteps(args, packer):
    """
    Custom execute the complete APK modification workflow.
    """
    basic = get_the_inputs(packer, args)
    conf = ConfigHandler(basic.apk_config)

    android_manifest, smali_folder, resources_folder, value_strings, decoded_dir = (
        get_demo(
            conf,
            basic,
            args=args,
        )
    )

    with console.status(
        "[bold orange_red1]Modifying...", spinner_style="orange_red1", spinner="point"
    ):
        ctx = UpdateContext(
            value_strings=value_strings,
            smali_folder=smali_folder,
            resources_folder=resources_folder,
            package_orig_name=basic.package_orig_name,
            package_orig_path=basic.package_orig_path,
            dex_folder_exists=basic.dex_folder_exists,
        )
        get_customize(src_icon=args.jpic, uicon=args.njp)
        get_updates(conf, android_manifest, basic.apk_config, ctx, args=args)
    get_finish(conf, decoded_dir=decoded_dir, apk_config=basic.apk_config, args=args)


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
    "-m",
    "--mid",
    type=int,
    metavar="<int>",
    default=0,
    show_default=True,
    help="Patch index range of jap android.",
)
@click.option(
    "-jp",
    "--jpic",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=str),
    metavar="<path>",
    default="./assets/rin.png",
    show_default=True,
    help="Path to the new app_icon.",
)
@click.option(
    "-njp",
    "--njp",
    is_flag=True,
    default=False,
    help="Uses original app_icon.",
)
@click.option(
    "-p",
    "--package",
    metavar="<name>",
    type=str,
    default="com.prpr.musedashjap",
    show_default=True,
    help="Change the package name.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, file_okay=True, dir_okay=True, path_type=str),
    default="./build/MUSEDASH",
    show_default=True,
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
    "-fb",
    "--fbok",
    type=str,
    default=None,
    metavar="<id;ct>",
    help="Facebook api update.",
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
    """Patcher: Just As Planned (Android)"""
    args = SimpleNamespace(**kwargs)
    packer: dict[str, Any] = CONFIG_DATA.get("apps", {})
    app_key = next(iter(packer.keys()))
    if getattr(args, "package", None):
        packer[app_key]["package"] = args.package
    if getattr(args, "fbok", None):
        try:
            app_id, client_token = str(args.fbok).split(":", 1)
            packer[app_key].setdefault("facebook", {}).update(
                {"app_id": app_id.strip(), "client_token": client_token.strip()}
            )
        except ValueError:
            console.print(
                Panel(
                    "Invalid format for -fb/fbok, Use <app_id:client_token>.",
                    title="Error",
                    title_align="left",
                    style="bold red",
                ),
            )
            sys.exit(1)

    commands: dict = packer[app_key].setdefault("commands", {})
    begin_list: dict = commands.setdefault("begin", {})
    end_list: dict = commands.setdefault("end", {})
    # Fix execute commands
    base_path = os.path.splitext(args.output)[0]
    apk_path, apk_file = get_path_build(base_path)
    build = apk_path
    if getattr(args, "single_apk", True):
        build = apk_file
    begin_list[0]["run"] = (
        f"hexsaly {HEXSALY_NO_DELAY} open {base_path}/root/lib/arm64-v8a/libil2cpp.so"
        f" -i {args.mid}"
    )
    end_list[0]["run"] = (
        "apksigner sign --key ./assets/android.pk8"
        f" --cert ./assets/android.x509.pem {build}"
    )
    if args.mid == 1:
        begin_list[0]["title"] = (
            "Hexsaly > [cyan3]Just As Planned [Master] [black](Android ARM64)"
        )
    elif args.mid > 1:
        begin_list[0]["title"] = f"Hexsaly > [cyan3]Index {args.mid}"
    elif args.mid < 0:
        console.print(
            Panel(
                f"Hexsaly cannot allow negative index [white]{args.mid}",
                title="Error",
                title_align="left",
                style="bold red",
            ),
        )
        sys.exit(1)
    # Main workflows
    show_logo("MUSE JAP")
    dowhat(args, click)
    runsteps(args, packer)


if __name__ == "__main__":
    main()

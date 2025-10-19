# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "demodapk",
#     "pillow",
# ]
# ///
"""Main Patcher"""

import os
from types import SimpleNamespace

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

SCRIPTS_PATH = os.path.abspath("scripts")
PATCH_ID: int = 0
CONFIG_DATA = {
    "apps": {
        "com.prpr.musedash": {
            "apkeditor": {
                "javaopts": "-Xmx1G",
                "output": "./build/MUSEDASH",
                "dex": True,
            },
            "app_name": "MUSEDASH",
            "commands": {
                "quietly": True,
                "begin": [
                    {
                        "run": f"hexsaly open $BASE_LIB/arm64-v8a/libil2cpp.so -i {PATCH_ID}",
                        "title": "Hexsaly > [cyan3]Just As Planned [black](Android ARM64)",
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
        base_resdir = os.environ["BASE_RESDIR"]
        src_image = validate_image("./assets/rin.png")
        update_existing_mipmaps(base_resdir, src_image, quiet=True)
        msg.progress("Updated new icons")
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
    help="Patch index range of jap android.",
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
    global PATCH_ID
    args = SimpleNamespace(**kwargs)
    packer = CONFIG_DATA.get("apps", {})
    PATCH_ID = args.mid
    show_logo("MUSE JAP")
    dowhat(args, click)
    runsteps(args, packer)


if __name__ == "__main__":
    main()

"""
Genicons: Android Icon Generator with Mask Support
Author: @Veha0001
"""

import os
import sys
from enum import Enum
from pathlib import Path

import typer
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError
from rich.console import Console
from typing_extensions import Annotated

# pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments

console = Console()
app = typer.Typer(
    help="Android Launcher Icon Generator with Mask Support",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    add_completion=False,
)

LEGACY_SIZES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}

ADAPTIVE_FOREGROUND_SIZES = {
    "mdpi": 108,
    "hdpi": 162,
    "xhdpi": 216,
    "xxhdpi": 324,
    "xxxhdpi": 432,
}

SAFE_ZONE_RATIO = 66 / 72
SHAPES = ["circle", "squircle", "rounded_square", "square", "full_bleed"]


class IconShapes(str, Enum):
    """list shapes in str"""

    CC = "circle"
    SR = "squircle"
    RS = "rounded_square"
    SE = "square"
    FB = "full_bleed"


def validate_image(image_path: Path) -> Image.Image:
    """Validate and open an image as RGBA."""
    try:
        img = Image.open(image_path)
        return img.convert("RGBA")
    except UnidentifiedImageError as e:
        console.print(f"[bold red]Error loading source image:[/bold red] {e}")
        sys.exit(1)


def create_mask(size: int, shape: str) -> Image.Image:
    """Create mask of a given shape and size."""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)

    if shape == "circle":
        draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    elif shape == "squircle":
        radius = size // 2
        center = radius
        for y in range(size):
            for x in range(size):
                dx, dy = abs(x - center), abs(y - center)
                if (dx**4 + dy**4) <= radius**4:
                    mask.putpixel((x, y), 255)
    elif shape == "rounded_square":
        radius = int(size * 0.167)
        draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    else:
        draw.rectangle((0, 0, size, size), fill=255)

    return mask


def apply_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    """Apply a mask to an RGBA image."""
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result


def apply_safe_zone(image: Image.Image, target_size: int) -> Image.Image:
    """Resize image safely for adaptive icons."""
    safe_size = int(target_size * SAFE_ZONE_RATIO)
    padded = ImageOps.pad(
        image,
        (safe_size, safe_size),
        method=Image.Resampling.LANCZOS,
        color=(0, 0, 0, 0),
    )
    return ImageOps.pad(
        padded,
        (target_size, target_size),
        method=Image.Resampling.LANCZOS,
        color=(0, 0, 0, 0),
    )


def generate_legacy_icon(
    src: Image.Image,
    size: int,
    shape: str,
    mask_file: Path | None,
    background: str | None,
) -> Image.Image:
    """Generate legacy icon with shape/mask and optional background."""
    icon = ImageOps.pad(src, (size, size), method=Image.Resampling.LANCZOS)

    if mask_file and mask_file.exists():
        try:
            mask = Image.open(mask_file).convert("RGBA")
            _, _, _, alpha = mask.resize((size, size), Image.Resampling.LANCZOS).split()
            icon.putalpha(alpha)
            console.print(f"[green]Applied custom mask:[/green] {mask_file}")
        except UnidentifiedImageError as e:
            console.print(f"[yellow]Mask failed:[/yellow] {e}")
    else:
        icon = apply_mask(icon, create_mask(size, shape))

    if background:
        try:
            rgb = tuple(int(background.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
            bg = Image.new("RGB", icon.size, rgb)
            bg.paste(icon, (0, 0), icon)
            icon = bg
        except ValueError:
            console.print(f"[yellow]Invalid background color:[/yellow] {background}")

    return icon


def generate_adaptive_foreground(
    src: Image.Image, size: int, mask_file: Path | None
) -> Image.Image:
    """Generate adaptive foreground icon."""
    fg = apply_safe_zone(src, size)
    if mask_file and mask_file.exists():
        try:
            mask = Image.open(mask_file).convert("RGBA")
            _, _, _, alpha = mask.resize((size, size), Image.Resampling.LANCZOS).split()
            fg.putalpha(alpha)
            console.print(f"[green]Applied foreground mask:[/green] {mask_file}")
        except UnidentifiedImageError as e:
            console.print(f"[yellow]Foreground mask failed:[/yellow] {e}")
    return fg


def update_existing_mipmaps(res_dir: Path, src: Image.Image):
    """Update mipmap icons while preserving alpha."""
    for root, _, files in os.walk(res_dir):
        if "mipmap-" not in os.path.basename(root):
            continue
        for file in files:
            if not file.endswith(".png"):
                continue
            path = Path(root) / file
            try:
                existing = Image.open(path).convert("RGBA")
                alpha = existing.split()[-1]
                resized = src.resize(existing.size, Image.Resampling.LANCZOS)
                new_img = Image.new("RGBA", existing.size, (0, 0, 0, 0))
                new_img.paste(resized, (0, 0))
                # Well the problem is bad...
                new_img.putalpha(alpha)
                new_img.save(path, "PNG", optimize=True)
                console.print(f"[cyan]Updated:[/cyan] {path.relative_to(res_dir)}")
            except UnidentifiedImageError as e:
                console.print(f"[red]Failed updating {path}:[/red] {e}")


@app.command()
def run(
    source: Path = typer.Argument(
        ...,
        help="Path to source icon (recommended 512x512)",
        dir_okay=False,
        metavar="<icon>",
    ),
    output: Path = typer.Argument(
        "output",
        file_okay=False,
        metavar="<path>",
        help="Path to Android res directory",
    ),
    shape: Annotated[
        IconShapes,
        typer.Option(
            "-s",
            "--shape",
            help="Shape for legacy icons",
            case_sensitive=False,
            show_choices=True,
            metavar="<type>",
        ),
    ] = IconShapes.RS,
    name: str = typer.Option(
        "ic_launcher",
        "--name",
        "-n",
        metavar="<str>",
        help="Base name for icons",
    ),
    mask: Path | None = typer.Option(
        None,
        "--mask",
        "-m",
        metavar="<path>",
        help="Optional mask PNG with alpha",
    ),
    background: str | None = typer.Option(
        None,
        "--background",
        "-b",
        metavar="<str>",
        help="Background hex color for legacy icons",
    ),
    skip_foreground: bool = typer.Option(
        False,
        "-sf",
        "--skip-foreground",
        help="Skip adaptive foreground icons",
    ),
    skip_legacy: bool = typer.Option(
        False,
        "-sl",
        "--skip-legacy",
        help="Skip legacy icons",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files",
    ),
):
    """Generate Android launcher icons with optional mask and shape."""
    os.makedirs(output, exist_ok=True)
    src_img = validate_image(source)

    for density, legacy_size in LEGACY_SIZES.items():
        mipmap_dir = output / f"mipmap-{density}"
        mipmap_dir.mkdir(parents=True, exist_ok=True)
        fg_size = ADAPTIVE_FOREGROUND_SIZES[density]

        if not skip_foreground:
            fg_path = mipmap_dir / f"{name}_foreground.png"
            if force or not fg_path.exists():
                fg_img = generate_adaptive_foreground(src_img, fg_size, mask)
                fg_img.save(fg_path, "PNG", optimize=True)
                console.print(f"[green]Generated foreground:[/green] {fg_path}")

        if not skip_legacy:
            legacy_path = mipmap_dir / f"{name}.png"
            if force or not legacy_path.exists():
                legacy_img = generate_legacy_icon(
                    src_img, legacy_size, shape, mask, background
                )
                legacy_img.save(legacy_path, "PNG", optimize=True)
                console.print(f"[green]Generated legacy:[/green] {legacy_path}")

    console.print("[bold green]Icon generation complete.[/bold green]")


@app.command()
def cpm(
    res: Path = typer.Argument(
        ...,
        help="Path to Android res directory containing mipmaps.",
        file_okay=False,
        metavar="<path>",
    ),
    output: Path = typer.Argument(
        "masks",
        help="Directory to save extracted mask PNGs.",
        file_okay=False,
        metavar="<path>",
    ),
):
    """Extract alpha channel from existing mipmaps as proper transparent masks."""
    os.makedirs(output, exist_ok=True)

    for root, _, files in os.walk(res):
        if "mipmap-" not in os.path.basename(root):
            continue

        # Preserve folder structure
        relative_root = Path(root).relative_to(res)
        out_dir = output / relative_root
        out_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            if not file.endswith(".png"):
                continue

            path = Path(root) / file
            try:
                img = Image.open(path).convert("RGBA")
                alpha = img.split()[-1]  # get alpha channel

                # Create proper alpha mask: fully white with alpha applied
                mask_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
                mask_img.putalpha(alpha)

                mask_path = out_dir / file
                mask_img.save(mask_path, "PNG", optimize=True)
                console.print(f"[cyan]Extracted mask:[/cyan] {mask_path}")
            except UnidentifiedImageError as e:
                console.print(f"[red]Failed extracting {path}:[/red] {e}")

    console.print("[bold green]Mask extraction complete.[/bold green]")


@app.command()
def cvm(
    masks: Path = typer.Argument(
        ...,
        help="Directory containing mask PNGs (from cpm).",
        file_okay=False,
        dir_okay=True,
        metavar="<path>",
    ),
    src: Path = typer.Argument(
        ...,
        help="Path to source icon (RGBA).",
        file_okay=True,
        dir_okay=False,
        metavar="<path>",
    ),
    output: Path = typer.Argument(
        "output",
        help="Directory to save masked icons (default: output).",
        file_okay=False,
        dir_okay=True,
        metavar="<path>",
    ),
):
    """Apply masks from a directory over a source icon, preserving folder structure."""
    os.makedirs(output, exist_ok=True)
    src_img = validate_image(src)

    for root, _, files in os.walk(masks):
        relative_root = Path(root).relative_to(masks)
        out_dir = output / relative_root
        out_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            if not file.endswith(".png"):
                continue

            mask_path = Path(root) / file
            try:
                mask_img = Image.open(mask_path).convert("RGBA")
                _, _, _, mask_alpha = mask_img.split()

                # Resize source icon to match mask size
                resized_src = src_img.resize(mask_img.size, Image.Resampling.LANCZOS)
                new_img = Image.new("RGBA", mask_img.size, (0, 0, 0, 0))
                new_img.paste(resized_src, (0, 0))
                new_img.putalpha(mask_alpha)

                out_file = out_dir / file
                new_img.save(out_file, "PNG", optimize=True)
                console.print(f"[cyan]Applied mask:[/cyan] {out_file}")
            except UnidentifiedImageError as e:
                console.print(f"[red]Failed processing {mask_path}:[/red] {e}")

    console.print("[bold green]Mask application complete.[/bold green]")


@app.command()
def repng(
    icon: Path = typer.Argument(
        ..., help="Path to a new source icon.", dir_okay=False, metavar="<file>"
    ),
    res: Path = typer.Argument(
        ...,
        help="Path to Android res directory containing mipmaps.",
        file_okay=False,
        metavar="<path>",
    ),
):
    """Reapply a new icon over existing mipmaps (preserving alpha)."""
    os.makedirs(res, exist_ok=True)
    src_img = validate_image(icon)
    update_existing_mipmaps(res, src_img)
    console.print("[bold green]Mipmap update complete.[/bold green]")


@app.callback()
def main(quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output")):
    """Global options."""
    if quiet:
        console.file = open(os.devnull, "w")


if __name__ == "__main__":
    app()

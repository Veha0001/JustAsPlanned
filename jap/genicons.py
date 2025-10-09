#!/usr/bin/env python3
# Android Icon Generator with Mask Support (mask applies to both legacy & foreground)
# Author: Veha0001
# Last Updated: 2025-08-18

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageOps

VERSION = "1.1.5"
AUTHOR = "Veha0001"
LAST_UPDATED = "2025-08-18"

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


def validate_image(image_path):
    try:
        img = Image.open(image_path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        return img
    except Exception as e:
        print(f"Error loading source image: {e}")
        sys.exit(1)


def create_circle_mask(size):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    return mask


def create_squircle_mask(size):
    mask = Image.new("L", (size, size), 0)
    radius = size // 2
    center = radius
    for y in range(size):
        for x in range(size):
            dx, dy = abs(x - center), abs(y - center)
            if (dx**4 + dy**4) <= radius**4:
                mask.putpixel((x, y), 255)
    return mask


def create_rounded_square_mask(size, corner_radius=0.167):
    radius = int(size * corner_radius)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    return mask


def apply_mask(image, mask):
    result = Image.new("RGBA", image.size, (0, 0, 0, 0))
    result.paste(image, (0, 0), mask)
    return result


def apply_safe_zone(image, target_size):
    safe_size = int(target_size * SAFE_ZONE_RATIO)
    padded = ImageOps.pad(
        image,
        (safe_size, safe_size),
        method=Image.Resampling.LANCZOS,
        color=(0, 0, 0, 0),
        centering=(0.5, 0.5),
    )
    return ImageOps.pad(
        padded,
        (target_size, target_size),
        method=Image.Resampling.LANCZOS,
        color=(0, 0, 0, 0),
        centering=(0.5, 0.5),
    )


def generate_legacy_icon(source_img, size, shape, mask_file=None):
    squared = ImageOps.pad(
        source_img,
        (size, size),
        method=Image.Resampling.LANCZOS,
        color=(0, 0, 0, 0),
        centering=(0.5, 0.5),
    )

    if mask_file and os.path.exists(mask_file):
        try:
            mask = Image.open(mask_file).convert("RGBA")
            mask_resized = mask.resize((size, size), Image.Resampling.LANCZOS)
            _, _, _, alpha = mask_resized.split()
            squared.putalpha(alpha)
            print(f"Applied custom mask to legacy: {mask_file}")
            return squared
        except Exception as e:
            print(f"Warning: failed to apply mask '{mask_file}' to legacy: {e}")

    if shape == "circle":
        return apply_mask(squared, create_circle_mask(size))
    elif shape == "squircle":
        return apply_mask(squared, create_squircle_mask(size))
    elif shape == "rounded_square":
        return apply_mask(squared, create_rounded_square_mask(size))
    return squared


def generate_adaptive_foreground(source_img, size, mask_file=None):
    fg_img = apply_safe_zone(source_img, size)

    if mask_file and os.path.exists(mask_file):
        try:
            mask = Image.open(mask_file).convert("RGBA")
            mask_resized = mask.resize((size, size), Image.Resampling.LANCZOS)
            _, _, _, alpha = mask_resized.split()
            fg_img.putalpha(alpha)
            print(f"Applied custom mask to foreground: {mask_file}")
        except Exception as e:
            print(f"Warning: failed to apply mask '{mask_file}' to foreground: {e}")

    return fg_img


def update_existing_mipmaps(res_dir, source_img):
    for root, _, files in os.walk(res_dir):
        # Only process folders that contain 'mipmap-' in their name
        if "mipmap-" not in os.path.basename(root):
            continue

        for file in files:
            if file.endswith(".png"):
                path = os.path.join(root, file)
                try:
                    existing = Image.open(path).convert("RGBA")
                    alpha = existing.split()[-1]
                    resized_src = source_img.resize(
                        existing.size, Image.Resampling.LANCZOS
                    )
                    new_img = Image.new("RGBA", existing.size, (0, 0, 0, 0))
                    new_img.paste(resized_src, (0, 0))
                    new_img.putalpha(alpha)
                    new_img.save(path, "PNG", optimize=True)
                    rel_path = os.path.relpath(path, res_dir)
                    print(f"Updated: {rel_path}")
                except Exception as e:
                    print(f"Failed updating {path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Android Launcher Icon Generator with Mask Support"
    )

    parser.add_argument("source_icon", help="Path to source icon (recommended 512x512)")
    parser.add_argument("res_dir", help="Path to Android res directory")
    parser.add_argument(
        "-s",
        "--shape",
        choices=SHAPES,
        default="circle",
        help="Shape for legacy icons (ignored if -m is used)",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="ic_launcher",
        help="Base name for generated icons (default: ic_launcher)",
    )
    parser.add_argument("-m", "--mask", help="Custom mask file (PNG with alpha)")
    parser.add_argument(
        "-b", "--background", help="Background color (hex) for legacy icons"
    )
    parser.add_argument(
        "--skip-foreground", action="store_true", help="Skip adaptive foreground icons"
    )
    parser.add_argument("--skip-legacy", action="store_true", help="Skip legacy icons")
    parser.add_argument(
        "-f", action="store_true", help="Force overwrite existing files"
    )
    parser.add_argument(
        "-r",
        "--retain",
        action="store_true",
        help="Update existing mipmap PNGs using the source image while retaining their alpha masks",
    )
    args = parser.parse_args()

    print(f"Android Launcher Icon Generator v{VERSION}")

    if not os.path.isdir(args.res_dir):
        os.makedirs(args.res_dir, exist_ok=True)

    src_img = validate_image(args.source_icon)

    if args.retain:
        update_existing_mipmaps(args.res_dir, src_img)
        print("Mipmap update complete.")
        sys.exit(0)

    try:
        for density in LEGACY_SIZES:
            mipmap_dir = os.path.join(args.res_dir, f"mipmap-{density}")
            os.makedirs(mipmap_dir, exist_ok=True)

            legacy_size = LEGACY_SIZES[density]
            foreground_size = ADAPTIVE_FOREGROUND_SIZES[density]

            if not args.skip_foreground:
                fg_path = os.path.join(mipmap_dir, f"{args.name}_foreground.png")
                if args.f or not os.path.exists(fg_path):
                    fg_img = generate_adaptive_foreground(
                        src_img, foreground_size, args.mask
                    )
                    fg_img.save(fg_path, "PNG", optimize=True)
                    print(f"Generated foreground: {fg_path}")

            if not args.skip_legacy:
                legacy_path = os.path.join(mipmap_dir, f"{args.name}.png")
                if args.f or not os.path.exists(legacy_path):
                    legacy_img = generate_legacy_icon(
                        src_img, legacy_size, args.shape, args.mask
                    )

                    if args.background:
                        try:
                            bg_color = tuple(
                                int(args.background.lstrip("#")[i : i + 2], 16)
                                for i in (0, 2, 4)
                            )
                            bg = Image.new("RGB", legacy_img.size, bg_color)
                            bg.paste(legacy_img, (0, 0), legacy_img)
                            legacy_img = bg
                        except ValueError:
                            print(
                                f"Invalid background color: {args.background}, ignored."
                            )

                    legacy_img.save(legacy_path, "PNG", optimize=True)
                    print(f"Generated legacy icon: {legacy_path}")

        print("Icon generation complete.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# JAP

Just As Planned

## Install

using pip

```bash
pip install -r ./requirements.txt
```

or using uv

```bash
uv sync --script main.py
```

## Setup

create keystore by using [keyfitsign](https://github.com/Veha0001/keyfitsign).

copy your created keys into `./assets/android.pk8` and `./assets/android.x509.pem`

uses [App Manager](https://github.com/MuntashirAkon/AppManager) or other way to get the apk.

and then copy the apk to `./src/`.

## Run

using python

```bash
python main.py ./src/<apk> -Sf -dex
```

or using uv

```bash
uv run main.py <apk> [options]
```

## Android Patcher

For `patcher.exe` or `patcher`.

Run the **cli** in terminal.

```pwsh
.\patcher.exe -h
```

Run to update **APKEditor**.

```pwsh
.\patcher -ua
```

### Apply Patches

All data patches are in the [config](./config.json).

Normal steps:

- Install **Rust** via `winget` or `rustup`.
- Run `cargo install --git https://github.com/Veha0001/Hexsaly`.
- Make sure to add `~/.cargo/bin/` to your PATH.
- Download the `config.json` into a folder.
- Copy the required input files for the patches into that folder.
- Run the command `hexsaly`.
- Copy the resulting `*_patched*` files back to replace the original library files.

## Context

`assets` images are from MuseDash.

> [!NOTE]
> You must own the base game. in the official sale, everything costs only `$$` btw.
>
> Love PeroPero!

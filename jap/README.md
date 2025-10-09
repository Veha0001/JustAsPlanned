# JAP

Just As Planned

## Install

using pip

```bash
pip install demodapk --upgrade
```

or using uv

```bash
uv sync --script main.py
```

## Setup

create keystore by using [keyfitsign](https://github.com/Veha0001/keyfitsign).

copy your created keys into `./assets/android.pk8` and `./assets/android.x509.pem`

uses [App Manager](https://github.com/MuntashirAkon/AppManager) or other way to get the apk.

and then copy the apk to `./src`

## Run

using python

```bash
python -m main src/<apk> -Sf -dex
```

or using uv

```bash
uv run main.py <apk> [options]
```

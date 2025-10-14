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

and then copy the apk to `./src` OR whatever.

## Run

using python

```bash
python main.py src/<apk> -Sf -dex
```

or using uv

```bash
uv run main.py <apk> [options]
```

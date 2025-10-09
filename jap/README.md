# JAP

Just As Planned

## Install

using pip

```bash
pip install demodapk --upgrade
```

using uv

```bash
uv sync --script main.py
```

## Setup

create keystore by using [keyfitsign](https://github.com/Veha0001/keyfitsign).

copy your created keys into `./assets/user.pk8` and `./assets/user.x509.pem`

uses `App Manager` or other to get the apk.

and then copy the apk to `./src`

## Run

using python

```bash
python -m main src/<apk> -Sf -dex
```

using uv

```bash
uv run main.py <apk>
```

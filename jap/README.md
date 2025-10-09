# JAP

install requirements

```
pip install demodapk --upgrade
```

create keystore by using [keyfitsign](https://github.com/Veha0001/keyfitsign).

copy your created keys into `./assets/user.pk8` and `./assets/user.x509.pem`

uses `App Manager` or other to get the apk.

and then copy the apk to `./src`

run the main script:

```bash
python -m main src/<apk> -Sf -dex
```

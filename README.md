# Just As Planned
Make all DLC free and playable in a Certain Rhythm Game.

## Forked
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Veha0001/JustAsPlanned/build.yml?branch=main&style=for-the-badge&labelColor=%234c4f69&color=%2340a02b&logo=cplusplusbuilder)](https://github.com/Veha0001/JustAsPlanned/actions)
[![GitHub Release](https://img.shields.io/github/v/release/Veha0001/JustAsPlanned?display_name=release&style=for-the-badge&labelColor=%231e1e2e&color=%23f38ba8)](https://github.com/Veha0001/JustAsPlanned/releases)

**Good** enough.

---
# 8/2/2023
Added `GameAssembly.dll` patcher, you just have to put the original `GameAssembly.dll` in the same folder as `patch_ga.py` then it will generate `GameAssembly_patched.dll` and put it in Muse Dash directory.
Currently doesn't have Wildcard Bytes support (cuz im skill issue 😭)

# 8/3/2023
Added support for Wildcard Bytes, so no need to hardcode the whole actual bytes.
The `consts.py`, `main.py`, and `utility.py` is not needed if you use the `patch_ga.py` as i am no longer updating the offset for runtime patching.

# How to use?
1. Put original `GameAssembly.dll` to the same directory as `patch_ga.py` (Take the original `GameAssembly.dll` from Muse Dash directory)
2. Then run `patch_ga.py` (`python patch_ga.py`)
3. Wait for a while until it generated `GameAssembly_patched.dll`
4. Put `GameAssembly_patched.dll` to your Muse Dash directory and rename it to `GameAssembly.dll`

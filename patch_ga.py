#!/bin/python
import os
import platform

# ANSI color codes for styling
PURPLE = '\033[95m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Disable colors for Windows platforms that don't support ANSI codes natively
if platform.system() == 'Windows':
    try:
        # Windows 10+ supports ANSI codes if terminal processing is enabled
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except ImportError:
        PURPLE = RED = BLUE = BOLD = RESET = ''  # Disable colors if ANSI isn't supported

def pattern_scan(data, pattern):
    """Search for a byte pattern in the given data."""
    pattern_bytes = pattern.split(' ')
    pattern_length = len(pattern_bytes)
    
    # Convert pattern into a list of bytes (integers) or None for wildcards '??'
    pattern_bytes = [int(b, 16) if b != '??' else None for b in pattern_bytes]

    for i in range(len(data) - pattern_length + 1):
        if all(p_b is None or p_b == data[i+j] for j, p_b in enumerate(pattern_bytes)):
            return i
    return -1

def colorize_pattern(pattern):
    """Colorize the pattern to display ?? in blue, hex codes in bold and blue."""
    colored_pattern = []
    for byte in pattern.split(' '):
        if byte == '??':
            colored_pattern.append(f"{BLUE}??{RESET}")
        else:
            colored_pattern.append(f"{BOLD}{BLUE}{byte}{RESET}")
    return ' '.join(colored_pattern)

def patch_code(in_file, out_file, byte_pairs):
    # Ensure input file exists
    if not os.path.exists(in_file):
        print(f"{RED}Error: Input file '{in_file}' not found.{RESET}")
        return

    try:
        with open(in_file, "rb") as f:
            data = bytearray(f.read())
    except Exception as e:
        print(f"{RED}Error: Could not read file '{in_file}': {e}{RESET}")
        return

    for orig, repl in byte_pairs:
        index = pattern_scan(data, orig)
        if index != -1:
            # Print "Found a match" in purple, "for" in red, pattern in colorized hex
            print(f"{PURPLE}Found a match {RED}for {RESET}{colorize_pattern(orig)} at offset {hex(index)}")

            # Convert replacement string to bytes
            repl_bytes = bytes.fromhex(repl.replace(' ', ''))
            orig_bytes_len = len(orig.split(' '))

            # Ensure we are only replacing the length of the replacement bytes
            data[index:index + len(repl_bytes)] = repl_bytes

            # Print "Patched bytes" in purple and patched data in colorized hex
            print(f"{PURPLE}Patched bytes {RESET}at {hex(index)}: {colorize_pattern(repl)}")
        else:
            print(f"{RED}No matches found {RESET}for {colorize_pattern(orig)}")

    try:
        with open(out_file, "wb") as f:
            f.write(data)
        print(f"{PURPLE}Patched file saved as {out_file}{RESET}")
    except Exception as e:
        print(f"{RED}Error: Could not write to output file '{out_file}': {e}{RESET}")

# Byte sequences (original, replacement)
byte_sequences = [
    ("40 53 48 83 EC ?? 8B D9 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? ?? ?? ?? 45 33 C0 8B D3 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? 5B E9 ?? ?? ?? ?? CC CC CC CC CC 48 83 EC ?? 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? ?? ?? ?? 33 D2 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? E9 ?? ?? ?? ?? CC CC CC CC CC CC CC CC CC CC CC CC CC 40 53 48 83 EC ?? 8B D9 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? ?? ?? ?? 45 33 C0 8B D3 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? 5B E9 ?? ?? ?? ?? CC CC CC CC CC 48 83 EC ?? 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? ?? ?? ?? 33 D2 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? E9 ?? ?? ?? ?? CC CC CC CC CC CC CC CC CC CC CC CC CC 48 83 EC", 
    "48 B8 01 00 00 00 00 00 00 00 C3"),
    
    ("40 53 48 83 EC ?? 8B D9 33 C9 E8 ?? ?? ?? ?? 80 3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 05 ?? ?? ?? ?? 45 33 C0 8B D3 48 8B 88 ?? ?? ?? ?? 48 8B 49 ?? 48 83 C4 ?? 5B E9 ?? ?? ?? ?? CC CC CC CC CC 40 55 53", 
    "B8 85 47 DE 63 C3"),
    
    ("48 83 EC ?? 80 3D ?? ?? ?? ?? ?? 75 ?? 8B 0D ?? ?? ?? ?? E8 ?? ?? ?? ?? C6 05 ?? ?? ?? ?? ?? 48 8B 0D ?? ?? ?? ?? F6 81 ?? ?? ?? ?? ?? 74 ?? 83 B9 ?? ?? ?? ?? ?? 75 ?? E8 ?? ?? ?? ?? 33 C9 E8 ?? ?? ?? ?? 84 C0 0F 85", 
    "48 B8 01 00 00 00 00 00 00 00 C3")
]

# Input and output files
input_file = "GameAssembly.dll"
output_file = "GameAssembly_patched.dll"

# Run patching process
patch_code(input_file, output_file, byte_sequences)

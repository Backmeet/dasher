import re
from sys import argv

# === Encoding Mapping ===
encodeing = {
    " ": "0000000", "a": "0000001", "b": "0000010", "c": "0000011",
    "d": "0000100", "e": "0000101", "f": "0000110", "g": "0000111",
    "h": "0001000", "i": "0001001", "j": "0001010", "k": "0001011",
    "l": "0001100", "m": "0001101", "n": "0001110", "o": "0001111",
    "p": "0010000", "q": "0010001", "r": "0010010", "s": "0010011",
    "t": "0010100", "u": "0010101", "v": "0010110", "w": "0010111",
    "x": "0011000", "y": "0011001", "z": "0011010", "1": "0011011",
    "2": "0011100", "3": "0011101", "4": "0011110", "5": "0011111",
    "6": "0100000", "7": "0100001", "8": "0100010", "9": "0100011",
    "0": "0100100", "-": "0100101", "=": "0100110", ".": "0100111",
    ",": "0101000", ";": "0101001", "/": "0101010", "à": "0101011",
    "â": "0101100", "ç": "0101101", "è": "0101110", "é": "0101111",
    "ê": "0110000", "î": "0110001", "ï": "0110010", "û": "0110011",
    "|": "0110100", "[": "0110101", "]": "0110110", "\"": "0110111",
    "🟧": "0111000", "🟨": "0111001", "🟩": "0111010", "🟦": "0111011",
    "🟪": "0111100", "⬜": "0111101", "▶": "0111110", "": "0111111",
    "A": "1000001", "B": "1000010", "C": "1000011", "D": "1000100",
    "E": "1000101", "F": "1000110", "G": "1000111", "H": "1001000",
    "I": "1001001", "J": "1001010", "K": "1001011", "L": "1001100",
    "M": "1001101", "N": "1001110", "O": "1001111", "P": "1010000",
    "Q": "1010001", "R": "1010010", "S": "1010011", "T": "1010100",
    "U": "1010101", "V": "1010110", "W": "1010111", "X": "1011000",
    "Y": "1011001", "Z": "1011010", "!": "1011011", "@": "1011100",
    "#": "1011101", "$": "1011110", "%": "1011111", "?": "1100000",
    "&": "1100001", "*": "1100010", "(": "1100011", ")": "1100100",
    "_": "1100101", "+": "1100110", ".": "1100111", "'": "1101000",
    ":": "1101001", "~": "1101010", "À": "1101011", "Â": "1101100",
    "Ç": "1101101", "È": "1101110", "É": "1101111", "Ê": "1110000",
    "Ì": "1110001", "Ï": "1110010", "Û": "1110011", "¦": "1110100",
    "{": "1110101", "}": "1110110", "^": "1110111", ">": "1111000",
    "<": "1111001", "█": "1111010", "➡": "1111011", "⬅": "1111100",
    "⬆": "1111101", "⬇": "1111110", "\n": "0000000", "  ":" 00000000"
}

# === File Handling ===
program = open(argv[1], "r")
outF = open(argv[2], "w")

allocated = {}
free_addresses = set(range(65536))  # Set of available 16-bit addresses

def allocate(name):
    if name in allocated:
        return allocated[name]  # Return existing address if already allocated
    if not free_addresses:
        raise MemoryError("No available memory addresses")
    address = format(free_addresses.pop(), '016b')
    allocated[name] = address
    return address

def deallocate(name):
    if name in allocated:
        address = int(allocated[name], 2)
        free_addresses.add(address)
        del allocated[name]

def Exists(name):
    if name not in allocated:
        raise NameError(f"Variable {name} does not exist")
    return True

# === New Helper: parse_value ===
def parse_value(val):
    """
    Parse the given value and return a 16-bit binary string.
    
    The value may be given in three ways:
      - As a decimal integer (e.g. "123")
      - As a binary literal ending with 'b' (e.g. "100001b")
      - As an encoded character (e.g. '"a"' or simply a key that exists in the encoding)
    """
    # Case 1: Binary literal (ends with "b")
    if val.endswith("b"):
        bin_part = val[:-1]
        if all(c in "01" for c in bin_part) and bin_part:
            return format(int(bin_part, 2), '016b')
        else:
            raise ValueError("Invalid binary literal")
    # Case 2: Decimal integer
    elif val.isdigit():
        return format(int(val), '016b')
    # Case 3: Encoded value (quoted or direct)
    elif ((val.startswith('"') and val.endswith('"')) or 
          (val.startswith("'") and val.endswith("'"))):
        # Remove surrounding quotes
        text = val[1:-1]
        if len(text) == 1:
            if text in encodeing:
                code = encodeing[text]
                return code.zfill(16)
            else:
                raise ValueError(f"Character '{text}' not in encoding mapping")
        else:
            raise ValueError("Encoded values must be a single character")
    elif val in encodeing:
        code = encodeing[val]
        return code.zfill(16)
    else:
        raise ValueError("Invalid value format")

def toint(n):
    # (Legacy conversion function; not used in new value parsing)
    if all(c in "01" for c in n) and 1 < len(n) < 16:
        return format(int(n, 2), "016b")
    elif n.isdigit():
        return format(int(n), "016b")
    else:
        raise ValueError("Invalid number format")

opreationToBin = {
    "+": "0000000000000001",
    "-": "0000000000000010",
    "*": "0000000000000011",
    "/": "0000000000000100",
    "%": "0000000000000101",
    "&": "0000000000000110",
    "~": "0000000000000111",
    "^": "0000000000001000",
    ">": "0000000000001001",
    "<": "0000000000001010",
    "==": "0000000000001011",
    ">>>": "0000000000001100",
    "<<<": "0000000000001101",
    "++": "0000000000001110",
    "--": "0000000000001111"
}

# === FIRST PASS: Build a mapping from source line number to binary offset ===

lines = program.readlines()
LineToBin = {}  # Keys will be source line numbers (1-indexed)
BinLine = 0     # This will count the binary instructions produced

def estimate_bin_length(cmd, args):
    """
    Given a command and its arguments, return the number of binary instructions
    (lines) that the command will produce.
    """
    if cmd == "var":
        if args[0] == "set":
            return 3
        elif args[0] == "copy":
            return 5
        elif args[0] == "new":
            return 3
        elif args[0] == "remove":
            return 0  # 'remove' may not produce machine code
        elif args[0] == "math":
            # Both single-var and two-var math produce 8 binary instructions
            return 8
    elif cmd == "draw":
        return 5
    elif cmd == "rnd":
        return 3
    elif cmd == "http":
        if args[1] == "get":
            return 3
        elif args[1] == "post":
            return 5
    elif cmd == "io":
        return 3
    elif cmd == "exec":
        return 2
    elif cmd in ("forever", "if", "while"):
        return 2
    elif cmd == "log":
        return 2
    return 0

# Build mapping from source lines to binary offset.
for i, line in enumerate(lines, start=1):
    line = line.strip()
    if not line:
        continue
    parts = [part.strip() for part in line.split(",")]
    if parts:
        cmd = parts[0]
        args = parts[1:]
        LineToBin[i] = BinLine
        BinLine += estimate_bin_length(cmd, args) - 1

# === SECOND PASS: Generate binary code using the mapping ===

out = []
BinLine = 0

print("Lines to bin:")
for key, value in LineToBin.items():
    print(f"     -> {key}:{value}")

for i, line in enumerate(lines, start=1):
    line = line.strip()
    if not line:
        continue
    parts = [part.strip() for part in line.split(",")]
    cmd = parts[0]
    args = parts[1:]
    appended = []
    
    match cmd:
        case "var":
            match args[0]:
                case "set":  # var, set, name, value
                    if Exists(args[1]):
                        appended.extend([
                            f"{allocated[args[1]]} 0001",
                            f"{parse_value(args[2])} 0010\n"
                        ])
                case "copy":  # var, copy, name, VarSetToName
                    if Exists(args[1]) and Exists(args[2]):
                        appended.extend([
                            f"{allocated[args[1]]} 0001",
                            "0000000000000100 0011",
                            f"{allocated[args[2]]} 0001",
                            "0000000000000100 0100\n"
                        ])
                case "new":  # var, new, name, value
                    appended.extend([
                        f"{allocate(args[1])} 0001",
                        f"{parse_value(args[2])} 0010\n"
                    ])
                case "remove":  # var, remove, name
                    deallocate(args[1])
                    appended.append(f"Deallocate({args[1]})")
                case "math":  # var, math, ... (single-var or two-var)
                    if args[2].strip() in [">>>", "<<<", "++", "--"] and Exists(args[1]) and Exists(args[3]):
                        appended.extend([
                            f"{allocated[args[1]]} 0001",
                            "0000000000000000 0011",
                            f"{allocate('TEMP')} 0001",
                            "0000000000000000 0010",
                            "0000000000000001 0011",
                            f"{allocated[args[3]]} 0001",
                            f"{opreationToBin[args[2]]} 0101\n"
                        ])
                        deallocate("TEMP")
                    elif args[2].strip() in [op for op in opreationToBin if op not in [">>>", "<<<", "++", "--"]] \
                         and Exists(args[1]) and Exists(args[3]) and Exists(args[4]):
                        appended.extend([
                            f"{allocated[args[1]]} 0001",
                            "0000000000000000 0011",
                            f"{allocated[args[3]]} 0001",
                            "0000000000000001 0011",
                            f"{allocated[args[4]]} 0001",
                            f"{opreationToBin[args[2]]} 0101\n"
                        ])
        case "draw":  # draw, var, var
            if Exists(args[0]) and Exists(args[1]):
                appended.extend([
                    f"{allocated[args[0]]} 0001",
                    "0000000000000000 0011",
                    f"{allocated[args[1]]} 0001",
                    "0000000000000000 1010\n"
                ])
        case "rnd":  # rnd, var
            if Exists(args[0]):
                appended.extend([
                    f"{allocated[args[0]]} 0001",
                    "0000000000001000 0100\n"
                ])
        case "http":  # http, get|post, ...
            match args[1]:
                case "get":
                    if Exists(args[2]):
                        appended.extend([
                            f"{allocated[args[2]]} 0001",
                            "0000000000000000 1001\n"
                        ])
                case "post":
                    if Exists(args[2]) and Exists(args[3]):
                        appended.extend([
                            f"{allocated[args[2]]} 0001",
                            "0000000000000000 0011",
                            f"{allocated[args[3]]} 0001",
                            "0000000000000001 1001\n"
                        ])
        case "io":  # io, var, port (1-4)
            if Exists(args[0]) and int(args[1]) in [1, 2, 3, 4]:
                appended.extend([
                    f"{allocated[args[0]]} 0001",
                    f"000000000000{format(int(args[1]), '04b')} 0011\n"
                ])
        case "exec":  # exec, bin
            x = re.findall(r"(?:^|\n)([01]{8,16} [01]{4})", args[1])
            if x:
                appended.append(x[0])

        case "jump":  # forever, line
            target_line = int(args[0])
            if target_line in LineToBin:
                appended.append(f"{format(LineToBin[target_line], '016b')} 1011\n")
        
        case "if":  # if, line, var
            target_line = int(args[0])
            if target_line in LineToBin and Exists(args[1]):
                appended.extend([
                    f"{allocated[args[1]]} 0001",
                    f"{format(LineToBin[target_line], '016b')} 0110\n"
                ])
        case "while":  # while, line, var
            target_line = int(args[0])
            if target_line in LineToBin and Exists(args[1]):
                appended.extend([
                    f"{allocated[args[1]]} 0001",
                    f"{format(LineToBin[target_line], '016b')} 0111\n"
                ])
        case "log":  # log, var
            if Exists(args[0]):
                appended.extend([
                    f"{allocated[args[0]]} 0001",
                    "0000000000001000 0111\n"
                ])
        case "hlt":  # hlt
            appended.extend([
                "0000000000000000 1111"
            ])
    
    # Debug output (optional)
    print(f"\ncmd: {cmd}; args: {args}; line No: {i};")
    print("  -> Allocated:")
    for key, value in allocated.items():
        print(f"     -> {key}:{value}")
    print("  -> Generated instructions:")
    for instr in appended:
        print(f"     -> {instr}")
    
    # Append the generated instructions to the output list.
    for instr in appended:
        out.append(instr)

# Write the final binary code to the output file.
for bin_instr in out:
    outF.write(bin_instr + "\n")

# Clean up
program.close()
outF.close()

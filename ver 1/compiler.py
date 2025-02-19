import re
from sys import argv

# Open files
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

def toint(n):
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
    elif cmd in ("jmp", "jz", "jnz"):
        return 2
    elif cmd == "log":
        return 2
    return 0

# Loop over source lines to build the mapping.
for i, line in enumerate(lines, start=1):
    # Strip whitespace and ignore empty lines.
    line = line.strip()
    if not line:
        continue
    # Parse the line
    parts = [part.strip() for part in line.split(",")]
    if parts:
        cmd = parts[0]
        args = parts[1:]
        # Record the current binary offset for this source line:
        LineToBin[i] = BinLine
        # Increase BinLine by the number of instructions this command produces.
        BinLine += estimate_bin_length(cmd, args) - 1

        

# === SECOND PASS: Generate binary code using the mapping ===

# Reset file pointer if needed (or work with the already read list)
out = []
# Reset BinLine if you want to track binary offsets during generation (optional)
BinLine = 0

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
                            f"{format(int(args[2]), '016b')} 0010\n"
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
                        f"{format(int(args[2]), '016b')} 0010\n"
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
        case "jmp":  # jmp, line
            target_line = int(args[0])
            if target_line in LineToBin:
                appended.append(f"{format(LineToBin[target_line], '016b')} 1011\n")
        case "jz":  # jz, line, var
            target_line = int(args[0])
            if target_line in LineToBin and Exists(args[1]):
                appended.extend([
                    f"{allocated[args[1]]} 0001",
                    f"{format(LineToBin[target_line], '016b')} 0110\n"
                ])
        case "jnz":  # jnz, line, var
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
    
    # (Optional) Debug output for this source line:
    print(f"\ncmd: {cmd}; args: {args}; line No: {i};")
    print(f"  -> Allocated:")
    for key, value in allocated.items(): print(f"     -> {key}:{value}")
    print(f"  -> Lines to bin:")
    for key, value in LineToBin.items(): print(f"     -> {key}:{value}")
    print(f"  -> Generated instructions:")
    for i in appended: print(f"     -> {i}") 
    
    # Append the generated instructions (each as a new line) to the output list.
    for instr in appended:
        out.append(instr)

# Write the final binary code to the output file.
for bin_instr in out:
    outF.write(bin_instr + "\n")

# Clean up
program.close()
outF.close()

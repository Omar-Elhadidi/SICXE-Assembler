import re

OPCODES = {
    "ADD": 3, "ADDF": 3, "ADDR": 2, "AND": 3,
    "CLEAR": 2, "COMP": 3, "COMPF": 3, "COMPR": 2,
    "DIV": 3, "DIVF": 3, "DIVR": 2, "FIX": 1,
    "FLOAT": 1, "HIO": 1, "J": 3, "JEQ": 3,
    "JGT": 3, "JLT": 3, "JSUB": 3, "LDA": 3,
    "LDB": 3, "LDCH": 3, "LDF": 3, "LDL": 3,
    "LDS": 3, "LDT": 3, "LDX": 3, "LPS": 3,
    "MUL": 3, "MULF": 3, "MULR": 2, "NORM": 1,
    "OR": 3, "RD": 3, "RMO": 2, "RSUB": 3,
    "SHIFTL": 2, "SHIFTR": 2, "SIO": 1, "SSK": 3,
    "STA": 3, "STB": 3, "STCH": 3, "STF": 3,
    "STI": 3, "STL": 3, "STS": 3, "STSW": 3,
    "STT": 3, "STX": 3, "SUB": 3, "SUBF": 3,
    "SUBR": 2, "SVC": 2, "TD": 3, "TIO": 1,
    "TIX": 3, "TIXR": 2, "WD": 3, "PADD": "3X", "PSUB": "3X", "PMUL": "3X", "PDIV": "3X", "PMOV": "3X"
}

DIRECTIVES = ["START", "END", "BYTE", "WORD", "RESB", "RESW", "RESM", "BASE", "NOBASE"]

def clean_line(line):
    line = re.sub(r'^\s*\d+\s*', '', line)
    line = re.sub(r'\..*$', '', line)
    return line.strip()

def generate_intermediate_file(input_file, intermediate_file):
    with open(input_file, 'r') as infile, open(intermediate_file, 'w') as outfile:
        for line in infile:
            cleaned = clean_line(line)
            if cleaned:
                outfile.write(cleaned + '\n')

def pass1(intermediate_file, out_pass1_file, symtab_file):
    symtab = {}
    locctr = 0
    start_addr = 0
    output_lines = []

    with open(intermediate_file, 'r') as file:
        lines = file.readlines()

    first_line = lines[0].split()
    if first_line[1] == "START":
        start_addr = int(first_line[2], 16)
        locctr = start_addr
        output_lines.append(f"{hex(locctr)[2:].zfill(4).upper()} {' '.join(first_line)}")
        lines = lines[1:]
    else:
        locctr = 0

    for line in lines:
        parts = line.split()
        label, opcode, operand = "", "", ""

        if len(parts) == 3:
            label, opcode, operand = parts
        elif len(parts) == 2:
            if parts[0] in OPCODES or parts[0].startswith('+') or parts[0] in DIRECTIVES:
                opcode, operand = parts
            else:
                label, opcode = parts
        elif len(parts) == 1:
            opcode = parts[0]

        if label:
            if label in symtab:
                print(f"Error: Duplicate symbol {label}")
            else:
                symtab[label] = locctr

        output_lines.append(f"{hex(locctr)[2:].zfill(4).upper()} {' '.join(parts)}")

        if opcode.startswith('+'):
            base_opcode = opcode[1:]
            if base_opcode in OPCODES:
                locctr += 4
        elif OPCODES.get(opcode) == "3X":
            locctr += 3  # Format 3X adds 3 bytes
        elif opcode in OPCODES:
            locctr += OPCODES[opcode]
        elif opcode == "WORD":
            locctr += 3
        elif opcode in ["RESW", "RESM"]:
            locctr += 3 * int(operand)
        elif opcode == "RESB":
            locctr += int(operand)
        elif opcode == "BYTE":
            if operand.startswith("C'") or operand.startswith("X'"):
                value = operand[2:-1]
                if operand.startswith("C'"):
                    locctr += len(value)
                elif operand.startswith("X'"):
                    locctr += len(value) // 2
        elif opcode == "END":
            break

    with open(out_pass1_file, 'w') as out_file:
        for line in output_lines:
            out_file.write(line + '\n')

    with open(symtab_file, 'w') as sym_file:
        for label, addr in symtab.items():
            sym_file.write(f"{label} {hex(addr)[2:].zfill(4).upper()}\n")

    program_length = locctr - start_addr
    return program_length

def get_opcode_value(op):
    # Skip directives
    if op.upper() in ["WORD", "RESW", "RESB", "BYTE", "START", "END", "BASE", "NOBASE"]:
        return None  # Return None instead of "??"
    
    base = {
        "LDA": "00", "STA": "0C", "LDX": "04", "STX": "10",
        "ADD": "18", "SUB": "1C", "MUL": "20", "DIV": "24",
        "COMP": "28", "J": "3C", "JEQ": "30", "JGT": "34",
        "JLT": "38", "JSUB": "48", "RSUB": "4C", "TIX": "2C",
        "TD": "E0", "RD": "D8", "WD": "DC", "LDCH": "50", "STCH": "54",
        "LDB": "68", "STB": "78", "LDS": "6C", "STS": "7C",
        "LDF": "70", "STF": "80", "COMPF": "88", "CLEAR": "B4",
        "TIXR": "B8", "SHIFTL": "A4", "SHIFTR": "A8", "RMO": "AC",
        "ADDR": "90", "SUBR": "94", "MULR": "98", "DIVR": "9C",
        "FIX": "C4", "FLOAT": "C0", "HIO": "F4", "SIO": "F0", "NORM": "C8",
        "SVC": "B0", "SSK": "EC", "STL": "14", "FIX": "C4", "FLOAT": "C0", "HIO": "F4", "NORM": "C8", "SIO": "F0", "TIO": "F8",
        "PADD": "BC", "PSUB": "8C", "PMUL": "E4", "PDIV": "FC", "PMOV": "CC"
    }
    return base.get(op.upper(), None)


def pass2(intermediate_file, symtab_file, out_pass2_file, htme_file, program_length):
    with open(intermediate_file, 'r') as intf, open(symtab_file, 'r') as symf:
        intermediate_lines = [line.strip() for line in intf if line.strip()]
        symtab = dict(line.strip().split() for line in symf if line.strip())

    object_codes = []
    modifications = []
    program_name = ""
    start_address = 0
    first_exec_addr = ""
    base_register = None

    for idx, line in enumerate(intermediate_lines):
        parts = line.split()
        if len(parts) < 2:
            continue

        loc = parts[0]
        fields = parts[1:]

        label, opcode, operand = "", "", ""
        if len(fields) == 3:
            label, opcode, operand = fields
        elif len(fields) == 2:
            opcode, operand = fields
        elif len(fields) == 1:
            opcode = fields[0]

        loc_int = int(loc, 16)

        if opcode == "START":
            program_name = label
            start_address = int(operand, 16)
            first_exec_addr = operand
            continue
        elif opcode == "BASE":
            if operand in symtab:
                base_register = int(symtab[operand], 16)
            continue
        elif opcode == "END":
            break

        is_format4 = False
        if opcode.startswith('+'):
            is_format4 = True
            opcode = opcode[1:]

        op_val_hex = get_opcode_value(opcode)

        # Handle WORD
        if opcode == "WORD":
            obj_code = f"{int(operand):06X}"
            object_codes.append((loc, obj_code))
            continue

        # Handle BYTE
        elif opcode == "BYTE":
            if operand.startswith("C'"):
                chars = operand[2:-1]
                obj_code = ''.join([f"{ord(c):02X}" for c in chars])
            elif operand.startswith("X'"):
                obj_code = operand[2:-1]
            object_codes.append((loc, obj_code))
            continue

        # Skip unrecognized directives
        if op_val_hex is None:
            continue


        op_val = int(op_val_hex, 16)
        obj_code = ""

        if is_format4:
            n, i, x, b, p, e = 1, 1, 0, 0, 0, 1

            if operand.startswith('#'):
                i, n = 1, 0
                operand = operand[1:]
            elif operand.startswith('@'):
                i, n = 0, 1
                operand = operand[1:]

            if ',' in operand:
                symbol, mode = operand.split(',')
                if mode.upper() == 'X':
                    x = 1
                    operand = symbol

            address = 0
            if operand.isdigit():
                address = int(operand)
            elif operand in symtab:
                address = int(symtab[operand], 16)
            else:
                address = 0

            ni = (n << 1) | i
            flags = (x << 3) | (b << 2) | (p << 1) | e
            opcode_bin = ((op_val >> 2) << 2) | ni
            obj_code = f"{opcode_bin:02X}{flags << 4 | (address >> 16) & 0x0F:01X}{(address & 0xFFFF):04X}"
            if not operand.isdigit():
                modifications.append(f"M^{hex(loc_int + 1)[2:].zfill(6).upper()}^05")
                
        elif OPCODES.get(opcode) == "3X":
            # Assume operand is like R1,R2,R3,R4
            regs = [reg.strip() for reg in operand.split(',')]
            if len(regs) != 4:
                print(f"Error: 3X instruction {opcode} expects 4 registers.")
                continue

            reg_vals = []
            for reg in regs:
                reg_map = {'A': 0, 'X': 1, 'L': 2, 'B': 3, 'S': 4, 'T': 5, 'F': 6, 'PC': 8, 'SW': 9}
                reg_vals.append(reg_map.get(reg.upper(), 0))

            opcode_val = get_opcode_value(opcode)
            byte1 = int(opcode_val, 16)
            byte2 = (reg_vals[0] << 4) | reg_vals[1]
            byte3 = (reg_vals[2] << 4) | reg_vals[3]
            obj_code = f"{byte1:02X}{byte2:02X}{byte3:02X}"

        elif OPCODES.get(opcode) == 1:
            obj_code = f"{op_val:02X}"
            object_codes.append((loc, obj_code))
        # <-- This is the missing piece


        elif OPCODES.get(opcode) == 2:
            # Format 2: opcode + 2 register operands
            reg_map = {'A': 0, 'X': 1, 'L': 2, 'B': 3, 'S': 4, 'T': 5, 'F': 6, 'PC': 8, 'SW': 9}
            r1, r2 = 0, 0
            if operand:
                regs = operand.split(',')
                if len(regs) >= 1:
                    r1 = reg_map.get(regs[0].strip().upper(), 0)
                if len(regs) == 2:
                    r2 = reg_map.get(regs[1].strip().upper(), 0)
            obj_code = f"{op_val:02X}{r1:01X}{r2:01X}"


        elif opcode in OPCODES:
            n, i, x, b, p, e = 1, 1, 0, 0, 1, 0  # Default to PC-relative

            if operand:
                if operand.startswith('#'):
                    n, i = 0, 1
                    operand = operand[1:]
                elif operand.startswith('@'):
                    n, i = 1, 0
                    operand = operand[1:]

                if ',' in operand:
                    symbol, reg = operand.split(',')
                    if reg.upper() == 'X':
                        x = 1
                        operand = symbol

                disp = 0
                if operand.isdigit():
                    disp = int(operand)
                    b, p = 0, 0
                elif operand in symtab:
                    target = int(symtab[operand], 16)
                    pc = int(intermediate_lines[idx + 1].split()[0], 16) if idx + 1 < len(intermediate_lines) else loc_int + 3
                    offset = target - pc
                    if -2048 <= offset <= 2047:
                        disp = offset & 0xFFF
                        b, p = 0, 1
                    elif base_register is not None:
                        offset = target - base_register
                        if 0 <= offset <= 4095:
                            disp = offset
                            b, p = 1, 0
                else:
                    disp = 0
            else:  # Handle no-operand instructions (like RSUB)
                disp = 0
                b, p = 0, 0  # Reset addressing flags

            ni = (n << 1) | i
            flags = (x << 3) | (b << 2) | (p << 1) | e
            opcode_bin = ((op_val >> 2) << 2) | ni
            flags_disp_high = (flags << 4) | ((disp >> 8) & 0x0F)
            disp_low = disp & 0xFF
            obj_code = f"{opcode_bin:02X}{flags_disp_high:02X}{disp_low:02X}"

        elif opcode == "BYTE":
            if operand.startswith("C'"):
                chars = operand[2:-1]
                obj_code = ''.join([f"{ord(c):02X}" for c in chars])
            elif operand.startswith("X'"):
                obj_code = operand[2:-1]
        elif opcode == "WORD":
            obj_code = f"{int(operand):06X}"

        object_codes.append((loc, obj_code))

        with open(out_pass2_file, 'w') as outf:
            start_loc_skipped = False
            start_loc_to_skip = None

            for idx, line in enumerate(intermediate_lines):
                parts = line.strip().split()
                if not parts:
                    continue
                loc = parts[0]
                fields = parts[1:]

                obj = ""
                for oc in object_codes:
                    if oc[0] == loc:
                        obj = oc[1]
                        break

                if len(fields) >= 2 and fields[1] == "START" and not start_loc_skipped:
                    # Mark the START line to skip object code
                    start_loc_to_skip = loc
                    start_loc_skipped = True
                    obj = ""  # Remove object code only for the first START line

                outf.write(f"{loc} {obj}\n")


    with open(htme_file, 'w') as htmef:
        htmef.write(f"H^{program_name}^{start_address:06X}^{program_length:06X}\n")

        record = ""
        start_loc = None
        for loc, obj in object_codes:
            if not obj:
                if record:
                    length = len(record) // 2
                    htmef.write(f"T^{start_loc:06X}^{length:02X}^{record}\n")
                    record = ""
                    start_loc = None
                continue

            if start_loc is None:
                start_loc = int(loc, 16)

            if len(record + obj) > 60:
                length = len(record) // 2
                htmef.write(f"T^{start_loc:06X}^{length:02X}^{record}\n")
                record = obj
                start_loc = int(loc, 16)
            else:
                record += obj

        if record:
            length = len(record) // 2
            htmef.write(f"T^{start_loc:06X}^{length:02X}^{record}\n")

        for mod in modifications:
            htmef.write(mod + '\n')

        htmef.write(f"E^{first_exec_addr.zfill(6).upper()}\n")

if __name__ == "__main__":
    input_filename = "in.txt"
    intermediate_filename = "intermediate.txt"
    out_pass1_filename = "out_pass1.txt"
    symtab_filename = "symbTable.txt"
    out_pass2_filename = "out_pass2.txt"
    htme_filename = "HTME.txt"

    generate_intermediate_file(input_filename, intermediate_filename)
    program_length = pass1(intermediate_filename, out_pass1_filename, symtab_filename)
    pass2(out_pass1_filename, symtab_filename, out_pass2_filename, htme_filename, program_length)

    print("All passes complete. Files generated:")
    print("- intermediate.txt")
    print("- out_pass1.txt")
    print("- symbTable.txt")
    print("- out_pass2.txt")
    print("- HTME.txt")
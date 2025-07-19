# SIC/XE Assembler

This project implements a two-pass assembler for the SIC/XE architecture. It takes an assembly program written in SIC/XE format and generates object code and HTME records.

## 🧠 Features

- Full support for Pass 1 and Pass 2 of assembly
- Symbol table generation
- Object code generation for formats 1, 2, 3, 4
- Extended (4-byte) instruction handling
- Custom pseudo-instructions (e.g., PADD, PMOV)
- HTME record generation

## 📁 Input

Place your SIC/XE assembly program in `in.txt`.

The program should include:
- Comments and line numbers (which are stripped during preprocessing)
- Standard SIC/XE instructions and directives

## 🧪 Output Files

Running the assembler will generate:

| File Name         | Description                                      |
|------------------|--------------------------------------------------|
| `intermediate.txt` | Cleaned assembly instructions without comments or line numbers |
| `out_pass1.txt`    | Location counter per line (Pass 1 output)       |
| `symbTable.txt`    | Generated symbol table                           |
| `out_pass2.txt`    | Object code per line (Pass 2 output)            |
| `HTME.txt`         | Final object program in HTME record format      |

## 🚀 How to Run

1. Make sure you have Python installed.
2. Clone or download this repository.
3. Place your input file as `in.txt` in the same folder.
4. Run the assembler:

```bash
python3 assembler.py

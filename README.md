# SIC/XE Assembler

This project implements a **two-pass assembler** for the **SIC/XE architecture**, written in Python. It reads a SIC/XE assembly program, removes comments, builds a symbol table, generates object code, and outputs HTME-formatted machine code.

---

## 📁 Project Structure


---

## 🚀 How It Works

1. `in.txt`: Input file containing SIC/XE assembly code.
2. **Pass 1**:
   - Cleans input file.
   - Generates location counters.
   - Builds the symbol table.
3. **Pass 2**:
   - Uses the symbol table to generate object code.
   - Formats object code as HTME (Header, Text, Modification, End).
4. Final outputs are saved in the `output/` directory.

---

## ▶️ Running the Project

1. Make sure you have Python 3 installed.
2. Place your SIC/XE assembly code in `in.txt`.
3. Run the assembler:

```bash
python assembler.py

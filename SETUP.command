#!/bin/bash
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 tools/setup_wizard.py
else
  echo "Khong tim thay Python 3. Cai Python 3.8+ tu https://www.python.org/downloads/ roi chay lai."
  echo "Python 3 was not found. Install Python 3.8+ from https://www.python.org/downloads/ and run this again."
fi
echo
read -n 1 -s -r -p "Nhan phim bat ky de dong / Press any key to close..."

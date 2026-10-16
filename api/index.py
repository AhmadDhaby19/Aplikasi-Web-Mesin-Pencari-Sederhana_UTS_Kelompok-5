import sys
from pathlib import Path

# Daftarkan root direktori proyek ke sys.path agar modul engine dan app dapat diimpor
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app

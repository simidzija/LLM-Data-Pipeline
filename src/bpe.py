import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from logger import Logger



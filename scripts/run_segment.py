"""
Script to segment text into sentences. 

Uses the functionality of segment.py.
"""

# Standard library
import sys
from pathlib import Path

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from segment import segment_jsonl

if __name__ == "__main__":
    inpath = str(ROOT/'data'/'deduplicate_data.jsonl')
    outpath = str(ROOT/'data'/'segment_data.jsonl')
    segment_jsonl(inpath, outpath, processes=10, omit_duplicates=True)
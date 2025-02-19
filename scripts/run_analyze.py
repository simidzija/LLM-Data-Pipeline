"""
Script to analyze character frequencies in Wikipedia text. 

Uses the functionality of analyze.py.
"""

# Standard library
import sys
from pathlib import Path

# Local
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))
from analyze import analyze_jsonl

if __name__ == "__main__":
    ### Determine frequencies of different types of dash and quote characters

    inpath = str(ROOT/'data/normalize_data.jsonl')
    chars = ["\u0022",
             "\u0027", 
             "\u201c",
             "\u201d",
             "\u2018",
             "\u2019",
             "\u2033",
             "\u2032",
             "\u002d",
             "\u2013",
             "\u2014",
             "\u2212"
             ]
    counter = analyze_jsonl(inpath, chars=chars, processes=10)

    for char in chars:
        freq = counter[char]
        print(f'{char} = U+{hex(ord(char))[2:].upper():4}  -  {freq:7d} times')
    
    #####################  Results - Before Normalization  ####################

    # " = U+22    -  1560327 times
    # ' = U+27    -  1157724 times
    # “ = U+201C  -    15831 times
    # ” = U+201D  -    15699 times
    # ‘ = U+2018  -     5421 times
    # ’ = U+2019  -    23688 times
    # ″ = U+2033  -     1763 times
    # ′ = U+2032  -     3554 times
    # - = U+2D    -  1599384 times
    # – = U+2013  -   416646 times
    # — = U+2014  -    96472 times
    # − = U+2212  -     5920 times


    #####################  Results - After Normalization  ####################

    # " = U+22    -  1591857 times
    # ' = U+27    -  1186833 times
    # “ = U+201C  -        0 times
    # ” = U+201D  -        0 times
    # ‘ = U+2018  -        0 times
    # ’ = U+2019  -        0 times
    # ″ = U+2033  -     1763 times
    # ′ = U+2032  -     3554 times
    # - = U+2D    -  1605304 times
    # – = U+2013  -   416646 times
    # — = U+2014  -    96472 times
    # − = U+2212  -        0 times
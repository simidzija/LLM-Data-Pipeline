import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT/'src'))

from analyze import analyze_jsonl

if __name__ == "__main__":
    inpath = [
        str(ROOT/'data/parse_data_1.jsonl'),
        str(ROOT/'data/parse_data_2.jsonl'),
        str(ROOT/'data/parse_data_3.jsonl'),
        str(ROOT/'data/parse_data_4.jsonl'),
        str(ROOT/'data/parse_data_5.jsonl')
        ]
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
    
    ################################  Results  ################################

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
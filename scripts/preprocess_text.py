from numbers_to_letters import number_to_letters
from pathlib import Path
from string import punctuation
import unicodedata
import re
from argparse import ArgumentParser
from tqdm import tqdm
# from nltk import sent_tokenize

SENT_PUNCT = {"\?", "\.", "\:", "\;", "\!"}
PUNCT = set(list(punctuation))
PUNCT |= {"«", "»", "—", "›", "‹", "–", "…", "-", "“", "”", "¿"}
PUNCT = "".join(PUNCT)

SENT_TOKENIZER: str = rf"({'|'.join(SENT_PUNCT)})"

to_replace: dict = {
    "ụ́": "ụ",
    "ị́": "ị",
    "ạ́": "ạ",
    "ọ́": "ọ",
    "ạ̈": "ạ"
}

def replace_accents(line: str) -> str:
    """Finds some accentuated vowels and remove those accents."""
    for vowel in to_replace:
        line = re.sub(vowel, to_replace[vowel], line)
    return line

def tokenize_line(line: str):
    return re.split(SENT_TOKENIZER, line)

def process_line(line: str) -> str:
    """Process a given line in order by\
        deleting punctuation marks, numbers, etc."""
    line = line.strip()
    line = line.lower()
    line = replace_accents(line)
    if re.search("\d+", line):
        *rest, number = line.split(" ")
        rest = " ".join(rest)
        letters = number_to_letters(number)
        line = f"{rest} {letters}"
    line = re.sub("\'", "ʔ", line)
    line = re.sub("\ꞌ", "ʔ", line)
    for sent in tokenize_line(line):
        sent = sent.translate(str.maketrans('', '', PUNCT))
        sent = re.sub(" +", " ", sent)
        sent = unicodedata.normalize("NFC", sent)
        yield sent.strip()

def process_txt(text_file: Path, output_folder) -> None:
    """Process a given text file line by line."""
    sents = []
    with open(text_file, "r") as input_file:
        for line in input_file:
            line = unicodedata.normalize("NFC", line)
            line = process_line(line)
            for sent in line:
                if not sent:
                    continue
                sents.append(sent)
    with open(output_folder / f"{text_file.stem}.txt", "w") as output_file:
        output_file.write(".\n".join(sents))

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("-t", "--text_folder",
                        help="The folder containing the text files.")
    args = parser.parse_args()
    text_folder = Path(args.text_folder)
    output_folder = text_folder.parent / "preprocessed"
    output_folder.mkdir(parents=True, exist_ok=True)
    text_files = list(text_folder.glob("*.txt"))
    for text_file in tqdm(text_files):
        process_txt(text_file=text_file, output_folder=output_folder)

if __name__ == "__main__":
    main()

"""
authors:
    - Angèle Barbedette
    - Alex Cristia
    - Yaya Sy
    - William N. Havard

Script for phonemizing tsimane text.
"""
from pathlib import Path
import os
from argparse import ArgumentParser
import re
import unicodedata

def mapping_table_file_to_dictionnary(mapping_table_file: str) -> dict:
    """Read the mapping table as a dictionnary."""
    mapping_table_dictionnary = dict()
    with open(mapping_table_file) as mapping_table:
        for line in mapping_table:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            charactere, phoneme, _ = line.split("\t")
            charactere = unicodedata.normalize("NFC", charactere)
            phoneme = unicodedata.normalize("NFC", phoneme)
            mapping_table_dictionnary[charactere] = phoneme
    return mapping_table_dictionnary
        
def phonemize(mapping_table, utterance, spread=True):
    """
    Author: Angele.
    Phonemizes a given utterance.
    """
    utterance = unicodedata.normalize("NFC", utterance)
    ignore_in_first_pass = {"y", "ʏ", "j", "ᴊ"}
    vowels = ["a","ã","o","õ","i","ɨ","+","e","@","=","ə","$"]
    nasal_vowels = ["+","ã","õ","@","=","$"]

    ### here is the commun process, using the mapping table     
    nl = []
    new_l = []
    if "c̣h" in utterance:
        utterance = re.sub("c̣h", mapping_table["c̣h"], utterance)
    for character in mapping_table: # we go through the list of characters
        if character in ignore_in_first_pass:
            continue
        if re.search(character, utterance):
            utterance = re.sub(character, mapping_table[character], utterance) # if we match the character/sequence of characters in the line : we replace it with the corresponding pronunciation 
            nl.append(utterance) # this new list contains every step (every replacement) for one word/expression 
    ### just below : rule for the "y" character (1)
    if re.search("y|ʏ", utterance):
        utterance = re.sub("y|ʏ", "#", utterance) # we do this in order to avoid the next rule, we will replace with the good symbol later
    
    ### just below : rule for the "j" --> becomes "x" except in the end of a syllable  in this context : Vowel+i+j --> Vj
    r1 = re.search("(.*[^aeoiɨãõ\+@ə=\$][aeoiɨãõ\+@ə=\$])(j|ᴊ)([^aeoiɨãõ\+@ə=\$].*)", utterance)
    if r1:
        j1 = r1.group(2)
        j1 = re.sub("j|ᴊ", "h", j1)
        utterance = r1.group(1) + j1 + r1.group(3)
        nl.append(utterance)
    r2 = re.search("(.*[^aeoiɨãõ\+@ə=\$][aeoiɨãõ\+@ə=\$])(j|ᴊ)($)", utterance)
    if r2:
        j2 = r2.group(2)
        j2 = re.sub("j|ᴊ", "h", j2)
        utterance = r2.group(1) + j2 + r2.group(3)
        nl.append(utterance)
    r3 = re.search("(.*[aeoiɨãõ\+@ə=\$])(ij|iᴊ)([^aeoiɨãõ\+@ə=\$].*)", utterance)
    if r3:
        j3 = r3.group(2) 
        j3 = re.sub("ij|iᴊ", "ih", j3)
        utterance = r3.group(1) + j3 + r3.group(3)
        nl.append(utterance)
    r4 = re.search("(.*[aeoiɨãõ\+@ə=\$])(ij|iᴊ)($)", utterance)
    if r4:
        j4 = r4.group(2)
        j4 = re.sub("ij|iᴊ","ih",j4)
        utterance = r4.group(1) + j4 + r4.group(3)
        nl.append(utterance)
    r5 = re.search("(^)(j|ᴊ)([aeoiɨãõ\+@ə=\$])(.*)", utterance)
    if r5:
        j5 = r5.group(2)
        j5 = re.sub("j|ᴊ", "h", j5)
        utterance = r5.group(1) + j5 + r5.group(3) + r5.group(4)
        nl.append(utterance)
    r6 = re.search("(.*)(j|ᴊ)([aeoiɨãõ\+@ə=\$])(.*)", utterance)   
    if r6:
        j6 = r6.group(2)
        j6 = re.sub("j|ᴊ", "h", j6)
        utterance = r6.group(1) + j6 + r6.group(3) + r6.group(4)
        nl.append(utterance)
        
    ### rule for the "y" character (2)
    if re.search("#", utterance):
        # utterance = re.sub("#", "j", utterance)
        utterance = re.sub("#", "j", utterance)
        nl.append(utterance)
        
    ### just below : rule for the nasalized vowels --> if the first vowel of a word is nasalized, the others too
    ### EXCEPT if there is an oral stop : nasalization spreads left to right but is blocked by the first oral stop (ie all stops, affricate, etc 
    ### except for nasal stops m n -- and ʔ probably doesn't block it either)
    v = []
    for character in utterance:
        if character in vowels: # we want to find the vowels of the word in order to see if it is a nasal one
            v.append(character) # we put these vowels in a list
            if v[0] in nasal_vowels and spread: # if the first element of the list is a nasal vowel (what we are looking for...) --> replacements
                r1 = re.match("([^g|p|b|t|d|k]*?)(g|p|b|t|d|k)(.*)", utterance) # searching for oral stops
                if r1:
                    before_oral_stop = r1.group(1)
                    oral_stop = r1.group(2)
                    after_oral_stop = r1.group(3)
                    before_oral_stop = re.sub("a", "ã", before_oral_stop)
                    before_oral_stop = re.sub("o", "õ", before_oral_stop)
                    before_oral_stop = re.sub("i", "ĩ", before_oral_stop)
                    before_oral_stop = re.sub("e", "ẽ", before_oral_stop)
                    before_oral_stop = re.sub("ə", "ə͂", before_oral_stop)
                    before_oral_stop = re.sub("ɨ", "ɨ̃", before_oral_stop)
                    nl.append(before_oral_stop + oral_stop + after_oral_stop)
                r3 = re.match("(^)(g|p|b|t|d|k)([^g|p|b|t|d|k]*)(g|p|b|t|d|k)(.*)", utterance)
                if r3:
                    begin1 = r3.group(1)
                    begin2 = r3.group(2)
                    rep = r3.group(3)
                    oral_stop = r3.group(4)
                    end = r3.group(5)
                    rep = re.sub("a", "ã", rep)
                    rep = re.sub("o", "õ", rep)
                    rep = re.sub("i", "ĩ", rep)
                    rep = re.sub("e", "ẽ", rep)
                    rep = re.sub("ə", "ə͂", rep)
                    rep = re.sub("ɨ", "ɨ̃", rep)
                    nl.append(begin1 + begin2 + rep + oral_stop + end)
                    
                r2 = re.match("(^)(g|p|b|t|d|k)([^g|p|b|t|d|k]*)($)", utterance)
                if r2:
                    begin = r2.group(1)
                    oral_stop = r2.group(2)
                    rep = r2.group(3)
                    end = r2.group(4)
                    rep = re.sub("a", "ã", rep)
                    rep = re.sub("o", "õ", rep)
                    rep = re.sub("i", "ĩ", rep)
                    rep = re.sub("e", "ẽ", rep)
                    rep = re.sub("ə", "ə͂", rep)
                    rep = re.sub("ɨ", "ɨ̃", rep)
                    nl.append(begin + oral_stop + rep + end)
                
                r4 = re.match("(^)([^g|p|b|t|d|k]*)($)", utterance)
                if r4:
                    begin = r4.group(1)
                    rep = r4.group(2)
                    end = r4.group(3)
                    rep = re.sub("a", "ã", rep)
                    rep = re.sub("o", "õ", rep)
                    rep = re.sub("i", "ĩ", rep)
                    rep = re.sub("e", "ẽ", rep)
                    rep = re.sub("ə", "ə͂", rep)
                    rep = re.sub("ɨ", "ɨ̃", rep)
                    nl.append(begin + rep + end)
            else:
                nl.append(utterance)

    if not nl:
        return ''
    ### results...      
    # new_a=str(nl[-1:])[2:-2] # we only keep the last step for a word (the form with all the replacements done); and we remove the parentheses and quotation marks
    new_l = nl[-1]
    ### replacement of = --> ə͂
    if re.search("=",new_l):
        new_l = re.sub("=","ə͂",new_l)
        
    ### replacement of + --> ɨ̃
    if re.search("\+",new_l):
        new_l = re.sub("\+","ɨ̃",new_l)
        
    ### replacement of $ --> ĩ 
    if re.search("\$",new_l):
        new_l = re.sub("\$","ĩ",new_l)

    ### replacement of @ --> ẽ
    if re.search("@",new_l):
        new_l = re.sub("@","ẽ",new_l)
    
    return unicodedata.normalize("NFC", new_l)

def post_process(phonemized: str):
    # phonemized = re.sub("\ꞌ", " ʔ ", phonemized)
    phonemized = re.sub("ɨ ̃", "ɨ̃", phonemized)
    # phonemized = re.sub("ɨ ̃́", " ɨ̃ ", phonemized)
    # phonemized = re.sub("ĩ́", " ɨ̃ ", phonemized)
    # phonemized = re.sub("õ ́", " õ ", phonemized)
    # phonemized = re.sub("ã ́", " õ ", phonemized)
    # phonemized = re.sub("k ̣", " k ", phonemized)
    # phonemized = re.sub("ɨ̃ ́", "ɨ̃", phonemized)
    phonemized = re.sub(" ʰ", "ʰ", phonemized)
    phonemized = re.sub(" ʲ", "ʲ", phonemized)
    phonemized = re.sub("ə ͂", "ə͂", phonemized)
    phonemized = re.sub("ẽĩ", "ẽ ĩ", phonemized)
    phonemized = re.sub("ĩĩ", "ĩ ĩ", phonemized)
    # phonemized = re.sub("ã ̈", "ã", phonemized)
    phonemized = re.sub("t ʃ", "tʃ", phonemized)
    phonemized = re.sub(" ʔ", "ʔ", phonemized)
    return unicodedata.normalize("NFC", phonemized)

def tokenize_phones(word, phones):
    return re.split(rf"({'|'.join(phones)})", word)


def phonemize_folder(folder: Path, mapping_table: dict, output_folder: Path) -> None:
    """Phonemize all utterances in a given folder"""
    for transcription_file in folder.glob("*.transcription"):
        transcription = next(open(transcription_file))
        transcription = transcription.strip()
        phonemized = phonemize(mapping_table, transcription)
        phonemized = phonemized.strip()
        with open(output_folder / f"{transcription_file.stem}.phonemized", "w") as output_file:
            output_file.write(f"{transcription}\t{phonemized}\n")

def phonemize_file(input_file: str, mapping_table: dict, phones: list, output_folder: Path):
    path_name = Path(input_file).stem
    ignored = 0
    with open(input_file, "r") as opened_file:
        with open(output_folder / f"{path_name}.dict", "w") as output_file:
            for line in opened_file:
                line = line.strip()
                phonemized = phonemize(mapping_table, line)
                phonemized_no_spread = phonemize(mapping_table, line, False)
                tokenized = " ".join(tokenize_phones(phonemized, phones)) # " ".join(features_table.segs_safe(phonemized))
                tokenized_no_spread = " ".join(tokenize_phones(phonemized_no_spread, phones))
                tokenized, tokenized_no_spread = re.sub(r" +", " ", tokenized), re.sub(r" +", " ", tokenized_no_spread)
                tokenized, tokenized_no_spread = post_process(tokenized), post_process(tokenized_no_spread)
                tokenized, tokenized_no_spread = tokenized.strip(), tokenized_no_spread.strip()
                if not tokenized or not tokenized_no_spread:
                    continue
                if phonemized != re.sub(r" ", "", tokenized):
                    ignored += 1
                tokenized, tokenized_no_spread = re.sub("t ʃ", "tʃ", tokenized), re.sub("t ʃ", "tʃ", tokenized_no_spread)
                if tokenized != tokenized_no_spread:
                    output_file.write(f"{line}\t{tokenized_no_spread}\n")
                output_file.write(f"{line}\t{tokenized}\n")
            print(f"{ignored} tokenize words that not really match the untokenized counterpart.")

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input",
                        help="The folder/file containing utterance files to phonemuze.\
                              One utterance per file/line.",
                        required=True)
    parser.add_argument("-m", "--mapping_table",
                        help="The dictionnary associating each grapheme to a phoneme.",
                        required=True)
    parser.add_argument("-p", "--phones",
                        help="The set of phones of Tsimane.",
                        required=True)
    parser.add_argument("-o", "--output_folder",
                        help="Where the phonemized utterances will be stored.",
                        required=True)
    args = parser.parse_args()
    output_folder = Path(args.output_folder)
    output_folder.mkdir(exist_ok=True, parents=True)

    mapping_table = mapping_table_file_to_dictionnary(args.mapping_table)
    with open(args.phones) as phones_file:
        phones = [phone.strip() for phone in phones_file]
        print(phones)
    if os.path.isdir(args.input):
        phonemize_folder(Path(args.input), mapping_table, output_folder)
    else:
        phonemize_file(args.input, mapping_table, phones, output_folder)

if __name__ == "__main__":
    main()
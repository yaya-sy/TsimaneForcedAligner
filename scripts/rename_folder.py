from warnings import warn
from pathlib import Path
import re
from argparse import ArgumentParser

def rename_folder(audio_folder: Path, format="mp3") -> None:
    """
    Rename the file of a given folder into a\
    LANGUAGE_CHAPTER-NUMBER_CHAPTER-NAME scheme.
    """
    for a_file in audio_folder.glob(f"*.{format}"):
        filename = a_file.stem
        filename = re.sub("_+", "_", filename)
        parts = filename.split("_")
        len_parts = len(parts)
        if len_parts == 5:
            chapter_number, chapter_name = parts[1], parts[3]
        elif len_parts == 4:
            chapter_number, chapter_name = parts[1], parts[2]
        else:
            warn(f"The filename {filename} has an unexpected scheme.")
        chapter_name = chapter_name[:3].upper()
        output_filename = f"CAS_{chapter_number}_{chapter_name}.{format}"
        a_file.rename(a_file.parent / output_filename)

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input_folder", help="The folder to rename.")
    parser.add_argument("-f", "--format", help="The extension of the files to rename.")

    args = parser.parse_args()
    rename_folder(Path(args.input_folder), args.format)

if __name__ == "__main__":
    main()
# TsimaneForcedAligner
A forced aligner for Tsimane language. This repository contains also many interesting things for tsimane, such as a _phonemizer_, _phonetic dictionary_, etc. and can be used for other purposes.

## Working environment

Clone this github repository:
```bash
git clone https://github.com/yaya-sy/FulaSpeechCorpora.git
```

and move to it:

```bash
cd TsimaneForcedAligner
```

You can create the conda environment if you want to donwnload the bible corpus:

```bash
conda env create -f environment.yml
```

and activate it:

```bash
conda activate tsimane-scraper
```

## Aligning the bible corpus

We release a file containing audio timemarks for each verse of the bible corpus. It's a tab-separated file:
```
filename    verse_line_id   onset   offset
```

The lines with `onset = offset = 0.0` are unaligned verses, you can ignore them.

You can donwload the bible corpus using the script `scripts/download_bible.py`, as:

```bash
python scripts/download_bible.py --page live.bible.is/bible/CASNTM/MRK/1 --output-directory data
```

Note that the source code of the web page or the links may change, so this scraper may become obsolete.

## Align your own corpus

To align a corpus you need:

- a _speech corpus_: folder containing your audios and their corresponding texts (they must have the same filenames).
- a _acoustic model_: We release a pretrained acoustic model for aligning a new corpus. This model is pretrained on the bible corpus and is located in `models/all_non_merged_glottal.zip`
- a _phonetic dictionary_: it's a vocabulary of the language mapping each word to its phonetic realization. You can find a _phonetic dictionary_ created with the bible corpus of Tsimane in `data/vocabularies/bible_vocabulary.dict`. But you can also phonemize your own vocabulary using this script: `scripts/phonemizer.py`

To align your speech corpus, you will need to install the [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/installation.html "Installation instruction for Montreal Forced Aligner").

After installation, you can align your corpus:
```bash
mfa align <your-speech-corpus> <your-phonetic-dictionary> models/tsimane_acoustic_model.zip  <output-folder> --clean --overwrite --temp_directory aligners/wnh_tsimane --num_jobs 1
```

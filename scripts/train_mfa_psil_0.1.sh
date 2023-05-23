#!/bin/bash
#SBATCH --cpus-per-task=14
#SBATCH --partition=all
#SBATCH --job-name=mfa_psil_0.1             # Job name
#SBATCH --time=48:00:00                         # Time limit hrs:min:sec
#SBATCH --output=%x-%j.log                    # Standard output and error log

echo "Running job on $(hostname)"

# load conda environment
source /shared/apps/anaconda3/etc/profile.d/conda.sh
conda activate aligner

# launch your computation
# mfa train --clean --overwrite ../DATA/BIBLE/Tsimane/speech_corpus/ outputs/vocabularies/bible_vocabulary.dict models/fula_acoustic_model.zip models/corpus_aligned -t mfa_logs --num_jobs 1 initial_beam 1000 --beam 10000 --retry-beam 40000 --config_path extra/mfa_config.yml
mfa train ../DATA/concatenated/ data/vocabularies/vocabulary.dict models/all_merged_glottal_concatenated.zip data/aligned/all_merged_glottal_concatenated --temp_directory mfa_logs/all_merged_glottal_concatenated --num_jobs 1 --beam 60 --retry-beam 120 --punctuation "?¿.:,;!" --silence_probability 0.1
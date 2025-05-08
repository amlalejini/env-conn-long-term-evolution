# Reviewer guide to the anonymized repository

👋 if you are a reviewer!

The software used for running our experiments are submodules (in `third-party`), which are not anonymized, and thus not included in the anonymized repository.
Of course, upon publication, the software will be easily accessible from GitHub (including specific commit hashes).

Once published, we will also aggregate relevant data analyses / documents into a web-accessible ebook built using bookdown (<https://bookdown.org/>), which will include a detailed table of contents that allow for quick navigation of supplemental figures, statistical results, etc.
For now, here's a rough guide to this repository's organization:

- `experiments` - In general, each directory corresponds to a separate experiment (or set of experiments) run, including all configuration and analysis files associated with them. Experiments are dated, so the most recently conducted experiments have the nearest dates.
  - The complete experiment files for the MABE2 experiments are in one of the submodules (not included in anonymized repo). However, the landscape files and R markdown used to generate plots for the paper are included in `experiments/mabe2-exps/`.
  - `2025-04-17-squished-lattice-longer` - Includes configuration files / analysis scripts for the lattice shape Avida experiments. See `analysis/plots` for all supplemental figures + tables that include full pairwise statistical results.
  - `2025-04-17-vary-structs` - Includes configuration files / analysis scripts for the varied graph Avida experiments. See `analysis/plots` for all supplemental figures + tables that include full pairwise statistical results.
  - `2025-04-avida-manuscript-fig` - Includes R markdown files used to generate the manuscript figure for the Avida experiments.
- `scripts` - Miscellaneous collection of scripts used for analyses, data management, etc.
- `third-party` - All "third-party" dependencies used, including repositories that contain experiment software (`avida-empirical`, `evo_spatial_discoveries`, and `MABE2`).
- `hpc-env` - Scripts that configure local module environments for high performance computing clusters used to conduct experiments.
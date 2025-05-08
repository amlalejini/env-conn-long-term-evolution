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

## "Frozen in time" dynamics in Avida

As mentioned in the manuscript, the default Avida configuration where digital organisms express their genomes at differential rates as determined by their merit caused degenerate "frozen in time" behavior in many spatial structures.
Specifically, on each update with the default configuration, each organism (on average) gets to execute 30 instructions.
The "on average" is key. The number of instructions an organism executes in their genome on any given update is a function of their merit.
That is, low-merit organisms will execute many fewer instructions than high-merit organisms, allowing high-merit organisms to quickly outcompete low-merit organisms (giving us "natural" selection!).

In sparsely connected / more constrained spatial structures with slow sweep times (i.e., structures where it takes a long time for lineages to "sweep" through environment), an organism in one region might evolve a new logic function, substantially increasing their merit relative to all other organisms in the environment.
As a result, the organism that gained a new function will be allotted many more instruction executions than other, lower-merit organisms.
This isn't a problem in relatively unconstrained environments (e.g., a square lattice or well-mixed environment), as the lineages of high-merit organisms can quickly take over the population, replacing all low-merit organisms and establishing more parity in merit across the population.

Having a prolonged period of large imbalance of merit values can cause degenerate behavior.
The organisms with high merit get allocated nearly all instruction executions each update, "freezing" low-merit regions in time.
Organisms can't self-replicate when they aren't given instruction executions, so there is little to no reproduction activity in low-merit regions when merit distribution is very skewed.
High merit regions have huge levels of reproductive activity because those organisms are getting even more instruction executions per update for a prolonged period of time.
If the high merit organisms don't replace low merit organisms, this imbalance persists for very long periods of time, exacerbating the problem because high merit organisms are the only ones reproducing (and thus evolving); so, there is no chance for low merit regions to "catch up".
I.e., this is a positive feedback loop.

We found that many spatial structures have bottleneck regions (sometimes many) that have low probabilities of offspring crossing the bottleneck.
So even though the high merit region might be producing many offspring overall, there is still a relatively low probability that a lineage finds its way to another region fast enough to sweep the low merit region while still be at merit parity with organisms in the region of its ancestors (as soon as a lineages merit falls behind, it might become frozen in time too).

We confirmed these dynamics by tracking birth counts per location, and indeed, in more constrained spatial structures, we observed very skewed distributions of birth counts across locations.
These data will be made available (and archived) in an OSF repository after the double blind review process.
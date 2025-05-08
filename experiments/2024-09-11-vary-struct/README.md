# 2024-09-11-vary-struct experiment

Initial exploratory experiment. Vary spatial structure:

- ...

TODO

- save mapping used from graph to locations in avida
- echo dynamic configuration variables

Directory guide:

- `config/` contains Avida configuration files (all of these files are copied into each run directory for each run)
- `spatial-structs` contains graph files for each spatial structure used in this experiment
  - These are not directly used by Avida. These files are used to generate Avida event files that configure the given spatial structure.
- `graphs.json` defines graphs to be generated for this experiment.
  - Note that we don't define well-mixed or toroidal lattice graphs in this way. Instead, we use Avida's built-in "well-mixed" and toroidal lattice options for those particular structures.
- `local-job-gen.sh` generates slurm files locally. Used for testing experiment setup locally. Not to be used on HPC.


Notes for next experiment:
- Level out rewards so that there are fewer weird effects of number of generations elapsed?
-
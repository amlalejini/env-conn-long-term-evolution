import polars as pl
from matplotlib import pyplot as plt
def main():
    df = pl.read_csv("./aggregate_data_out/aggregate.csv")

    #passed both evaulations (tasks && mostCPUSGenotype evolved)
    numDef9EvolvedBothEvals = df.filter(pl.col('treatment') == 'default_9' & pl.col('evolved_in_tasks') == 'True' & pl.col('evolved_in_mostCPUsGenotype') == 'True')
    numEQUOnlyEvolvedBothEvals = df.filter(pl.col('treatment') == 'EQU_Only' & pl.col('evolved_in_tasks') == 'True' & pl.col('evolved_in_mostCPUsGenotype') == 'True')

    numDef9EvolvedTasks = df.filter(pl.col('treatment') == 'default_9' & pl.col('evolved_in_tasks') == 'True')
    numDef9EvolovedMostCPUs = df.filter(pl.col('treatment') == 'default_9' & pl.col('evolved_in_mostCPUsGenotype') == 'True')

    numEQUOnlyEvolvedTasks = df.filter(pl.col('treatment') == 'EQU_only' & pl.col('evolved_in_tasks') == 'True')
    numEQUOnlyEvolovedMostCPUs = df.filter(pl.col('treatment') == 'EQU_only' & pl.col('evolved_in_mostCPUsGenotype') == 'True')


    plt.bar =(['Defualt9', 'EQU_Only'], [numDef9EvolvedBothEvals, numEQUOnlyEvolvedBothEvals])
    plt.title('Runs that Evolved EQU in both evaluations')
    plt.xlabel('treatments')
    plt.ylabel('Number of Runs EQU evolved')

    plt.show
if __name__ == "__main__":
    main()
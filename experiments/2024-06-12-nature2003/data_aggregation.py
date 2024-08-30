import argparse, os, sys, errno, subprocess, csv
run_identifier = "run_"

#number of EQU-performing-CPU's required to say the population "Evolved EQU"
threshold = 5

#This is functionally equivalent to the mkdir -p [fname] bash command

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def extract_params_cmd_log(path):
    content = None
    with open(path, "r") as fp:
        content = fp.read().strip()
    content = content.replace("./avida", "")
    params = [param.strip() for param in content.split("-set") if param.strip() != ""]
    cfg = {param.split(" ")[0]:param.split(" ")[1] for param in params}
    return cfg

def read_avida_dat_file(path, backfill_missing_fields=False):
    content = None
    with open(path, "r") as fp:
        content = fp.read().strip().split("\n")
    legend_start = 0
    legend_end = 0
    # Where does the legend table start?
    for line_i in range(0, len(content)):
        line = content[line_i].strip()
        if line == "# Legend:":         # Handles analyze mode detail files.
            legend_start = line_i + 1
            break
        if "#  1:" in line:             # Handles time.dat file.
            legend_start = line_i
            break
    # For each line in legend table, extract field
    fields = []
    for line_i in range(legend_start, len(content)):
        line = content[line_i].strip()
        if line == "":
            legend_end = line_i
            break
        # patch 3-input logic tasks because avida file format is nonsense
        if "Logic 3" in line:
            line = line.split("(")[0]

        fields.append( line.split(":")[-1].strip().lower().replace(" ", "_") )
    data = []
    for line_i in range(legend_end, len(content)):
        line = content[line_i].strip()
        if line == "": continue
        data_line = line.split(" ")
        if len(data_line) > len(fields):
            print("found more items than there are fields!")
            print(fields)
            print(data_line)
            exit(-1)
        elif backfill_missing_fields:
            num_backfill = len(fields) - len(data_line)
            for _ in range(num_backfill): data_line.append("")
        elif len(data_line) != len(fields):
            print("data fields mismatch!")
            print(fields)
            print(data_line)
            exit(-1)
        data.append({field:value for field,value in zip(fields, data_line)})
    return data


def main():
    print("main runs")
    parser = argparse.ArgumentParser(description="Run submission script.")
    parser.add_argument("--dump", type=str, help="Where to dump this?", default=".")
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    mkdir_p(dump_dir)

    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    summary_header = None
    summary_content_lines = []
    mostCPUsGenotype_evolvedEQU={}
    tasks_evolvedEQU ={}

    for run_dir in run_dirs:
        print("itterating run_dir: " + run_dir)
        run_path = os.path.join(data_dir, run_dir)
        # Skip over (but make note of) incomplete runs.
        if not os.path.exists(os.path.join(run_path, 'data')):
            print('Skipping: ', run_path)
            continue

        #######################################################################################
         # Extract detail_mostCPUsGenotype.dat data
        mostCPUsGenotype_data = read_avida_dat_file(os.path.join(run_path, "data", "detail_mostCPUsGenotype.dat"))
        ############print(mostCPUsGenotype_data)
        # Summery information
        # - average generation
        #summary_info["time_average_generation"] = [line["average_generation"] for line in time_data if int(line["update"]) == update][0]

        if(int(mostCPUsGenotype_data[0]["equals"]) > 0):
            mostCPUsGenotype_evolvedEQU[run_dir] = True
        else:
            mostCPUsGenotype_evolvedEQU[run_dir] = False

        #########################################################################################   


        ##########################################################################################
        
        #Extract details from tasks.dat
        tasks_data = read_avida_dat_file(os.path.join(run_path, "data", "tasks.dat"))
        #########print(tasks_data)
        #threshold = num of equ to have evolved 
        #sudo
        #if [equals] > threshold
            #tasks_evolved[run_dir] = true
        #else: false]

        #declare oldest population as first in dictionary (it wont be)
        oldestpop = int(tasks_data[0]['update'])
        #find oldest population (Should be 100,000 for this given study)
        for population in tasks_data:
            if int(population['update']) > oldestpop:
                    oldestpop = int(population['update'])
        #itterate all populations
        for population in tasks_data:
            #if the update is the oldest update
            if(int(population['update']) == int(oldestpop)):
                #if population computed n EQUs, can say run evolved EQU
                if(int(population["equals"]) > threshold):
                    tasks_evolvedEQU[run_dir] = True
                else:
                    tasks_evolvedEQU[run_dir] = False
    #run: [treatment,evolvedtasks, evolvedMostCPU]
    aggregateDict = {}
    #aggregateDict['fields'] = ['treatment','EQU_evolved_in_tasks', 'EQU_evolved_in_mostCPUsGenotype']
    for run in run_dirs:
        if 'run_10' in run:
            aggregateDict[run] = ['default_9', tasks_evolvedEQU[run], mostCPUsGenotype_evolvedEQU[run]]
        if 'run_11' in run:
            aggregateDict[run] = ['EQU_Only', tasks_evolvedEQU[run], mostCPUsGenotype_evolvedEQU[run]]
    
    for key, value in aggregateDict.items():
        print(f"{key}: {value}")
    with open('./aggregated_data_out/aggregate.csv', mode='w', newline='') as file:
        writer=csv.writer(file)
        writer.writerow(['run', 'treatment','EQU_evolved_in_tasks', 'EQU_evolved_in_mostCPUsGenotype'])
        for key, value in aggregateDict.items():
            writer.writerow([key] + value)
if __name__ == "__main__":
    main()
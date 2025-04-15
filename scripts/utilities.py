import csv
import errno
import os

def mkdir_p(path):
    """
    This is functionally equivalent to the mkdir -p [fname] bash command
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def read_csv(file_path):
    """
    Read content of csv file into a list where each entry in the list is a dictionary
    with header:value entries.
    """
    content = None
    with open(file_path, "r") as fp:
        content = fp.read().strip().split("\n")
    header = content[0].split(",")
    content = content[1:]
    lines = [
        {header[i]: l[i] for i in range(len(header))}
        for l in csv.reader(
            content,
            quotechar='"',
            delimiter=',',
            quoting=csv.QUOTE_ALL,
            skipinitialspace=True
        )
    ]
    return lines

def write_csv(output_path:str, rows:list):
    header = list(rows[0].keys())
    header.sort()
    lines = [ ",".join([str(row[field]) for field in header]) for row in rows ]
    with open(output_path, "w") as fp:
        fp.write(",".join(header) + "\n")
        fp.write("\n".join(lines))

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

def read_avida_task_grid(filename, num_tasks=77):
    '''
    Reads avida task grid file.
    Returns two-dimentional
    '''
    lines = []
    with open(filename, "r") as fp:
        content = fp.read().strip()
        lines = [list(map(int, line.strip().split(" "))) for line in content.split("\n")]
    grid_info = {}
    id = 0
    for y in range(len(lines)):
        line = lines[y]
        for x in range(len(line)):
            task_value = line[x]
            task_profile = ''.join(
                reversed(
                    [str((task_value >> i) & 1) for i in range(num_tasks)]
                )
            )
            grid_info[id] = {
                "loc_x": x,
                "loc_y": y,
                "loc_id": id,
                "tasks_int": task_value,
                "task_profile": task_profile
            }
            id += 1
    return grid_info

def filter_time_points(all_points, method, resolution):
    if method == "total":
        return filter_time_points_total(all_points, resolution)
    elif method == "interval":
        return filter_time_points_interval(all_points, resolution)
    else:
        return None

def filter_time_points_total(all_points, total):
    '''
    Given a sequence of points,
    sort points and sample 'total' amount of them, evenly distributed.
    '''
    sorted_points = sorted(all_points)
    ids = { i * ((len(all_points) - 1) // (total - 1)) for i in range(total)}

    ids = sorted(list(ids))
    # If last id isn't final index, make it so.
    if ids[-1] != (len(sorted_points) - 1):
        ids[-1] = len(sorted_points) - 1

    return [sorted_points[idx] for idx in ids]

def filter_time_points_interval(all_points, interval, guarantee_final_point=True):
    '''
    Given a sequence of points, sample sorted sequence at given interval.
    Guarant
    '''
    sorted_points = sorted(all_points)
    return [
        sorted_points[i] for i in range(len(sorted_points))
        if (i == 0) or (not (i % interval)) or (guarantee_final_point and (i == (len(sorted_points) - 1)))
    ]

def get_tasks_from_environment_file(file_path):
    content = None
    with open(file_path, "r") as fp:
        content = fp.read().strip().split("\n")
    # REACTION  NOT  not   process:value=1.0:type=pow  requisite:max_count=1
    reaction_lines = [line for line in content if line.startswith("REACTION")]
    task_names = []
    for line in reaction_lines:
        split_line = [word for word in line.split(" ") if word != ""]
        task_names.append(split_line[2])
    return task_names
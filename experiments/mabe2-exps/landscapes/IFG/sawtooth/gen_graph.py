import sys

if len(sys.argv) != 5:
    print('Error! Expected exactly five arguments:')
    print('  1) The reward for each discovery')
    print('  2) The number of mutations to each discovery')
    print('  3) The fitness change per mutation')
    print('  4) The number of potential discoveries')
    quit()

discovery_reward = float(sys.argv[1])
muts_to_discovery = int(sys.argv[2])
change_per_mut = float(sys.argv[3])
potential_discoveries = int(sys.argv[4])

fname = 'graph__'
fname += f'reward_{str(discovery_reward).replace(".", "_")}__'
fname += f'muts_{muts_to_discovery}__'
fname += f'change_{str(change_per_mut).replace(".", "_")}__'
fname += f'discoveries_{potential_discoveries}.txt'
with open(fname, 'w') as fp:
    cur_fitness = 1
    prev_name = 'start'
    fp.write(f'add, {prev_name}, {cur_fitness}\n')
    fp.write('\n')
    for discovery_id in range(1, potential_discoveries + 1):
        discovery_name = 'M' + str(discovery_id)
        discovery_fitness = cur_fitness * discovery_reward
        for step_id in range(1, muts_to_discovery - 1):
            step_name = f'P{discovery_id}_{step_id}'
            cur_fitness = (1 + change_per_mut) * cur_fitness
            fp.write(f'add, {step_name}, {cur_fitness:.4f}\n')
            fp.write(f'connect, {prev_name}, {step_name}, 0\n')
            prev_name = step_name
        fp.write(f'add, {discovery_name}, {discovery_fitness:.4f}\n')
        fp.write(f'connect, {prev_name}, {discovery_name}, 0\n')
        fp.write('\n')
        cur_fitness = discovery_fitness
        prev_name = discovery_name




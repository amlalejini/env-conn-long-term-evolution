
num_paths = 100
max_fitness = 5
start_fitness = 1
fitness_step = (max_fitness - start_fitness) / num_paths

print(f'add, start, {start_fitness}')
for i in range(1, num_paths + 1):
    fitness = start_fitness + fitness_step * i
    fitness = round(fitness, 2)
    print(f'add, P{i}, {fitness}')
    print(f'connect, start, P{i}, {i - 1}')


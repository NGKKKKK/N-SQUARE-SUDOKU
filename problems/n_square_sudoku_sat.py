import os, time, csv
from pysat.solvers import Solver
from amo import pairwise_amo, bitwise_amo, commander_amo, sequential_amo, product_amo

# Solve sudoku grid n² x n²
def solve_sudoku(grid: list, n: int, type_amo, name_solver: str) -> dict | None:
    # Initialization
    size = n*n
    clauses = []
    current_id = size*size*size
    def get_id(x: int, y: int, value: int) -> int:
        return x*size*size + y*size + value
    literals = set(get_id(i, j, value) for i in range(size) for j in range(size) for value in range(1, size+1))
    def add_exactly_one(literals_: list) -> None:
        nonlocal current_id
        clauses.append(literals_) # ALO
        cl, au, current_id = type_amo.encode(literals_, current_id)
        clauses.extend(cl)

    # Cell constraint
    for r in range(size):
        for c in range(size):
            add_exactly_one([get_id(r, c, value) for value in range(1, size+1)])

    # Column constraint
    for c in range(size):
        for value in range(1, size+1):
            add_exactly_one([get_id(r, c, value) for r in range(size)])

    # Row constraint
    for r in range(size):
        for value in range(1, size+1):
            add_exactly_one([get_id(r, c, value) for c in range(size)])

    # Subgrid constraint (n x n)
    for sr in range(n):
        for sc in range(n):
            for value in range(1, size+1):
                lits = []
                for offset_r in range(n):
                    for offset_c in range(n):
                        r = sr*n + offset_r
                        c = sc*n + offset_c
                        lits.append(get_id(r, c, value))
                add_exactly_one(lits)

    # For some pre-numbered cells
    for r in range(size):
        for c in range(size):
            value = grid[r][c]
            if value != 0:
                clauses.append([get_id(r, c, value)])

    # Solve
    result = 'SAT'
    st = {}
    # print(f'Type of AMO: {name_amo}')
    solver = Solver(name=name_solver)
    try:
        for c in clauses:
            solver.add_clause(c)
        st['num_clauses'] = len(clauses)
        st['num_aux_vars'] = current_id - size**3

        t_solve_start = time.perf_counter()
        sat = solver.solve()
        t_solve_end = time.perf_counter()
        solve_time = t_solve_end - t_solve_start
        # print(f'Solving time: {(solve_time*1000):.4f}ms')
        st['solving_time_ms'] = round(solve_time*1000,4)

        if sat:
            model = set(solver.get_model())
            # print(f'Number of clauses: {len(clauses)}')
            # print(f'Number of auxiliary variables: {current_id - size**3}')
            # st['stats'] = solver.accum_stats()
            # print(f'Stats: {stats}')
            # result = [(x if x in model else -x) for x in literals]
            # print(f'Solution with main literals: {result}')
            # Board Visualization
            # for r in range(size):
            #    for c in range(size):
            #        for value in range(1, size+1):
            #            if get_id(r, c, value) in model:
            #                print(value, end = ' ' if c < size-1 else '\n')
            #                break
        else:
            result = 'UNSAT'
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if solver is not None:
            solver.delete()
    st['result'] = result
    return st

def read_sudoku_data(data_folder: str, filename: str) -> tuple:
    filepath = os.path.join("..", "data", data_foler, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    n = int(lines[0])
    size = n * n
    grid = [[int(val) for val in line.split()] for line in lines[1:size+1]]
    return grid, n

# For S-dataset
schemes_solo = [('pairwise', pairwise_amo),
               ('bitwise', bitwise_amo),
               ('commander', commander_amo),
               ('sequential', sequential_amo),
               ('product', product_amo)]

solvers_solo = ['cadical195', 'glucose4', 'minisat22',
           'mergesat3', 'maplecm']

# For M-dataset
schemes_fight = [('product', product_amo)]

solvers_fight = ['cadical195', 'minisat22']

# For L-dataset
schemes_final = [('commander', commander_amo),
                     ('sequential', sequential_amo),
                     ('product', product_amo)]

solvers_final = ['cadical195']

def write_sudoku_stat(data_folder: str, filename: str, solvers: list, amo_schemes: list) -> None:
    fieldnames = ['test_id', 'grid_size', 'n',
                  'amo_scheme', 'solver_name', 'num_vars', 'num_aux_vars',
                  'num_clauses', 'result', 'solving_time_ms']

    filepath = os.path.join("..", "data", filename)
    data_dir = os.path.join("..", "data", data_folder)
    all_files = sorted(f for f in os.listdir(data_dir) if f.endswith('.txt'))

    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()

        puzzle_id, stage = (0, 0)
        for fname in all_files:
            grid, n= read_sudoku_data(data_folder, fname)
            puzzle_id += 1
            stage = 0
            for name_amo, type_amo in amo_schemes:
                stage += 1
                for solver_name in solvers:
                    try:
                        row = solve_sudoku(grid, n, type_amo, solver_name)
                        writer.writerow({'test_id': f'{puzzle_id}.{stage}',
                                         'grid_size': f'{n * n}x{n * n}',
                                         'n': n,
                                         'amo_scheme': name_amo,
                                         'solver_name': solver_name,
                                         'num_vars': n ** 6,
                                         'num_aux_vars': row['num_aux_vars'],
                                         'num_clauses': row['num_clauses'],
                                         'result': row['result'],
                                         'solving_time_ms': row['solving_time_ms']})
                        f.flush()
                    except Exception as e:
                        print(f"Error at file: {fname} with {solver_name}: {e}")

if __name__ == "__main__":
    # solo = 'n_square_sudoku_data/S'
    # write_sudoku_stat(solo, 'result.csv', solvers_solo, schemes_solo)
    #
    # fight = 'n_square_sudoku_data/M'
    # write_sudoku_stat(fight, 'result_fight.csv', solvers_fight, schemes_fight)

    final = 'n_square_sudoku_data/L'
    write_sudoku_stat(final, 'result_final.csv', solvers_final, schemes_final)
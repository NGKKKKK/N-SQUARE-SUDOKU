import os
import time
import csv
from typing import List

from docplex.mp.model import Model as MipModel
from docplex.cp.model import CpoModel
from ortools.sat.python import cp_model
import gurobipy as gp
from gurobipy import GRB

def solve_cplex_mip(grid: list, n: int) -> dict:
    size = n * n
    model = MipModel(name="Sudoku_MIP")

    x = {(r, c, v): model.binary_var(name=f'x_{r}_{c}_{v}')
         for r in range(size) for c in range(size) for v in range(1, size + 1)}

    for r in range(size):
        for c in range(size):
            model.add_constraint(model.sum(x[r, c, v] for v in range(1, size + 1)) == 1)
            if grid[r][c] != 0:
                model.add_constraint(x[r, c, grid[r][c]] == 1)

    for i in range(size):
        for v in range(1, size + 1):
            model.add_constraint(model.sum(x[i, j, v] for j in range(size)) == 1)
            model.add_constraint(model.sum(x[j, i, v] for j in range(size)) == 1)

    for sr in range(n):
        for sc in range(n):
            for v in range(1, size + 1):
                model.add_constraint(
                    model.sum(x[sr * n + i, sc * n + j, v]
                              for i in range(n) for j in range(n)) == 1
                )

    t_start = time.perf_counter()
    sol = model.solve(log_output=False)
    t_end = time.perf_counter()

    return {
        'result': 'SAT' if sol else 'UNSAT',
        'solving_time_ms': round((t_end - t_start) * 1000, 4),
        'num_vars': size ** 3
    }

def solve_cplex_cp(grid: list, n: int) -> dict:
    size = n * n
    model = CpoModel(name="Sudoku_CP")

    x = {(r, c): model.integer_var(min=1, max=size, name=f'x_{r}_{c}')
         for r in range(size) for c in range(size)}

    for r in range(size):
        for c in range(size):
            if grid[r][c] != 0:
                model.add(x[r, c] == grid[r][c])

    for i in range(size):
        model.add(model.all_diff([x[i, j] for j in range(size)]))
        model.add(model.all_diff([x[j, i] for j in range(size)]))

    for sr in range(n):
        for sc in range(n):
            model.add(model.all_diff([x[sr * n + i, sc * n + j]
                                      for i in range(n) for j in range(n)]))

    t_start = time.perf_counter()
    sol = model.solve(TimeLimit=300, LogVerbosity='Quiet')
    t_end = time.perf_counter()

    return {
        'result': 'SAT' if sol else 'UNSAT',
        'solving_time_ms': round((t_end - t_start) * 1000, 4),
        'num_vars': size ** 2
    }

def solve_gurobi_mip(grid: list, n: int) -> dict:
    size = n * n
    env = gp.Env(empty=True)
    env.setParam('OutputFlag', 0)
    env.start()
    model = gp.Model("Sudoku_Gurobi", env=env)

    x = {(r, c, v): model.addVar(vtype=GRB.BINARY, name=f'x_{r}_{c}_{v}')
         for r in range(size) for c in range(size) for v in range(1, size + 1)}

    for r in range(size):
        for c in range(size):
            model.addConstr(gp.quicksum(x[r, c, v] for v in range(1, size + 1)) == 1)
            if grid[r][c] != 0:
                model.addConstr(x[r, c, grid[r][c]] == 1)

    for i in range(size):
        for v in range(1, size + 1):
            model.addConstr(gp.quicksum(x[i, j, v] for j in range(size)) == 1)
            model.addConstr(gp.quicksum(x[j, i, v] for j in range(size)) == 1)

    for sr in range(n):
        for sc in range(n):
            for v in range(1, size + 1):
                model.addConstr(
                    gp.quicksum(x[sr * n + i, sc * n + j, v]
                                for i in range(n) for j in range(n)) == 1
                )

    t_start = time.perf_counter()
    model.optimize()
    t_end = time.perf_counter()

    res = 'UNSAT'
    if model.Status == GRB.OPTIMAL:
        res = 'SAT'

    return {
        'result': res,
        'solving_time_ms': round((t_end - t_start) * 1000, 4),
        'num_vars': size ** 3
    }

def solve_ortools_cpsat(grid: list, n: int) -> dict:
    size = n * n
    model = cp_model.CpModel()

    x = {(r, c): model.NewIntVar(1, size, f'x_{r}_{c}')
         for r in range(size) for c in range(size)}

    for r in range(size):
        for c in range(size):
            if grid[r][c] != 0:
                model.Add(x[r, c] == grid[r][c])

    for i in range(size):
        model.AddAllDifferent([x[i, j] for j in range(size)])
        model.AddAllDifferent([x[j, i] for j in range(size)])

    for sr in range(n):
        for sc in range(n):
            model.AddAllDifferent([x[sr * n + i, sc * n + j]
                                   for i in range(n) for j in range(n)])

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = False

    t_start = time.perf_counter()
    status = solver.Solve(model)
    t_end = time.perf_counter()

    res = 'UNSAT'
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        res = 'SAT'

    return {
        'result': res,
        'solving_time_ms': round((t_end - t_start) * 1000, 4),
        'num_vars': size ** 2
    }

def read_sudoku_data(data_folder: str, filename: str) -> tuple:
    filepath = os.path.join("..", "data", data_folder, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    n = int(lines[0])
    size = n * n
    grid = [[int(val) for val in line.split()] for line in lines[1:size + 1]]
    return grid, n

# For M-dataset
solvers_fight = [('cplex_mip', solve_cplex_mip),
                 ('cplex_cp', solve_cplex_cp),
                 ('ortools_cpsat', solve_ortools_cpsat),
                 ('gurobi_mip', solve_gurobi_mip)]

# For L-dataset
solvers_final = [('ortools_cpsat', solve_ortools_cpsat)]

def write_sudoku_stat(data_folder: str, filename: str, solvers: list) -> None:
    fieldnames = ['test_id', 'grid_size', 'n', 'solver_name',
                  'num_vars', 'result', 'solving_time_ms']

    filepath = os.path.join("..", "data", filename)
    data_dir = os.path.join("..", "data", data_folder)
    all_files = sorted(f for f in os.listdir(data_dir) if f.endswith('.txt'))

    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if f.tell() == 0:
            writer.writeheader()

        board_id = 0
        for fname in all_files:
            grid, n= read_sudoku_data(data_folder, fname)
            board_id += 1
            solver_id = 0
            for solver_name, solver_func in solvers:
                solver_id += 1
                try:
                    row = solver_func(grid, n)
                    writer.writerow({'test_id': f'{board_id}.{solver_id}',
                                     'grid_size': f'{n * n}x{n * n}',
                                     'n': n,
                                     'solver_name': solver_name,
                                     'num_vars': row['num_vars'],
                                     'result': row['result'],
                                     'solving_time_ms': row['solving_time_ms']})
                    f.flush()
                except Exception as e:
                    print(f"Error at file {fname} with {solver_name}: {e}")


if __name__ == "__main__":
    # fight = 'n_square_sudoku_data/M'
    # write_sudoku_stat(fight, 'result_fight_2.csv', solvers_fight)

    final = 'n_square_sudoku_data/L'
    write_sudoku_stat(final, 'result_final_2.csv', solvers_final)


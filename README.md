# N-SQUARE-SUDOKU

Code and experimental results for the paper *SAT Encoding Approaches for Exact Sudoku Solving: A Comparison with ILP and CP Methods*.

Sudoku on an n² × n² grid is encoded as a SAT problem with five at-most-one (AMO) encodings (pairwise, bitwise, commander, sequential, product), solved through PySAT, and compared with ILP and CP solvers (Gurobi, CPLEX MIP, CPLEX CP, OR-Tools CP-SAT).

## Repository structure

| Folder / file     | Content                                                                |
|-------------------|------------------------------------------------------------------------|
| `amo/`            | AMO encodings and the Sudoku SAT solver                                |
| `data/`           | Benchmark puzzles (`n_square_sudoku_data/`) and raw result CSV files   |
| `problems/`       | Programme using SAT solver and other solvers (Gurobi, Cplex, OR-Tools) |
| `requirement.txt` | Neccessary libraries for running programme                             |

## Environment

Tested with Python 3.11.5 on Windows 11, inside a virtual environment.

```
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

## Data

Puzzles are plain text files, one per instance, with `0` for an empty cell.

| Group | Grid sizes | Instances per size | Used for |
|---|---|----------|---|
| S | 4x4, 9x9, 16x16, 25x25 | 50       | AMO ablation |
| M | 36x36, 49x49, 64x64 | 10       | SAT vs. ILP/CP |
| L | 81x81, 100x100 | 10       | Scalability |

Puzzle source:

| Group | Source |
|-------|---|
| S     | generated with the `py-sudoku` Python library |
| M + L | generated with the online Sudoku generator at <https://mocha2007.github.io/tools/sudoku.html> |

All generated puzzles are stored in `data/`, so the experiments can be reproduced without the library or the website.

## Usage

- Run all experiments (SAT part):

```
python -m problems.n_square_sudoku
```

Results are written as CSV to `data/`. Each row is one run (puzzle × AMO encoding × solver) with the columns:

`test_id, grid_size, n, amo_scheme, solver_name, num_vars, num_aux_vars, num_clauses, result, solving_time_ms`.

`solving_time_ms` is the wall-clock time of the solver alone (CNF generation excluded). No time limit was set for any solver.

- Run all experiments (SAT part):

```
python -m problems.n_square_sudoku_other
```

Results are written as CSV to `data/`. Each row is one run (puzzle × solver) with the columns:

`test_id, grid_size, n, solver_name, result, solving_time_ms`

`solving_time_ms` is the wall-clock time of the solver alone (Constraints generation excluded). No time limit was set for any solver.

## Summary of results

- Pairwise is fastest on 4x4 and 9x9, but its clause count grows quickly with the grid size.
- Product is the best encoding on the larger grids.
- SAT with the product encoding is faster than Gurobi, CPLEX MIP, CPLEX CP and OR-Tools CP-SAT on most grids; at 100x100, OR-Tools CP-SAT is faster.

## Author

Nguyen Duc Khiem - Faculty of Information Technology, VNU University of Engineering and Technology, Ha Noi, Viet Nam - nguyenkhiem1812.206@gmail.com.

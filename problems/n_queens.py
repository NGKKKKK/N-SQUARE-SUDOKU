from pysat.solvers import Solver
from amo import pairwise_amo, sequential_amo


# Solve n-queens problem
def solve_n_queens(board: list, n: int, type_amo, name_amo: str, name_solver: str) -> None:
    # Initialization
    clauses = []
    current_id = n * n
    def get_id(x: int, y: int) -> int:
        return x*n + y + 1
    literals = set(get_id(r, c) for r in range(n) for c in range(n))

    # Row constraint
    for r in range(n):
        row_literals = [get_id(r, c) for c in range(n)]
        clauses.append(row_literals) # ALO
        cl, au, current_id = type_amo.encode(row_literals, current_id)
        clauses.extend(cl)

    # Column constraint
    for c in range(n):
        column_literals = [get_id(r, c) for r in range(n)]
        cl, au, current_id = type_amo.encode(column_literals, current_id)
        clauses.extend(cl)

    # Diag constraint
    diag_size = 2*n - 1
    main_diags = [[] for i in range(diag_size)]
    sub_diags = [[] for i in range(diag_size)]
    for r in range(n):
        for c in range(n):
            m = r-c+(n-1)
            main_diags[m].append(get_id(r, c))
            s = r+c
            sub_diags[s].append(get_id(r, c))
    for e in main_diags:
        if len(e) > 1:
            cl, au, current_id = type_amo.encode(e, current_id)
            clauses.extend(cl)
    for e in sub_diags:
        if len(e) > 1:
            cl, au, current_id = type_amo.encode(e, current_id)
            clauses.extend(cl)

    # For some reserved cells
    for r in range(n):
        for c in range(n):
            value = board[r][c]
            if value != 0:
                clauses.append([get_id(r, c)])

    # Solve
    print(f'Type of AMO: {name_amo}')
    solver = Solver(name=name_solver)
    try:
        for c in clauses:
            solver.add_clause(c)
        if solver.solve():
            model = set(solver.get_model())
            result = [(x if x in model else -x) for x in literals]
            print(f'Solution with main literals: {result}')
            # Board Visualization
            for r in range(n):
                for c in range(n):
                    print(1 if get_id(r, c) in model else 0, end = ' ' if c < n-1 else '\n')
        else:
            print('No solution found!')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if solver is not None:
            solver.delete()
    print()

if __name__ == '__main__':
    n = 8
    board = [[0 for j in range(n)] for i in range(n)]
    board[0][0] = 1
    board[2][3] = 1
    print(board)
    solve_n_queens(board, n, sequential_amo, name_amo='Sequential', name_solver='glucose4')
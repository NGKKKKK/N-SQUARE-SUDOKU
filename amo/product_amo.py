from pysat.solvers import Solver
import math
from amo import pairwise_amo

def encode(literals: list, current_id: int = None) -> list:
    size = len(literals)
    if size <= 1:
        return [[], [], current_id if current_id is not None else 0]
    if current_id is None:
        current_id = max(literals) if size > 1 else 0
    column_size = math.ceil(math.sqrt(size))
    row_size = math.ceil(size/column_size)
    row_literals = [current_id + i for i in range(1, row_size+1)]
    column_literals = [current_id + row_size + i for i in range(1, column_size+1)]
    au_literals = row_literals + column_literals
    new_id = current_id + row_size + column_size
    clauses = []
    for i in range(size):
        r = i // column_size
        c = i % column_size
        clauses.append([-literals[i], row_literals[r]])
        clauses.append([-literals[i], column_literals[c]])
    clauses.extend(pairwise_amo.encode(row_literals)[0])
    clauses.extend(pairwise_amo.encode(column_literals)[0])
    return [clauses, au_literals, new_id]

def solve(model_name: str, literals: list) -> None:
    clauses, au_literals, new_id = encode(literals)
    print(f'Main literals: {literals} \nAuxiliary literals: {au_literals}\nClauses: {clauses}')
    solver = Solver(name=model_name)
    try:
        for c in clauses:
            solver.add_clause(c)
        if solver.solve():
            model = solver.get_model()
            print(f'Solution with auxiliary literals: {model}')
            result = [(x if x in model else -x) for x in literals]
            print(f'Solution with main literals: {result}')
        else:
            print('No solution found!')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if solver is not None:
            solver.delete()


if __name__ == '__main__':
    test = [1,2,3,4,5]
    solve('glucose4', test)
from pysat.solvers import Solver

def encode(literals: list, current_id: int = None) -> list:
    size = len(literals)
    if size <= 1:
        return [[], [], current_id if current_id is not None else 0]
    if current_id is None:
        current_id = max(literals)
    au_literals = [current_id + i for i in range(1, size)]
    new_id = current_id + size - 1
    clauses = []
    for i in range(size-1):
        clauses.append([-literals[i], au_literals[i]])
    for i in range(1, size-1):
        clauses.append([-au_literals[i-1], au_literals[i]])
    for i in range(1, size):
        clauses.append([-au_literals[i-1], -literals[i]])
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
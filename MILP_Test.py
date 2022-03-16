from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('SCIP')

infinity = solver.infinity()

x = solver.IntVar(0.0,infinity,'x')
y = solver.IntVar(0.0,infinity,'y')

solver.Add(x + 6 * y <= 15)
solver.Add(x <= 4 )

solver.Maximize(x + 8 * y)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
	print('Solution:')
	print('Objective value -', solver.Objective().Value())
	print('x - ', x.solution_value())
	print('y - ',y.solution_value())
else:
	print('Could not find an optimal solution')


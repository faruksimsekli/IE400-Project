"""
    @author Faruk Simsekli
    @date May 03, 2020
"""
# after you make some changes in the file, please edit above!
import sys
import copy
import xpress as xp

# In both solutions, we will use the variable names matrix for distances and W for waiting times
# after reading the Excel file, make sure that you set the variables right

# Parameters
# for testing purposes
# the costs between the locations i and j, i = 0, 1, ..., N, j = 0, 1, ..., N
matrix = [[0, 23, 15, 42, 30, 51],
          [23, 0, 34, 28, 35, 45],
          [15, 34, 0, 48, 62, 27],
          [42, 28, 48, 0, 21, 19],
          [30, 35, 62, 21, 0, 36],
          [51, 45, 27, 19, 36, 0]]

W = [35, 45, 20, 50, 65]

# randomly generated
# w_i : waiting time for student i , i = 1, 2, ..., N # name will be changed to W
w_i = [472, 316, 495, 349, 405, 315, 322, 443, 307, 364, 384, 405, 304,
       456, 327, 466, 349, 488, 479, 459, 450, 472, 429, 487, 447, 461,
       352, 471, 487, 328, 399, 317, 427, 399, 364, 337, 477, 300, 361,
       443, 471, 457, 488, 311, 474, 476, 454, 374, 424, 392, 310, 426,
       353, 327, 463, 476, 430, 474, 397, 433, 305, 349, 341, 383, 446,
       440, 456, 405, 430, 432, 330, 305, 348, 496, 386]

g = {}
p = []

'''
    Solution to TSP using Dynamic Programming
'''


def dynamic_tsp(N):
    N += 1
    for x in range(1, N):
        g[x + 1, ()] = matrix[x][0]

    optimal_solution = get_minimum(1, tuple(range(2, N + 1)))

    print('\nSolution with DP: {0, ', end='')
    solution = p.pop()
    print(solution[1][0] - 1, end=', ')
    for x in range(N - 2):
        for new_solution in p:
            if tuple(solution[1]) == new_solution[0]:
                solution = new_solution
                print(solution[1][0] - 1, end=', ')
                break
    print('0}')
    print("Optimal solution is ", optimal_solution)
    return


def get_minimum(k, a):
    if (k, a) in g:
        # Already calculated Set g[%d, (%s)]=%d' % (k, str(a), g[k, a]))
        return g[k, a]

    values = []
    all_min = []
    for j in a:
        set_a = copy.deepcopy(list(a))
        set_a.remove(j)
        all_min.append([j, tuple(set_a)])
        result = get_minimum(j, tuple(set_a))
        values.append(matrix[k - 1][j - 1] + W[j - 2] + result)

    # get minimum value from set as optimal solution for
    g[k, a] = min(values)
    p.append(((k, a), all_min[values.index(g[k, a])]))
    # print(values)
    return g[k, a]


'''
    Solution to TSP using Python interface of Xpress solver
'''


def solver_tsp_xpress(N):
    x = {}
    my_problem = xp.problem(name="TSP")
    N += 1

    # Xij decision variable
    for i in range(N):
        for j in range(N):
            x[i, j] = xp.var(name=f"X_{i}_{j}", vartype=xp.binary)
    my_problem.addVariable(x)

    # Ui auxiliary decision variable
    u = {}
    for i in range(N):
        u[i] = xp.var(name=f"U_{i}", vartype=xp.continuous)
    my_problem.addVariable(u)

    # [i]sum(x[i][j]) for all j = 1
    for i in range(N):
        my_problem.addConstraint(xp.Sum(x[i, j] for j in range(N)) == 1)

    # [j]sum(x[i][j]) for all i = 1
    for j in range(N):
        my_problem.addConstraint(xp.Sum(x[i, j] for i in range(N)) == 1)

    # [i]sum(x[i][j]) for all i = 0
    for i in range(N):
        my_problem.addConstraint(x[i, i] == 0)

    # sub-tour elimination
    for i in range(1, N):
        for j in range(1, N):
            if i != j:
                my_problem.addConstraint(u[i] - u[j] + (N - 1) * x[i, j] <= N - 2)

    # minimize [i, j]sum[x[i][j] * c[i][j]]
    obj = 0
    for i in range(N):
        for j in range(N):
            obj += matrix[i][j] * x[i, j]
        if i != 0:
            obj += W[i - 1]

    # Calculations
    my_problem.setObjective(obj, sense=xp.minimize)

    my_problem.solve()
    print("problem status:            ", my_problem.getProbStatus())
    print("problem status, explained: ", my_problem.getProbStatusString())
    sol = my_problem.getSolution()
    mov = []  # contains our X_i values
    for i in range(6):
        lst = []
        for j in range(6):
            lst.append(sol[6 * i + j])
        mov.append(lst)

    # printing the solution
    loc = 0
    print('\nSolution with IP: {', end='')
    for i in range(6):
        for j in range(6):
            if mov[loc][j] == 1:
                print(loc, end=", ")
                loc = j
                break

    print('0}')


if __name__ == '__main__':
    # solver_tsp_xpress(5)  # there are 5 students
    dynamic_tsp(5)  # there are 5 students
    sys.exit(0)

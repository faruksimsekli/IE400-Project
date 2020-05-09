"""
    @author Faruk Simsekli, Tarik Emin Kaplan, Gulnihal Muslu
    @date May 09, 2020
"""
# after you make some changes in the file, please edit above!
import sys
import copy
import math
import time
import xpress as xp
import pandas as pd
import numpy as np
from pandas import ExcelWriter
from pandas import ExcelFile

matrix = []  # will be read from excel file

W = []  # waiting times

g = {}
p = []

# m[i][j][k] i'th matrix, j'th row, k'th column
# (i.e. averaged travel time matrix for N = 5 student 1 to student 2 is m[0][0][1])
average_matrices = []


# generate the random matrices and take the average
def generate_random_matrices(N):
    num_of_matrices = math.floor(N * math.log(N))
    temp = np.zeros((N + 1, N + 1))  # N + 1 including professor
    for i in range(num_of_matrices):
        A = np.random.randint(low=100, high=300, size=(N + 1, N + 1))
        np.fill_diagonal(A, 0)  # Sets m[i][i] = 0
        A = (A + A.T) / 2
        temp = np.add(temp, A)
    temp = np.true_divide(temp, num_of_matrices)
    temp = temp.astype(int)
    average_matrices.append(temp)
    return


# Solution to TSP using Dynamic Programming
def dynamic_tsp(N):
    N += 1
    for x in range(1, N):
        g[x, ()] = matrix[x][0]  # from x no other students left, return to prof

    optimal_solution = get_minimum(0, tuple(range(1, N)))

    print('\nSolution with DP: {0, ', end='')
    solution = p.pop()

    print(solution[1][0], end=', ')
    for x in range(N - 1):
        for new_solution in p:
            if tuple(solution[1]) == new_solution[0]:
                solution = new_solution
                print(solution[1][0], end=', ')
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
        values.append(matrix[k][j] + W[j - 1] + result)

    # get minimum value from set as optimal solution for
    g[k, a] = min(values)
    p.append(((k, a), all_min[values.index(g[k, a])]))
    # print(values)
    return g[k, a]


# Solution to TSP using Python interface of Xpress solver
def solver_tsp_xpress(N):
    x = {}
    my_problem = xp.problem(name="TSP")
    N += 1

    # Xij decision variable
    for i in range(N):
        for j in range(N):
            x[i, j] = xp.var(name=f"X_{i}_{j}", vartype=xp.binary)
            my_problem.addVariable(x[i, j])

    # Ui auxiliary decision variable
    u = {}
    for i in range(N):
        u[i] = xp.var(name=f"U_{i}", vartype=xp.continuous)
        my_problem.addVariable(u[i])

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
    my_problem.fixglobals(1)
    my_problem.solve()
    # print("problem status:            ", my_problem.getProbStatus())
    # print("problem status, explained: ", my_problem.getProbStatusString())
    sol = my_problem.getSolution()

    mov = []  # contains our X_i values
    for i in range(N):
        lst = []
        for j in range(N):
            lst.append(sol[N * i + j])
        mov.append(lst)

    '''for i in range(N):
        for j in range(N):
            print(mov[i][j], end=" ")
        print()
    '''

    # printing the solution
    loc = 0
    print('\nSolution with IP: {', end='')
    for i in range(N):
        for j in range(N):
            if mov[loc][j] > 0.9:
                print(loc, end=", ")
                loc = j
                break

    print('0}')


def generateMatrixFromExcel(filename, sheetname):
    df = pd.read_excel(filename, sheetname)
    print("Column headings:")
    print(df.columns)

    mSize = len(df.columns) - 2  # subtract prof & waiting columns
    print("msize: ", mSize)

    # extracting W
    print(type(df["Waiting Time"]))
    waiting_times_temp = list(df["Waiting Time"])[:mSize - 1]
    waiting_times = []
    for i in waiting_times_temp:
        waiting_times.append(int(i))
    print(type(waiting_times))

    # extracting X_ij
    m = [[0 for j in range(mSize)] for i in range(mSize)]

    isProf = False
    for i in range(mSize):
        if i == 0:
            isProf = True
        for j in df.index:
            if isProf:
                if j == 0:
                    m[i][j] = 0
                else:
                    m[i][j] = df['Professor'][j]
            else:
                char = df['Student ' + str(i)][j]
                if isinstance(char, str):
                    m[i][j] = 0
                else:
                    m[i][j] = char
        isProf = False
    return m, waiting_times


if __name__ == '__main__':

    # part A for submission
    matrix, W = generateMatrixFromExcel("test.xlsx", "Sheet1")
    N = len(matrix) - 1
    solver_tsp_xpress(N)
    dynamic_tsp(N)

'''
    # Part B for testing of random matrices

    # randomly generated only once
    # w_i : waiting time for student i , i = 1, 2, ..., N # name will be changed to W
    W = [472, 316, 495, 349, 405, 315, 322, 443, 307, 364, 384, 405, 304,
         456, 327, 466, 349, 488, 479, 459, 450, 472, 429, 487, 447, 461,
         352, 471, 487, 328, 399, 317, 427, 399, 364, 337, 477, 300, 361,
         443, 471, 457, 488, 311, 474, 476, 454, 374, 424, 392, 310, 426,
         353, 327, 463, 476, 430, 474, 397, 433, 305, 349, 341, 383, 446,
         440, 456, 405, 430, 432, 330, 305, 348, 496, 386]
    
    N = 15
    for i in range(5, N + 1, 5):
        generate_random_matrices(i)

        matrix = average_matrices[int((i / 5) - 1)]

        print('====================MATRIX FOR N = ', i, '===========================')
        for i in range(len(matrix)):
            print("[", end="")
            for j in range(len(matrix[i])):
                print(matrix[i][j], end=", ")
            print("],")

        print('====================SOLVING IP FOR N = ', i, '===========================')
        start = time.time()
        solver_tsp_xpress(i)
        end = time.time()
        print('Elapsed Time:', end - start)

        print('====================SOLVING FOR DP N = ', i, '===========================')
        start = time.time()
        dynamic_tsp(i)
        end = time.time()
        g = {}
        p = []
        print('Elapsed Time:', end - start)

'''
sys.exit(0)

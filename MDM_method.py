import numpy as np
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

def generate_points(a, alpha, num_points, dim):
    return alpha * np.random.rand(num_points, dim) + a


def get_convex_hull_and_plot(points, dim):
    hull = ConvexHull(points)
    if dim == 2:
        plt.plot(points[:, 0], points[:, 1], 'o')
        for simplex in hull.simplices:
            plt.plot(points[simplex, 0], points[simplex, 1], 'b-')
        #plt.show()
    elif dim == 3:
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        plt.plot(points[:, 0], points[:, 1], points[:, 2], 'o')
        for simplex in hull.simplices:
            plt.plot(points[simplex, 0], points[simplex, 1], points[simplex, 2], 'b-')
        #plt.show()
    else:
        print('There is no way to plot graph in dim > 3, but hull is found successfully!')
    return hull


class MDM(object):
    __class__ = 'MDM'
    __doc__ = """
    This is an implementation the Mitchell-Demyanov-Malozemov method for 
    finding nearest to coordinates beginning point.
    Plots convex-hull and optimal solution in 2- and 3-dimensional cases.
    """

    def __init__(self, points, hull, dim):
        self._dim = dim
        self._points = points.copy()
        self._hull = hull
        self._A_matrix = points.copy().transpose()
        self.iterations = None
        self.delta_p = None
        self.p_vector = None
        self.vector_current = None
        self.supp_vector = None     # supp for vector p (i.e. {i \in 0 : dim - 1 | p[i] > 0} )

    def solve(self):
        delta_p = 1
        p_vector = [0 for i in range(0, len(self._points))]
        supp_vector = []
        t_param_vector =[]
        MIN_set = []
        MAX_set = []
        v_cycle_start = 0

        diff_vector = []    #for cycles finding
        cycle_constructed = False
        cycle_is_constructing = False
        cycle_current_size = 0          #we will search actual size of cycle

        iterations = 0
        initial_approximation = 1               # it can be changed for lowering iterations sake;
        # for first approximation we'll just take point from a board of hull - cause it's easy reduced
        vector_current = self._points[self._hull.vertices[initial_approximation]].copy()  #need copy() there for non-changing _points
        supp_vector.append(self._hull.vertices[initial_approximation])               # approximation => get vect_0
        p_vector[self._hull.vertices[initial_approximation]] = 1                    # working right concat
        # then we need to find vect_{k+1} iteratively

        while delta_p > 0.0000001 and iterations < 500 and len(supp_vector) != 0:
            if cycle_constructed is False:
                mult = np.dot(self._points[supp_vector], vector_current)
                ind_max = np.argmax(mult)     #finding max for indices in supp_vector
                ind_max = supp_vector[ind_max]      #finding max general in our mult product
                MAX_set.append(ind_max)

                mult = np.matmul(vector_current, self._A_matrix)
                ind_min = np.argmin(mult)                                                 # i''_k
                MIN_set.append(ind_min)

                diff = self._points[ind_max] - self._points[ind_min]
                print('Diff: ' + str(diff))
                delta_p = np.dot(diff, vector_current)

                if delta_p > 0.0000001:                  #if not bigger, then we've found a solution

                    print('\nDelta: ' + str(delta_p))
                    print('p_vector[ind_max] = ' + str(p_vector[ind_max]) + '\nnp.linalg.norm(diff)): '
                          + str(np.linalg.norm(diff)))
                    t_param = delta_p / (p_vector[ind_max] * (np.linalg.norm(diff)) ** 2)  # recounting all variables
                    if t_param >= 1:
                        t_param = 1


                    if iterations > 0 and cycle_is_constructing is False:         #constructing cycle(active finding cycle, i mean, active-active)
                        contains = np.where(np.all(diff_vector == diff, axis = 1))[0]
                        if len(contains) != 0:
                            cycle_is_constructing = True
                            v_cycle_start = vector_current.copy()
                            cycle_start = contains[0]           #index of first element of cycle; not changing
                            cycle_size = iterations - cycle_start           #not changing
                            cycle_current_size += 1
                        t_param_vector.append(t_param)
                        diff_vector.append(diff)
                    elif cycle_is_constructing is True and cycle_constructed is False:
                        if cycle_current_size < cycle_size and np.where(np.all(diff_vector == diff, axis = 1))[0] \
                                == (cycle_start + cycle_current_size):
                                    cycle_current_size += 1
                                    t_param_vector.append(t_param)
                                    diff_vector.append(diff)
                                    t_param_vector.append(t_param)
                        else:
                            cycle_constructed = True
                            print('CYCLE FOUND AND CONSTRUCTED SUCCESSFULLY!!!')
                            iterations = 500
                    elif iterations == 0:
                        t_param_vector.append(t_param)
                        diff_vector.append(diff)


                    vector_current -= t_param * p_vector[ind_max] * diff
                    #plt.plot(vector_current, 'r-')

                    supp_vector = []    # recounting
                    temp1 = t_param * p_vector[ind_max]
                    temp2 = (1 - t_param)
                    p_vector[ind_min] += temp1
                    p_vector[ind_max] *= temp2
                    for i in range(len(p_vector)):
                        if p_vector[i] > 0.0000001:
                            supp_vector.append(i)
                print('Vector current: ' + str(vector_current))
                iterations += 1
                print('Iterations: ' + str(iterations))
                print('Supp_vector: ' + str(supp_vector))

            # elif cycle_constructed is True:
            #     V = 0           #constructing V as linear combination of D's that we used previously
            #     for i in range(cycle_size):
            #         V += t_param_vector[i] * -diff_vector[cycle_start +i]
            #     vector_current = v_cycle_start
            #     lambda_t = -np.dot(vector_current, V)/np.linalg.norm(V)**2
            #     for i in range(cycle_size):
            #         if t_param_vector[i] > 0:
            #             if lambda_t > (1 - p_vector[MIN_set[i]])/t_param_vector[i]:
            #                 lambda_t = (1 - p_vector[MIN_set[i]])/t_param_vector[i]
            #         elif t_param_vector[i] < 0:
            #             if lambda_t > -p_vector[MAX_set[i]]/t_param_vector[i]:
            #                 lambda_t = -p_vector[MAX_set[i]]/t_param_vector[i]
            #     vector_current += lambda_t*V
            #     for i in range(cycle_size):
            #         p_vector[MAX_set[i]] -= lambda_t * t_param_vector[i]
            #         p_vector[MIN_set[i]] += lambda_t * t_param_vector[i]
            #
            #     iterations = 500
        if cycle_constructed is True:
            V = 0           #constructing V as linear combination of D's that we used previously
            for i in range(cycle_size):
                   V += -1* t_param_vector[cycle_start + i] * diff_vector[cycle_start +i]
            delta_p = 1
            p_vector = [0 for i in range(0, len(self._points))]
            supp_vector = []
            initial_approximation = 1  # it can be changed for lowering iterations sake;
            # for first approximation we'll just take point from a board of hull - cause it's easy reduced
            vector_current = self._points[
                self._hull.vertices[initial_approximation]].copy()  # need copy() there for non-changing _points
            supp_vector.append(self._hull.vertices[initial_approximation])  # approximation => get vect_0
            p_vector[self._hull.vertices[initial_approximation]] = 1  # working right concat
            for i in range(cycle_start):
                mult = np.dot(self._points[supp_vector], vector_current)
                ind_max = np.argmax(mult)  # finding max for indices in supp_vector
                ind_max = supp_vector[ind_max]  # finding max general in our mult product

                mult = np.matmul(vector_current, self._A_matrix)
                ind_min = np.argmin(mult)  # i''_k

                diff = self._points[ind_max] - self._points[ind_min]
                print('Diff: ' + str(diff))
                delta_p = np.dot(diff, vector_current)
                if delta_p > 0.0000001:  # if not bigger, then we've found a solution

                    print('\nDelta: ' + str(delta_p))
                    print('p_vector[ind_max] = ' + str(p_vector[ind_max]) + '\nnp.linalg.norm(diff)): '
                              + str(np.linalg.norm(diff)))
                    t_param = delta_p / (
                                 p_vector[ind_max] * (np.linalg.norm(diff)) ** 2)  # recounting all variables
                    if t_param >= 1:
                          t_param = 1

                    vector_current -= t_param * p_vector[ind_max] * diff
                    # plt.plot(vector_current, 'r-')

                    supp_vector = []  # recounting
                    temp1 = t_param * p_vector[ind_max]
                    temp2 = (1 - t_param)
                    p_vector[ind_min] += temp1
                    p_vector[ind_max] *= temp2
                    for j in range(len(p_vector)):
                        if p_vector[j] > 0.0000001:
                               supp_vector.append(j)
                    print('Vector current: ' + str(vector_current))
                    iterations += 1
                    print('Iterations: ' + str(iterations))
                    print('Supp_vector: ' + str(supp_vector))

            lambda_t = -np.dot(vector_current, V)/np.linalg.norm(V)**2
            for i in range(cycle_size):
                if t_param_vector[i] > 0:
                     if lambda_t > (1 - p_vector[MIN_set[i]])/t_param_vector[i]:
                          lambda_t = (1 - p_vector[MIN_set[i]])/t_param_vector[i]
                elif t_param_vector[i] < 0:
                     if lambda_t > -p_vector[MAX_set[i]]/t_param_vector[i]:
                        lambda_t = -p_vector[MAX_set[i]]/t_param_vector[i]
            vector_current += lambda_t*V
            for i in range(cycle_size):
                   p_vector[MAX_set[i]] -= lambda_t * t_param_vector[i]
                   p_vector[MIN_set[i]] += lambda_t * t_param_vector[i]

            #IT SHOULDNOT BE THERE:::::::::::::::::::::::::::::::::::::::::
            while delta_p > 0.0000001  and iterations < 1000 and len(supp_vector) != 0:
                if cycle_constructed is True:
                    mult = np.dot(self._points[supp_vector], vector_current)
                    ind_max = np.argmax(mult)  # finding max for indices in supp_vector
                    ind_max = supp_vector[ind_max]  # finding max general in our mult product

                    mult = np.matmul(vector_current, self._A_matrix)
                    ind_min = np.argmin(mult)  # i''_k

                    diff = self._points[ind_max] - self._points[ind_min]
                    print('Diff: ' + str(diff))
                    delta_p = np.dot(diff, vector_current)

                    if delta_p > 0.0000001:  # if not bigger, then we've found a solution

                        print('\nDelta: ' + str(delta_p))
                        print('p_vector[ind_max] = ' + str(p_vector[ind_max]) + '\nnp.linalg.norm(diff)): '
                              + str(np.linalg.norm(diff)))
                        t_param = delta_p / (
                                    p_vector[ind_max] * (np.linalg.norm(diff)) ** 2)  # recounting all variables
                        if t_param >= 1:
                            t_param = 1

                        vector_current -= t_param * p_vector[ind_max] * diff

                        supp_vector = []  # recounting
                        temp1 = t_param * p_vector[ind_max]
                        temp2 = (1 - t_param)
                        p_vector[ind_min] += temp1
                        p_vector[ind_max] *= temp2
                        for i in range(len(p_vector)):
                            if p_vector[i] > 0.0000001:
                                supp_vector.append(i)
                    print('Vector current: ' + str(vector_current))
                    iterations += 1
                    print('Iterations: ' + str(iterations))
                    print('Supp_vector: ' + str(supp_vector))
        return vector_current



# TODO plot it on each step. how??


#plt.plot(points[hull.vertices, 0], points[hull.vertices, 1], points[hull.vertices, 2], 'g-', lw=2)

#points = generate_points(3, 68, 30, 3)
points =np.array([[ -73.337555  ,   -4.82192605],
       [   9.36299101,   14.79378288],
       [  33.74875017,   10.02043701],
       [ 133.04981839,   92.18760616],
       [-105.00396348,  -69.46640213],
       [  32.54560694,   43.96449265],
       [ -78.01174375,   61.08025333],
       [  92.03366094,  -51.6208306 ],
       [  17.22114877,   54.92524147],
       [ -87.14266467,  128.5875058 ],
       [ -35.76597696, -161.63324815],
       [ 156.36709765,  -55.60266369],
       [  41.00897625,  -54.92133061],
       [ 129.50005618,  -39.14660553],
       [ 101.99767049,    5.91893179],
       [ 120.62635591,   39.32842524],
       [  58.91037616,  -29.52086718],
       [-116.99548555,  -35.64041842],
       [ -49.26778003,   18.11377985],
       [  91.22017504,   26.95527778],
       [   5.98350205,  -29.65544224],
       [  73.8606758 ,  -67.33527561],
       [ -57.11269196,  -23.38066312],
       [  10.29413585,   19.91249178],
       [ -76.57980277,   36.15112039],
       [  40.91217006,  -17.81387299],
       [  51.88700332,  -69.65988091],
       [  57.41048001, -119.28130887],
       [ -66.49323658,  -92.43371661],
       [  10.46455101,  -80.23934518]])
# points = np.array([[3, 4],[-3, 11],[5, 4], [5.5, 2], [7.5, 5.5], [-3, 17]])
dim = 2
hull = get_convex_hull_and_plot(points, dim)
mdm = MDM(points, hull, dim)
result = mdm.solve()            #result is a point in R^dim
if(dim ==2):
    plt.plot([result[0], 0], [result[1], 0], 'ro')
elif(dim==3):
    plt.plot([result[0], 0], [result[1], 0], [result[2], 0], 'ro')
plt.show()
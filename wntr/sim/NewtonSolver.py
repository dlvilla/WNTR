import numpy as np
import scipy.sparse as sp
import copy
import time
import warnings
import logging

# Ideas:
#    scale variables
#    fraction to the boundary rule
#    better line search
#    Incorrect jacobian

warnings.filterwarnings("error",'Matrix is exactly singular',sp.linalg.MatrixRankWarning)
np.set_printoptions(precision=3, threshold=10000, linewidth=300)

logger = logging.getLogger('wntr.sim.NewtonSolver')

class NewtonSolver(object):
    def __init__(self, num_nodes, num_links, num_leaks, options={}):
        self._options = options
        self.num_nodes = num_nodes
        self.num_links = num_links
        self.num_leaks = num_leaks

        self.flow_filter = np.ones(self.num_nodes*2+self.num_links+self.num_leaks)
        self.flow_filter[self.num_nodes*2:(2*self.num_nodes+self.num_links)] = np.zeros(self.num_links)

        if 'MAXITER' not in self._options:
            self.maxiter = 300
        else:
            self.maxiter = self._options['MAXITER']

        if 'TOL' not in self._options:
            self.tol = 1e-6
        else:
            self.tol = self._options['TOL']

        if 'BT_C' not in self._options:
            self.bt_c = 0.0001
        else:
            self.bt_c = self._options['BT_C']

        if 'BT_RHO' not in self._options:
            self.rho = 0.5
        else:
            self.rho = self._options['BT_C']

        if 'BT_MAXITER' not in self._options:
            self.bt_maxiter = 30
        else:
            self.bt_maxiter = self._options['BT_MAXITER']

        if 'BACKTRACKING' not in self._options:
            self.bt = True
        else:
            self.bt = self._options['BACKTRACKING']


    def solve(self, Residual, Jacobian, x0):

        x = np.array(x0)

        num_vars = len(x)

        #I = sp.csr_matrix((np.ones(num_vars),(range(num_vars),range(num_vars))),shape=(num_vars,num_vars))
        #I = 10*I
        use_r_ = False

        # MAIN NEWTON LOOP
        for iter in xrange(self.maxiter):
            if use_r_:
                r = r_
                r_norm = lhs
            else:
                r = Residual(x)
                r_norm = np.max(abs(r))

            #logger.debug('iter: {0:<10d} inf norm: {1:<16.8f}'.format(iter, r_norm))
            #logger.debug('x = {0}'.format(x))

            if r_norm < self.tol:
                return [x, iter, 1]

            J = Jacobian(x)
            
            # Call Linear solver
            #t0 = time.time()
            try:
                d = -sp.linalg.spsolve(J,r)
            except sp.linalg.MatrixRankWarning:
                print 'Jacobian is singular.'
                return [x, iter, 0]
                #print 'Jacobian is singular. Adding regularization term.'
                #J = J+I
                #d = -sp.linalg.spsolve(J,r)
            #logger.debug('step = {0}'.format(d))
            #d = -np.linalg.solve(J, r)
            #self._total_linear_solver_time += time.time() - t0

            # Backtracking
            alpha = 1.0
            if self.bt:
                use_r_ = True
                for iter_bt in xrange(self.bt_maxiter):
                    #print alpha
                    rhs = r_norm
                    x_ = x + alpha*d
                    r_ = Residual(x_)
                    #if iter_bt > 0:
                    #    last_lhs = lhs
                    #    lhs = np.max(abs(r_))
                    #else:
                    lhs = np.max(abs(r_))
                    #    last_lhs = lhs + 1.0
                    #rhs = np.max(r + self.bt_c*alpha*J*d)
                    #print "     ", iter, iter_bt, alpha
                    if lhs < (1.0-0.0001*alpha)*rhs:
                        #x_ -= self.flow_filter*(x_<=-100.0)*x_*0.01
                        x = x_
                        break
                    else:
                        alpha = alpha*self.rho

                if iter_bt+1 >= self.bt_maxiter:
                    return [x,iter,0]
                    #raise RuntimeError("Backtracking failed. ")
            else:
                x += d
            #print 'alpha = ',alpha

        return [x, iter, 0]
        #raise RuntimeError("No solution found.")




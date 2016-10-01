import argparse
from mpl_toolkits.mplot3d import axes3d
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np

from streamplt.data_listener import DataListener

def scale_to_len(q1, q2, q3, length=1):
    c  = float(length) / np.linalg.norm([q1, q2, q3])
    return (q1*c, q2*c, q3*c)

def quat_to_euler(q):
    """ Converts quaternion 'q' to Euler angles. """
    q = np.array(q) / np.linalg.norm(q)
    phi = np.arctan2(2*(q[0]*q[1] + q[2]*q[3]), 1 - 2*(q[1]**2 + q[2]**2))
    theta = np.arcsin(2*(q[0]*q[2] - q[3]*q[1]))
    psi = np.arctan2(2*(q[0]*q[3] + q[1]*q[2]), 1-2*(q[2]**2+q[3]**2))
    return (phi, theta, psi)

def quat_conjugate(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])

def quat_prod(a, b):
    c = np.empty((4,))
    c[0] = a[0]*b[0] - np.dot(a[1:], b[1:])
    c[1:] = a[0]*b[1:]+b[0]*a[1:]+np.cross(a[1:], b[1:])
    return c

def rotate_by_quat(p, q):
    if not isinstance(q, np.ndarray):
        q = np.array(q)

    # Normalize to unit length
    q = q / np.linalg.norm(q)

    # Augment 3-vector.
    p = np.array([0, p[0], p[1], p[2]])

    # Perform rotation by the quaternion.
    p_r = quat_prod(q, quat_prod(p, quat_conjugate(q)))
    return p_r[1:]

class Orientation3dPlot(object):
    """ A 3D plot of streaming orientation data.

    Supports various input modes:
    ===========================================================================
    * 'xyz': input data is a 3-vector, possibly unnormalized, giving a
             direction from the origin.
    * 'wxyz': input data is a quaternion giving an orientation with respect to
              the positive x-axis.
    """
    MAX_NUM_FRAMES = 100000000
    def __init__(self, address, input_mode='xyz',
                 interval_ms=20, lw=2, arrow_len=1.0,
                 fig=None, ax=None):
        assert (input_mode in ('xyz', 'wxyz')), \
                "Unsupported mode: " + input_mode
        self.input_mode = input_mode

        # Setup transformation function per input mode.
        self.transformation_fn = lambda x: x
        if input_mode == 'wxyz':
            self.transformation_fn =  lambda q : rotate_by_quat([1,0,0], q)

        buffer_width = 1 + (3 if input_mode == 'xyz' else 4)
        self.listener = DataListener(address, buffer_width=buffer_width,
                buffer_length=10)
        self.listener.start()

        if fig and ax:
            self.fig = fig
            self.ax = ax
        else:
            self.fig = plt.figure()
            self.ax = self.fig.gca(projection='3d')

        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)

        self.arrow_position = (0,0,0)
        self.arrow_orientation = (0,0,arrow_len)
        self.arrow_len = arrow_len

        self.quiver = self.ax.quiver([0], [0], [0],
                        [self.arrow_orientation[0]],
                        [self.arrow_orientation[1]],
                        [self.arrow_orientation[2]],
                        length=self.arrow_len,
                        pivot='middle')

        self.anim = animation.FuncAnimation(
                self.fig, self.animate,
                init_func=self.init_func,
                frames=Orientation3dPlot.MAX_NUM_FRAMES,
                interval=interval_ms,
                blit=False)

    def init_func(self):
        return (self.quiver,)

    def animate(self, i):
        data = self.listener.get_data()
        if len(data) == 0:
            return (self.quiver,)

        self.ax.collections.remove(self.quiver)

        t = data[-1][0]
        q1, q2, q3 = self.transformation_fn(data[-1][1:])
        q1, q2, q3 = scale_to_len(q1, q2, q3)
        self.quiver = self.ax.quiver([0], [0], [0],
                        [q1], [q2], [q3],
                        length=self.arrow_len,
                        pivot='middle')

        return (self.quiver,)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", '-a', default= "ipc:///tmp/stream",
                        help="Address to listen to for incoming data.")
    parser.add_argument("--mode", '-m', choices=["xyz", "wxyz"], default="xyz")

    args = parser.parse_args()

    s = Orientation3dPlot(args.address, input_mode=args.mode)
    plt.show()

if __name__ == "__main__":
    main()


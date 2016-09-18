import argparse
from mpl_toolkits.mplot3d import axes3d
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np

from streamplt.data_listener import DataListener

def scale_to_len(q1, q2, q3, length=1):
    c  = float(length) / np.linalg.norm([q1, q2, q3])
    return (q1*c, q2*c, q3*c)

class Orientation3dPlot(object):
    MAX_NUM_FRAMES = 100000000
    def __init__(self, address, interval_ms=20, lw=2, arrow_len=1.0, fig=None, ax=None):
        self.listener = DataListener(address, buffer_width=3+1,
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

        t, q1, q2, q3 = data[-1]
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

    args = parser.parse_args()

    s = Orientation3dPlot(args.address)
    plt.show()

if __name__ == "__main__":
    main()


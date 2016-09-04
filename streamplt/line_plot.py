import numpy as np
import argparse
import time
import datetime
import matplotlib.pyplot as plt
from matplotlib import animation
from streamplt.data_listener import DataListener

def get_duration_string(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02.2f" % (h, m, s)


class StreamLinePlot(object):
    MAX_NUM_FRAMES = 1000000000
    def __init__(self, address, dim=1, time_window=10, buffer=1000, ylim=None,
            interval_ms=20, lw=2, fig=None, ax=None):
        self.listener = DataListener(address, buffer_width=dim+1,
                buffer_length=buffer)
        self.listener.start()

        if fig and ax:
            self.fig = fig
            self.ax = ax
        else:
            self.fig = plt.figure()
            self.ax = plt.axes(xlim=(0, time_window), ylim=ylim)

        self.time_text = self.ax.text(0.02, 0.95, '', transform=self.ax.transAxes)

        self.lines = tuple(self.ax.plot([], [], lw=lw)[0] for _ in xrange(dim))

        self.init_time = time.time()
        self.time_window = time_window

        self.anim = animation.FuncAnimation(
                self.fig, self.animate,
                init_func=self.init_func,
                frames=StreamLinePlot.MAX_NUM_FRAMES,
                interval=interval_ms,
                blit=False)

    def init_func(self):
        for j in xrange(len(self.lines)):
            self.lines[j].set_data([], [])

        self.time_text.set_text('')
        return self.lines + (self.time_text,)

    def update_ylim(self, data):
        """ Returns a new (min, max) tuple if we should resize the axis. None
        otherwise.

        Args:
            data: latest batch of data being plotted
        """

        current_lim = self.ax.get_ylim()
        dmin = min([d[j] for d in data for j in xrange(1, len(data[0]))])
        dmax = max([d[j] for d in data for j in xrange(1, len(data[0]))])

        if dmin > current_lim[0] and dmax < current_lim[1]:
            return None
        else:
            return (min(dmin, current_lim[0]), max(dmax, current_lim[1]))


    def animate(self, i):
        data = self.listener.get_data()
        if len(data) == 0:
            return self.lines + (self.time_text,)

        end_time = time.time()
        t = [self.time_window - (end_time - d[0]) for d in reversed(data)]

        for j in xrange(len(self.lines)):
            self.lines[j].set_data(t, [d[j+1] for d in reversed(data)])

        self.time_text.set_text("time: " + get_duration_string(end_time -
            self.init_time))

        new_ylim = self.update_ylim(data)
        if new_ylim is not None:
            self.ax.set_ylim(new_ylim)

        return self.lines + (self.time_text,)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", '-a', default= "ipc:///tmp/stream",
                        help="Address to listen to for incoming data.")
    parser.add_argument("--dim", '-d', type=int, default=3,
                        help="Dimensionality of incoming data (not including "
                             "time)")

    parser.add_argument("--ylim", '-y', type=float, default=50)
    parser.add_argument("--buffersize", '-b', type=int, default=1000)
    parser.add_argument("--time_window", '-w', type=int, default=10,
                        help="Span of time to display on plot.")

    args = parser.parse_args()

    s = StreamLinePlot(args.address, dim=args.dim, ylim=(-args.ylim,args.ylim),
                       buffer=args.buffersize)
    plt.show()

if __name__ == "__main__":
    main()


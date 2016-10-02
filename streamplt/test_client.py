import zmq
import random
import time
import argparse
import numpy as np

context = zmq.Context()
class TestClient:
    def __init__(self, dim, delay=0.5, address="ipc:///tmp/stream"):
        self.dim = dim
        self.delay = delay
        self.format_string = ",".join("%f" for _ in xrange(dim+1))
        self.sock = context.socket(zmq.PUB)
        self.sock.bind(address)

    def run(self):
        x = np.random.rand(self.dim) - 0.5
        while True:
            x += np.random.rand(self.dim) - 0.5
            t = time.time()
            self.sock.send(self.format_string % ((t,)+tuple(x)))
            time.sleep(self.delay)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dim", "-d", type=int, default=3)
    parser.add_argument("--address", "-a", default="ipc:///tmp/stream")
    parser.add_argument("--time", "-t", type=float, default=0.5,
                        help="Time to wait between subsequent samples.")
    args = parser.parse_args()

    client = TestClient(args.dim, delay=args.time, address=args.address)
    client.run()

if __name__ == "__main__":
    main()

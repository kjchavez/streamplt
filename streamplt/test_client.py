import zmq
import random
import time

context = zmq.Context()

sock = context.socket(zmq.PUB)
sock.bind("ipc:///tmp/stream")

x = 0.0
y = 0.0
z = 0.0
while True:
    t = time.time()
    x += 2*(random.random() - 0.5)
    y += 1*(random.random() - 0.5)
    z += 1*(random.random() - 0.5)
    sock.send("%f, %f, %f, %f" % (t, x, y, z))
    time.sleep(0.01)

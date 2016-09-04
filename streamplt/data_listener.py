import collections
import copy
import threading
import zmq

context = zmq.Context()
class DataListener(object):
    def __init__(self, address, buffer_width=1, buffer_length=1000):
        self.data = collections.deque([], buffer_length)
        self.address = address
        self.buffer_width = buffer_width
        self.data_lock = threading.Lock()

    def run(self):
        sock = context.socket(zmq.SUB)
        sock.connect(self.address)
        sock.setsockopt_string(zmq.SUBSCRIBE, u'')

        while True:
            msg = sock.recv()
            try:
                data_point = tuple(float(x) for x in msg.split(','))
                if len(data_point) == self.buffer_width:
                    self.data_lock.acquire()
                    self.data.appendleft(data_point)
                    self.data_lock.release()
                else:
                    print "Warning invalid data width!"
            except:
                print "Warning. Invalid data: ", msg

    def start(self):
        t = threading.Thread(target=self.run)
        t.start()

    def get_data(self):
        self.data_lock.acquire()
        data = copy.deepcopy(self.data)
        self.data_lock.release()
        return data


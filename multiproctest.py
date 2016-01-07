#!/usr/bin/env python

import sys
from multiprocessing import Process, JoinableQueue as Queue
import time
import datetime
import random

class Feeder(Process):
    def __init__(self,inputqueue,outputqueue, threads):
        self.inputqueue = inputqueue
        self.outputqueue = outputqueue
        super().__init__()

        for i in range(0,50000):
            self.inputqueue.put(random.randint(1,1000) )

        for i in range(0,threads):
            self.inputqueue.put(None)


    def run(self):
        while True:
            n = self.outputqueue.get()
            self.outputqueue.task_done()
            if n is None:
                break
            #print("out="+str(n))

        print("outputqueue end")

class Processor(Process):
    def __init__(self, inputqueue, outputqueue):
        self.inputqueue = inputqueue
        self.outputqueue = outputqueue
        super().__init__()

    def compute(self,n):
        x = []
        for i in range(0,random.randint(1000,10000)):
            x.append(random.random() )
        return n * random.random() * sum(x)

    def run(self):
        while True:
            n = self.inputqueue.get()
            self.inputqueue.task_done()
            if n is None:
                print("inputqueue end")
                break
            else:
                print(datetime.datetime.now().strftime("%H:%M:%S.%f") + " - BEGIN " + str(self.pid),file=sys.stderr)
                n = self.compute(n)
                self.outputqueue.put(n)
                print(datetime.datetime.now().strftime("%H:%M:%S.%f") + " - END   " + str(self.pid),file=sys.stderr)


if __name__ == '__main__':
    begintime = time.time()

    inputqueue = Queue()
    outputqueue = Queue()
    threads = int(sys.argv[1])

    feeder = Feeder(inputqueue,outputqueue, threads)
    feeder.start()
    duration = time.time() - begintime
    print("Feeder started (" + str(duration) + "s)")


    for _ in range(0,threads):
        processor = Processor(inputqueue,outputqueue)
        processor.start()

    inputqueue.join()
    duration = time.time() - begintime
    print("Inputqueue done (" + str(duration) + "s)")
    outputqueue.put(None)

    print("Outputqueue length (" + str(outputqueue.qsize()) + ")")
    feeder.join()
    duration = time.time() - begintime
    print("Outputqueue done (" + str(duration) + "s)")


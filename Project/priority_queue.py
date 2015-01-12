#!/usr/bin/env python
# -*- coding: utf-8 -*-

from heapq import *

class PriorityQueue(object):
    def __init__(self):
        super(PriorityQueue, self).__init__()
        self.heap = []

    def push(self, value, priority):
        heappush(self.heap, (- priority, value))

    def pop(self):
        return heappop(self.heap)[-1]

    def __str__(self):
        return 'PriorityQueue ' + self.heap.__str__()
        
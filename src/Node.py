import math
import random
import heapq
from collections import deque


class Node:
    def __init__(self, node_id, coordinates):
        self.node_id = node_id
        self.coordinates = coordinates
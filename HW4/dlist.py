class Node(object):
    def __init__(self, prev, next, val):
        self.prev = prev
        self.next = next
        self.val = val

class DList(object):
    '''double linked list'''

    def __init__(self):
        self.map = {}
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, val):
        assert(not (val in self.map))
        if self.size == 0:
            self.head = Node(None, None, val)
            self.tail = self.head
        else:
            self.head.next = Node(self.head, None, val)
            self.head = self.head.next

        self.size = self.size + 1
        self.map[val] = self.head
        return self.head

    def pop(self, val):
        node = self.map[val]
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if self.head is node:
            self.head = self.head.prev
        if self.tail is node:
            self.tail = self.tail.next
        node.next = None
        node.prev = None
        self.size = self.size - 1
        del self.map[val]
        return node.val

    def pop_front(self):
        return self.pop(self.tail.val)

    def pop_back(self):
        return self.pop(self.head.val)

    def find(self, val):
        if val in self.map:
            return self.map[val]
        return None

    def __len__(self):
        return self.size

    def __contains__(self, val):
        return val in self.map

    def __getitem__(self, val):
        return self.map[val].val

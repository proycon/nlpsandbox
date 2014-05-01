
class NestedNamedDict():
    def __init__(self):
        self._node = {}
        self._list = False

    def __setattr__(self, attrib, value):
        if attrib[0] != '_':
            self._node[attrib] = value
        else:
            return super(NestedNamedDict,self).__setattr__(attrib, value)

    def __getattr__(self, attrib):
        if attrib[0] != '_':
            if not attrib in self._node:
                self._node[attrib] = NestedNamedDict()
            return self._node[attrib]
        else:
            return super(NestedNamedDict,self).__getattr__(attrib)

    def __getitem__(self, index):
        if isinstance(index,int):
            if not index in self._node:
                self._node[index] = NestedNamedDict()
                self._node[index]._list = True
            return self._node[index]
        else:
            return self.__getattr__(index)

    def __setitem__(self, index, value):
        if isinstance(index,int):
            self._node[index] = value
        else:
            return self.__setattr__(index, value)

    def __len__(self):
        return len(self._node)

    def __iter__(self):
        if self._list:
            return sorted(iter(self._node))
        else:
            return iter(self._node)


if __name__ == '__main__':

    d = NestedNamedDict()

    d.blah.blieh.blo = 4
    d.blah.bluh = 5
    print(d.blah.blieh.blo)
    print(d.blah)

    d.blah.l[0] = 'a'
    d.blah.l[1] = 'b'
    d.blah.l[2].x = 'c'

    for name in d.blah:
        print(name)

    for name in d.blah.l:
        print(name)


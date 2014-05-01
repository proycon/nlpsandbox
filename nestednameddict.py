from __future__ import print_function, unicode_literals, division, absolute_import

class NestedNamedDict(object):
    def __init__(self, name):
        self._name = name
        self._node = {}
        self._list = False

    def __setattr__(self, attrib, value):
        if attrib[0] != '_' and not self._list:
            self._node[attrib] = value
        else:
            return super(NestedNamedDict,self).__setattr__(attrib, value)

    def __getattr__(self, attrib):
        if attrib[0] != '_' and not self._list:
            if not attrib in self._node:
                self._node[attrib] = NestedNamedDict(attrib)
            return self._node[attrib]
        else:
            raise AttributeError
            #return super(NestedNamedDict,self).__getattr__(attrib)

    def __getitem__(self, index):
        if isinstance(index,int):
            if not index in self._node:
                self._node[index] = NestedNamedDict(self._name)
                self._list = True
            return self._node[index]
        else:
            return self.__getattr__(index)

    def __setitem__(self, index, value):
        if isinstance(index,int):
            self._node[index] = value
            self._list = True
        else:
            return self.__setattr__(index, value)

    def __len__(self):
        return len(self._node)

    def __iter__(self):
        if self._list:
            for i in sorted(self._node):
                yield self._node[i]
        else:
            for n in self._node:
                yield n

    def __str__(self):
        if self._list:
            s = ""
            for node in self:
                if isinstance(node, NestedNamedDict):
                    s += str(node)
                else:
                    s += "<"  + self._name + ">" + str(node) + "</"  + self._name + ">"
            return s
        else:
            s = "<" + self._name + ">"
            for node, value in self._node.items():
                if isinstance(value, NestedNamedDict):
                    s += str(value)
                else:
                    s += "<" + node + ">" + str(value) + "</" + node + ">"
            return s + "</" + self._name + ">"



if __name__ == '__main__':

    d = NestedNamedDict('d')

    d.blah.blieh.blo = 4
    d.blah.bluh = 5

    for name in d.blah:
        print(name)


    #print converts to str(), which means XML in our case:
    print(d.blah.blieh.blo)
    print(d.blah)

    d.blah.l[0] = 'a'
    d.blah.l[1] = 'b'
    d.blah.l[2] = 'c'


    for value in d.blah.l:
        print(value)

    print(d)

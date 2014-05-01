
class NestedNamedDict():
    def __init__(self):
        self._node = {}

    def __setattr__(self, attrib, value):
        if attrib[0] != '_':
            print("Setting attrib: ", attrib)
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

    def __len__(self):
        return len(self._node)

    def __iter__(self):
        return iter(self._node)

if __name__ == '__main__':

    d = NestedNamedDict()

    d.blah.blieh.blo = 4
    d.blah.bluh = 5
    print(d.blah.blieh.blo)
    print(d.blah)

    for name in d.blah:
        print(name)

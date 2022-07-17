class Path:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.sx = 0
        self.sy = 0
        self.elements = []

    def moveto(self, x, y, absolute=True):
        if not absolute:
            x += self.cx
            y += self.cy
        self.elements.append(('M', x, y))
        self.cx = self.sx = x
        self.cy = self.sy = y

    def lineto(self, x, y, absolute=True):
        if not absolute:
            x += self.cx
            y += self.cy
        self.elements.append(('L', x, y))
        self.cx = x
        self.cy = y

    def close(self):
        self.elements.append(('Z', self.sx, self.sy))
        self.cx = self.sx
        self.cy = self.sy

    def svg(self):
        def transform(el):
            if el[0] == 'Z':
                return 'Z'
            if el[0] in ('M', 'L'):
                return f'{el[0]}{el[1]} {el[2]}'
        return ''.join(map(transform, self.elements))

    def cff(self):
        x0 = y0 = 0
        def transform(el):
            nonlocal x0, y0
            if el[0] == 'Z':
                pass
            if el[0] == 'M':
                x, y = el[1], el[2]
                r = f'{x-x0} {y-y0} rmoveto'
                x0, y0 = x, y
                return r
            if el[0] == 'L':
                x, y = el[1], el[2]
                r = f'{x-x0} {y-y0} rlineto'
                x0, y0 = x, y
                return r
        return '\n'.join(map(transform, self.elements))

    def transform(self, a, b, c, d, e, f):
        self.elements = [(t, a*x+c*y+e, b*x+d*y+f) for (t,x,y) in self.elements]

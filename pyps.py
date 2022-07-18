import copy
import itertools

import op_base
import op_dict
import op_array
import op_font
import op_graphics

import gpath

from svgdevice import SVGDevice
from psobject import PSObject

def populate(d, module):
    for key, value in module.__dict__.items():
        if key[:3] == 'op_':
            d[key[3:]] = PSObject('operatortype', value, False)

class PushBackIter:
    def __init__(self, iterable):
        self.iter = iter(iterable)
        self.queue = []

    def __next__(self):
        if self.queue:
            x = self.queue.pop()
        else:
            x = next(self.iter, '\004')
        #print(x)
        return x

    def __iter__(self):
        return self

    def push(self, value):
        self.queue.append(value)


def scanps(source):
    tokens = []

    def emit(ttype, value):
        if tokens:
            tokens[-1].append(PSObject.from_token(ttype, value))
        else:
            #print(ttype, repr(value))
            yield PSObject.from_token(ttype, value)

    def hexstring():
        value = ''

        while True:
            c = next(chars)
            if c == '>':
                return bytes.fromhex(value).decode('latin1')
            elif c.lower() in '0123456789abcdef':
                value += c.lower()
            else:
                assert c in ' \n\t', f'illegal cahracter {c!r} in <...>'

    def string():
        nparen = 0
        value = ''

        while True:
            c = next(chars)
            if c == ')' and nparen == 0:
                return value
            if c == '\\':
                c = next(chars)
                if c == 'n':
                    value += '\n'
                elif c == 'r':
                    value += '\r'
                elif c == 't':
                    value += '\t'
                elif c == 'b':
                    value += '\b'
                elif c == 'f':
                    value += '\f'
                elif c in '()\\':
                    value += c
                elif c in '01234567':
                    c1 = next(chars)
                    assert c1 in '01234567'
                    c0 = next(chars)
                    assert c0 in '01234567'
                    value += chr(64*int(c) + 8*int(c1) + int(c0))
                else:
                    assert False, f'illegal escape sequence \\{c}'
            else:
                value += c
                if c == '(':
                    nparen += 1
                if c == ')':
                    nparen -= 1
                    assert nparen >= 0

    def name():
        value = ''
        c = next(chars)
        assert c not in '\004\0 \t\n\r\f()<>[]{}/%', c
        while c not in '\004\0 \t\n\r\f()<>[]{}/%':
            value += c
            c = next(chars)
        chars.push(c)
        return value

    def number():
        value = ''
        c = next(chars)
        while c not in '\004\0 \t\n\r\f()<>[]{}/%':
            value += c
            c = next(chars)

        if '#' in value:
            base, value = value.split('#')
            value = int(value, int(base))
        else:
            try:
                value = int(value)
            except ValueError:
                value = float(value)
        chars.push(c)
        return value

    chars = PushBackIter(source)

    while True:
        c = next(chars, None)
        if c is None:
            return

        if c == '%':
            while c != '\n':
                c = next(chars)
            continue

        if c in '\0 \t\n\r\f':
            while c in '\0 \t\n\r\f':
                c = next(chars)
            chars.push(c)
            continue

        if c == '(':
            yield from emit('STRING', string())
            continue

        if c == '<':
            yield from emit('STRING', hexstring())
            continue

        if c == '/':
            c = next(chars)
            if c == '/':
                yield from emit('IMMNAME', name())
                continue
            chars.push(c)
            yield from emit('LITNAME', name())
            continue

        if c in '[]':
            yield from emit('NAME', c)
            continue

        if c == '{':
            tokens.append([])
            continue
        if c == '}':
            assert tokens, 'unmatched }'
            yield from emit('PROC', tokens.pop())
            continue

        if c in '+-.0123456789':
            chars.push(c)
            yield from emit('NUMBER', number())
            continue

        if c == '\004':
            return

        chars.push(c)
        yield from emit('NAME', name())
        continue


#tokens = list(scanps(open('testfiles/region.ps').read()))

class DictStack:
    def __init__(self):
        self.stack = []

    def push(self, d=None):
        if d is None:
            d = {}
        self.stack.append(d)

    def pop(self):
        assert len(self.stack) > 3, 'can not pop bottom 3 dicts'
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def __getitem__(self, key):
        for d in reversed(self.stack):
            try:
                return d[key]
            except KeyError:
                if d is self.stack[0]:
                    raise
        raise KeyError

    def __setitem__(self, key, value):
        self.stack[-1][key] = value

    def where(self, key):
        for d in reversed(self.stack):
            if key in d:
                return d

class GraphicsState:
    def __init__(self):
        self.current_path = gpath.Path()
        self.color_space = 'DeviceRGB'
        self.color = (0,0,0)
        self.line_width = 1.0
        self.CTM = [1,0,0,1,0,0]

    def transform(self, x, y):
        a,b,c,d,tx,ty = self.CTM
        return a*x + c*y + tx, b*x + d*y + ty

    def itransform(self, x, y):
        a,b,c,d,tx,ty = self.CTM
        det = b*c - a*d
        return (d*(tx-x) + c*(y-ty))/det, (a*(ty-y) + b*(x-tx))/det

    def newpath(self):
        self.current_path = gpath.Path()
        self.current_point = None

    def moveto(self, x, y):
        print('moveto', x, y, self.CTM, self.transform(x,y))
        self.current_path.moveto(*self.transform(x,y))
        self.current_point = (x,y)
        #print(self.current_path)

    def rmoveto(self, x, y):
        print('rmoveto', x, y, self.CTM)
        (u,v) = self.itransform(*self.current_point)
        x += u
        y += v
        self.current_path.moveto(*self.transform(x,y))
        self.current_point = (x,y)
        #print(self.current_path)

    def lineto(self, x, y):
        print('lineto', x, y, self.CTM, self.transform(x,y))
        self.current_path.lineto(*self.transform(x,y))
        self.current_point = (x,y)
        #print(self.current_path)

    def rlineto(self, x, y):
        print('rlineto', x, y, self.CTM)
        (u,v) = self.current_point
        x += u
        y += v
        self.current_path.lineto(*self.transform(x,y))
        self.current_point = (x,y)
        #print(self.current_path)

    def closepath(self):
        print('closepath', self.CTM)
        self.current_path.close()
        #print(self.current_path)

class Interpreter:
    def __init__(self):
        self.dict_stack = DictStack()
        self.userdict = {}
        self.globaldict = {}

        self.fonts = {}

        self.ids = itertools.count(101)

        self.mark = PSObject('marktype', None, True)
        self.false = PSObject('booltype', False, True)
        self.true = PSObject('booltype', True, True)
        self.null = PSObject('nulltype', None, True)

        self.systemdict = {
            'userdict': PSObject('dicttype', self.userdict, True),
            'globaldict': PSObject('dicttype', self.globaldict, True),
            'false': self.false,
            'true': self.true,
            'mark': self.mark, '[': self.mark, '<<': self.mark,
            'statusdict': PSObject('dicttype', {}, True),
            'product': PSObject('stringtype', 'PYPS', True),
            }
        self.dict_stack.push(self.systemdict)
        self.dict_stack.push(self.globaldict)
        self.dict_stack.push(self.userdict)

        populate(self.systemdict, op_base)
        populate(self.systemdict, op_dict)
        populate(self.systemdict, op_array)
        populate(self.systemdict, op_font)
        populate(self.systemdict, op_graphics)

        self.op_stack = []
        self.ex_stack = []

        self.graphics_state_stack = [GraphicsState()]
        self.page_device = SVGDevice()

    @property
    def graphics_state(self):
        return self.graphics_state_stack[-1]

    def gsave(self):
        self.graphics_state_stack.append(copy.deepcopy(self.graphics_state))

    def grestore(self):
        self.graphics_state_stack.pop()

    def execfile(self, fname):
        self.ex_stack.append(scanps(open(fname).read()))
        while self.ex_stack:
            tokens = self.ex_stack[-1]
            token = next(tokens, None)
            if not token:
                self.ex_stack.pop()
                continue
            self.execobj(token, True)

    def execsub(self, tokens):
        sentinel = object()
        self.ex_stack.append(sentinel)
        self.ex_stack.append(tokens)
        while self.ex_stack:
            tokens = self.ex_stack[-1]
            if tokens is sentinel:
                self.ex_stack.pop()
                return
            token = next(tokens, None)
            if not token:
                self.ex_stack.pop()
                continue
            self.execobj(token, True)


    def execobj(self, token, direct):
        try:
            print('ops:', ' '.join(map(str, self.op_stack)))
        except:
            print('ops: --')
            pass
        print('tok:', token)
        if (token.literal
            or token.type in ('integertype', 'realtype', 'stringtype')
            or (token.type == 'arraytype' and direct)):
            self.op_stack.append(token)

        elif token.type == 'nametype':
            obj = self.dict_stack[token.value]
            self.execobj(obj, False)

        elif token.type == 'operatortype':
            token.value(self)

        elif token.type == 'arraytype':
            self.ex_stack.append(iter(token.value))

        else:
            assert False, f'not implemented: {token}'
        try:
            print('ops:', ' '.join(map(str, self.op_stack)))
        except:
            print('ops: --')
        print()
        assert all(isinstance(x, PSObject) for x in self.op_stack)

    def bool(self, value):
        if value:
            return self.true
        else:
            return self.false



# interpreter = Interpreter()
# interpreter.execfile('testfiles/region.ps')
# interpreter.page_device.write('testfiles/region.svg')
if __name__ == '__main__':
    import sys
    interpreter = Interpreter()
    interpreter.execfile(sys.argv[1])
    interpreter.page_device.write(sys.argv[2])

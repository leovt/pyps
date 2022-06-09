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
            print(ttype, repr(value))
            yield PSObject.from_token(ttype, value)

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
                    assert c2 in '01234567'
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

        if c in '+-0123456789':
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

    def __getitem__(self, key):
        for d in reversed(self.stack):
            try:
                return d[key]
            except KeyError:
                pass
        raise KeyError

    def __setitem__(self, key, value):
        self.stack[-1][key] = value

class PSObject:
    def __init__(self, type, value, literal):
        self.type = type
        self.value = value
        self.literal = literal

    def __repr__(self):
        return f'{self.__class__.__name__}({self.type}, {self.value}, {self.literal})'

    @classmethod
    def from_token(cls, ttype, value):
        if ttype == 'NAME':
            return cls('nametype', value, False)
        if ttype == 'LITNAME':
            return cls('nametype', value, True)
        if ttype == 'NUMBER':
            if isinstance(value, int):
                return cls('integertype', value, True)
            else:
                return cls('realtype', value, True)
        if ttype == 'PROC':
            return cls('arraytype', value, False)
        assert False, f'unknown ttype {ttype}'



class Interpreter:
    def __init__(self):
        self.dict_stack = DictStack()
        self.userdict = {}
        self.globaldict = {}
        self.systemdict = {
            'userdict': self.userdict,
            'globaldict': self.globaldict}
        self.dict_stack.push(self.systemdict)
        self.dict_stack.push(self.globaldict)
        self.dict_stack.push(self.userdict)

        self.op_stack = []
        self.ex_stack = []

    def execfile(self, fname):
        self.ex_stack.append(scanps(open(fname).read()))
        while self.ex_stack:
            tokens = self.ex_stack[-1]
            token = next(tokens, None)
            if not token:
                self.ex_stack.pop()
                continue
            if token.literal:
                self.op_stack.append(token)
                print('ops:', self.op_stack)

interpreter = Interpreter()
interpreter.execfile('testfiles/region.ps')

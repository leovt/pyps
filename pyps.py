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
    tokens = [[]]

    def emit(ttype, value):
        print(ttype, repr(value))
        tokens[-1].append((ttype, value))

    def begin():
        c = next(chars, None)
        if c is None:
            return

        if c == '%':
            while c != '\n':
                c = next(chars)
            return begin

        if c in '\0 \t\n\r\f':
            while c in '\0 \t\n\r\f':
                c = next(chars)
            chars.push(c)
            return begin

        if c == '(':
            return string

        if c == '/':
            c = next(chars)
            if c == '/':
                return immname
            chars.push(c)
            return litname

        if c in '[]':
            emit('NAME', c)
            return begin

        if c == '{':
            tokens.append([])
            return begin
        if c == '}':
            assert len(tokens)>1, 'unmatched }'
            emit('PROC', tokens.pop())
            return begin

        if c in '+-0123456789':
            chars.push(c)
            return number

        if c == '\004':
            return None

        chars.push(c)
        return name

    def string():
        nparen = 0
        value = ''

        while True:
            c = next(chars)
            if c == ')' and nparen == 0:
                emit('STRING', value)
                return begin
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

    def immname():
        value = ''
        c = next(chars)
        while c not in '\004\0 \t\n\r\f()<>[]{}/%':
            value += c
            c = next(chars)
        emit('IMMNAME', value)
        chars.push(c)
        return begin

    def litname():
        value = ''
        c = next(chars)
        while c not in '\004\0 \t\n\r\f()<>[]{}/%':
            value += c
            c = next(chars)
        emit('LITNAME', value)
        chars.push(c)
        return begin

    def name():
        value = ''
        c = next(chars)
        assert c not in '\004\0 \t\n\r\f()<>[]{}/%', c
        while c not in '\004\0 \t\n\r\f()<>[]{}/%':
            value += c
            c = next(chars)
        emit('NAME', value)
        chars.push(c)
        return begin

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
        emit('NUMBER', value)
        chars.push(c)
        return begin



    state = begin
    chars = PushBackIter(source)

    while state:
        state = state()
    return tokens

tokens = scanps(open('testfiles/region.ps').read())

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

interpreter = Interpreter()
for t in tokens:
    interpreter.read_token(*t)

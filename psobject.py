class PSObject:
    def __init__(self, type, value, literal):
        self.type = type
        self.value = value
        self.literal = literal

    def __repr__(self):
        return f'{self.__class__.__name__}({self.type!r}, {self.value!r}, {self.literal!r})'

    def __str__(self):
        if self.type == 'arraytype':
            if len(self.value) > 4:
                value = self.value[:2] + ['...'] + self.value[-2:]
            else:
                value = self.value
            if self.literal:
                return '[' + ', '.join(map(str, value)) + ']'
            else:
                return '{' + ', '.join(map(str, value)) + '}'
        if self.type == 'operatortype':
            return self.value.__name__
        if self.type == 'dicttype':
            return '<< --dict-- >>'
        if self.type == 'stringtype':
            return repr(self.value)
        return str(self.value)

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
        if ttype == 'STRING':
            return cls('stringtype', value, True)
        assert False, f'unknown ttype {ttype}'

from psobject import PSObject

def op_def(ip):
    value = ip.op_stack.pop()
    name = ip.op_stack.pop()
    ip.dict_stack[name.value] = value

def op_save(ip):
    ip.op_stack.append(PSObject('savetype', None, True))

def op_restore(ip):
    ip.op_stack.pop()

def op_begin(ip):
    ip.dict_stack.push(ip.op_stack.pop().value)

def op_end(ip):
    ip.dict_stack.pop()

def op_bind(ip):
    pass

def op_mul(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', a*b, True))

def op_add(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', a+b, True))

def op_sub(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', a-b, True))

def op_neg(ip):
    a = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', -a, True))

def op_round(ip):
    a = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', int(a+0.5), True))

def op_abs(ip):
    a = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', abs(a), True))

def op_div(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', a/b, True))

def op_ge(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(ip.bool(a>=b))

def op_gt(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(ip.bool(a>b))

def op_lt(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(ip.bool(a<b))

def op_le(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(ip.bool(a<=b))

def op_ne(ip):
    b = ip.op_stack.pop().value
    a = ip.op_stack.pop().value
    ip.op_stack.append(ip.bool(a!=b))

def makearray(ip):
    i = -1
    while ip.op_stack[i] is not ip.mark:
        i -= 1
    arr = PSObject('arraytype', ip.op_stack[i+1:], True)
    ip.op_stack[i:] = [arr]
globals()['op_]'] = makearray

def op_string(ip):
    ip.op_stack.append(PSObject('stringtype', '\x00'*ip.op_stack.pop().value, False))

def op_if(ip):
    b = ip.op_stack.pop()
    a = ip.op_stack.pop().value
    if a:
        ip.ex_stack.append(iter(b.value))

def op_ifelse(ip):
    c = ip.op_stack.pop()
    b = ip.op_stack.pop()
    a = ip.op_stack.pop().value
    if a:
        ip.ex_stack.append(iter(b.value))
    else:
        ip.ex_stack.append(iter(c.value))

def op_pop(ip):
    ip.op_stack.pop()

def op_dup(ip):
    ip.op_stack.append(ip.op_stack[-1])

def op_exch(ip):
    c = ip.op_stack.pop()
    b = ip.op_stack.pop()
    ip.op_stack.append(c)
    ip.op_stack.append(b)

def op_roll(ip):
    j = ip.op_stack.pop().value
    n = ip.op_stack.pop().value
    j %= n
    ip.op_stack[-n:] = ip.op_stack[-j:] + ip.op_stack[-n:-j]

def op_length(ip):
    ip.op_stack.append(PSObject('integertype', len(ip.op_stack.pop().value), True))

def op_getinterval(ip):
    a = ip.op_stack.pop()
    b = ip.op_stack.pop().value
    c = ip.op_stack.pop().value
    ip.op_stack.append(PSObject(a.type, a.value[b:b+c], a.literal))

def op_for(ip):
    proc = ip.op_stack.pop()
    limit = ip.op_stack.pop().value
    increment = ip.op_stack.pop().value
    initial = ip.op_stack.pop().value
    for_exec = (x for i in range(initial, limit+1, increment) for x in (
                    PSObject('integertype', i, True), proc, PSObject('operatortype', op_exec, False)))
    ip.ex_stack.append(iter(for_exec))

def op_forall(ip):
    proc = ip.op_stack.pop()
    container = ip.op_stack.pop()
    if container.type == 'dicttype':
        for_exec = (x for key, value in container.value.items() for x in (
                        PSObject('nametype', key, True), value, proc, PSObject('operatortype', op_exec, False)))
    else:
        for_exec = (x for value in container.value for x in (
                        value, proc, PSObject('operatortype', op_exec, False)))
    ip.ex_stack.append(iter(for_exec))

def op_exec(ip):
    proc = ip.op_stack.pop()
    ip.ex_stack.append(iter(proc.value))

def op_index(ip):
    n = ip.op_stack.pop().value
    item = ip.op_stack[-n-1]
    # print(f'# op_index {n=} -> {item!r}')
    ip.op_stack.append(item)

def op_cvn(ip):
    s = ip.op_stack.pop()
    ip.op_stack.append(PSObject('nametype', s.value, s.literal))

def op_cvx(ip):
    s = ip.op_stack.pop()
    ip.op_stack.append(PSObject(s.type, s.value, False))

def op_load(ip):
    key = ip.op_stack.pop().value
    ip.op_stack.append(ip.dict_stack[key])

def op_copy(ip):
    n = ip.op_stack.pop()
    if n.type in ('integertype', 'realtype'):
        ip.op_stack.extend(ip.op_stack[-n.value:])
    else:
        m = ip.op_stack.pop()
        assert m.type == n.type
        if n.type == 'arraytype':
            assert len(n.value) >= len(m.value)
            n.value[:len(m.value)] = m.value
            ip.op_stack.append(PSObject('arraytype', n.value[:len(m.value)], n.literal))
        else:
            assert False
def op_type(ip):
    ip.op_stack.append(PSObject('nametype', ip.op_stack.pop().type, False))

from psobject import PSObject

def op_dict(ip):
    capacity = ip.op_stack.pop() #ignore
    ip.op_stack.append(PSObject('dicttype', {}, True))

def op_where(ip):
    key = ip.op_stack.pop().value
    #print('where', key)
    #breakpoint()
    d = ip.dict_stack.where(key)
    if d is None:
        ip.op_stack.append(ip.false)
    else:
        ip.op_stack.append(PSObject('dicttype', d, True))
        ip.op_stack.append(ip.true)

def op_known(ip):
    a = ip.op_stack.pop().value
    b = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('realtype', a in b, True))

def op_put(ip):
    any = ip.op_stack.pop()
    key = ip.op_stack.pop().value
    coll = ip.op_stack.pop()
    if coll.type == 'stringtype':
        coll.value = coll.value[:key] + chr(any.value) + coll.value[key+1:]
    elif coll.type == 'arraytype':
        coll.value[key] = any
    elif coll.type == 'dicttype':
        coll.value[key] = any
    else:
        assert False

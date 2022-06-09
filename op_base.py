def op_def(ip):
    value = ip.op_stack.pop()
    name = ip.op_stack.pop()
    ip.dict_stack[name.value] = value

def op_save(ip):
    ip.op_stack.append('save')

def op_restore(ip):
    ip.op_stack.pop()

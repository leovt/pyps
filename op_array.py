from psobject import PSObject

def op_array(ip):
    size = ip.op_stack.pop().value
    ip.op_stack.append(PSObject('arraytype', [ip.null] * size, True))

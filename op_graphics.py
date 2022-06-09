def op_setfont(ip):
    font = ip.op_stack.pop()

def op_setrgbcolor(ip):
    blue = ip.op_stack.pop()
    green = ip.op_stack.pop()
    red = ip.op_stack.pop()

def op_newpath(ip):
    print('newpath')
    pass

def op_moveto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    print(f'M {x} {y}')

def op_lineto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    print(f'L {x} {y}')

def op_stroke(ip):
    pass

def op_showpage(ip):
    pass

def op_setfont(ip):
    font = ip.op_stack.pop()

def op_setrgbcolor(ip):
    blue = ip.op_stack.pop().value
    green = ip.op_stack.pop().value
    red = ip.op_stack.pop().value
    ip.graphics_state.color_space = 'DeviceRGB'
    ip.graphics_state.color = (red, green, blue)

def op_newpath(ip):
    ip.graphics_state.current_path = []

def op_moveto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    ip.graphics_state.current_path.append([('M', x, y)])

def op_lineto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    ip.graphics_state.current_path[-1].append(('L', x, y))

def op_stroke(ip):
    ip.page_device.stroke(ip.graphics_state)
    ip.graphics_state.current_path = []

def op_showpage(ip):
    ip.page_device.showpage(ip.graphics_state)

from psobject import PSObject

def op_setrgbcolor(ip):
    blue = ip.op_stack.pop().value
    green = ip.op_stack.pop().value
    red = ip.op_stack.pop().value
    ip.graphics_state.color_space = 'DeviceRGB'
    ip.graphics_state.color = (red, green, blue)

def op_setgray(ip):
    gray = ip.op_stack.pop().value
    ip.graphics_state.color_space = 'DeviceGray'
    ip.graphics_state.color = (gray, gray, gray)

def op_newpath(ip):
    ip.graphics_state.newpath()

def op_moveto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    ip.graphics_state.moveto(x, y)

def op_rmoveto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    ip.graphics_state.rmoveto(x, y)

def op_lineto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    ip.graphics_state.lineto(x, y)

def op_rlineto(ip):
    y = ip.op_stack.pop().value
    x = ip.op_stack.pop().value
    ip.graphics_state.rlineto(x, y)

def op_closepath(ip):
    ip.graphics_state.closepath()

def op_stroke(ip):
    ip.page_device.stroke(ip.graphics_state)
    ip.graphics_state.current_path = []

def op_fill(ip):
    ip.page_device.fill(ip.graphics_state)
    ip.graphics_state.current_path = []

def op_showpage(ip):
    ip.page_device.showpage(ip.graphics_state)

def op_scale(ip):
    if ip.op_stack[-1].type == 'arraytype':
        matrix = ip.op_stack.pop()
        sy = ip.op_stack.pop().value
        sx = ip.op_stack.pop().value
        ip.op_stack.append(matrix)
        assert False
    else:
        sy = ip.op_stack.pop().value
        sx = ip.op_stack.pop().value
        a,b,c,d,tx,ty = ip.graphics_state.CTM
        ip.graphics_state.CTM = [sx*a,sx*b,sy*c,sy*d,tx,ty]
        print(f'scale {sx=} {sy=} -> {ip.graphics_state.CTM}')

def op_translate(ip):
    if ip.op_stack[-1].type == 'arraytype':
        matrix = ip.op_stack.pop()
        ty = ip.op_stack.pop().value
        tx = ip.op_stack.pop().value
        ip.op_stack.append(matrix)
        assert False
    else:
        ty = ip.op_stack.pop().value
        tx = ip.op_stack.pop().value
        a,b,c,d,tx0,ty0 = ip.graphics_state.CTM
        ip.graphics_state.CTM = [a,b,c,d,a*tx+c*ty+tx0, b*tx+d*ty+ty0]
        print(f'translate {tx=} {ty=} -> {ip.graphics_state.CTM}')

def op_transform(ip):
    if ip.op_stack[-1].type == 'arraytype':
        matrix = ip.op_stack.pop()
        y = ip.op_stack.pop().value
        x = ip.op_stack.pop().value
        ip.op_stack.append(x)
        ip.op_stack.append(y)
        assert False
    else:
        y = ip.op_stack.pop().value
        x = ip.op_stack.pop().value
        x,y = ip.graphics_state.transform(x,y)
        ip.op_stack.append(PSObject('realtype', x, True))
        ip.op_stack.append(PSObject('realtype', y, True))

def op_itransform(ip):
    if ip.op_stack[-1].type == 'arraytype':
        matrix = ip.op_stack.pop()
        y = ip.op_stack.pop().value
        x = ip.op_stack.pop().value
        ip.op_stack.append(x)
        ip.op_stack.append(y)
        assert False
    else:
        y = ip.op_stack.pop().value
        x = ip.op_stack.pop().value
        x,y = ip.graphics_state.itransform(x,y)
        ip.op_stack.append(PSObject('realtype', x, True))
        ip.op_stack.append(PSObject('realtype', y, True))

def op_matrix(ip):
    zero = PSObject('realtype', 0.0, True)
    one = PSObject('realtype', 1.0, True)
    ip.op_stack.append(PSObject('arraytype', [one, zero, zero, one, zero, zero], True))

def op_currentmatrix(ip):
    ip.op_stack[-1].value = [PSObject('realtype', x, True) for x in ip.graphics_state.CTM]

def op_setmatrix(ip):
    mat = ip.op_stack.pop()
    ip.graphics_state.CTM = [x.value for x in mat.value]
    print(f'setmatrix -> {ip.graphics_state.CTM}')

def op_gsave(ip):
    ip.gsave()
    print('gsave !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

def op_grestore(ip):
    ip.grestore()
    print('restore !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

def op_imagemask(ip):
    d = ip.op_stack.pop()
    if d.type == 'dicttype':
        raise NotImplementedError
    else:
        datasrc = d
        matrix = ip.op_stack.pop()
        polarity = ip.op_stack.pop()
        height = ip.op_stack.pop().value
        width = ip.op_stack.pop().value

    imagedata = ''
    while True:
        ip.execsub(iter(datasrc.value))
        ret = ip.op_stack.pop().value
        if not ret:
            break
        imagedata += ret
        if len(imagedata)*8 >= width*height:
            break
    breakpoint()

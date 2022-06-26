from psobject import PSObject
import svgdevice

class Font:
    def __init__(self, fontdict, metrics):
        self.fontdict = fontdict
        self.metrics = metrics
        self.scale = 1

def stringwidth(fontdict, text):
    return 5*len(text)

def op_show(ip):
    text = ip.op_stack.pop().value
    gs = ip.graphics_state
    #x,y = gs.current_pointip.graphics_state
    #x += stringwidth(gs.font, text)
    #gs.current_point = (x, y)
    ip.page_device.show(text, gs)

def op_findfont(ip):
    font = ip.op_stack[-1]
    print(f'findfont {font=}')

def op_scalefont(ip):
    scale = ip.op_stack.pop()
    font = ip.op_stack.pop()
    print(f'scalefont {scale=}')
    sm = font.value.get('ScaleMatrix', 1)
    sm *= scale
    font.value['ScaleMatrix'] = sm
    ma = list(font.value['FontMatrix'])
    ma[0] *= scale
    ma[3] *= scale
    font.value['FontMatrix'] = ma

def op_definefont(ip):
    from op_base import op_exec
    font = ip.op_stack.pop()
    key = ip.op_stack.pop()
    FontType = font.value.get('FontType', ip.null).value
    FontMatrix = font.value.get('FontMatrix', ip.null).value
    FontName = font.value.get('FontName', ip.null).value
    print(f'definefont {FontType=} {FontName=}')
    metrics = []
    glyphs = []

    originaldevice = ip.page_device

    def op_setcachedevice(ip):
        ury = ip.op_stack.pop().value
        urx = ip.op_stack.pop().value
        lly = ip.op_stack.pop().value
        llx = ip.op_stack.pop().value
        wy = ip.op_stack.pop().value
        wx = ip.op_stack.pop().value
        metrics.append((wx,wy,llx,lly,urx,ury))
        glyphdevice = svgdevice.GlyphDevice()
        glyphs.append(glyphdevice)

    def op_endfont(ip):
        r = ip.dict_stack.pop()
        ip.page_device = originaldevice
        fid = next(ip.ids)
        font.value['FID'] = PSObject('fonttype', fid, True)
        fontobj = Font(font, metrics)
        ip.fonts[fid] = fontobj
        ip.op_stack.append(font)
        for i, glyph in enumerate(glyphs):
            glyph.showpage(ip.graphics_state)

            fname = f'fonts/font_{fid}_glyph_{i:03d}.svg'
            import os
            os.mkdirs('fonts')
            print(fname, os.path.abspath(fname))
            glyph.write(fname)



    proc = font.value['BuildChar']

    ip.dict_stack.push({'setcachedevice': PSObject('operatortype', op_setcachedevice, False)})
    for_exec = (x for i,charname in enumerate(font.value['base'].value) for x in (
                                font, PSObject('integertype', i, True), proc, PSObject('operatortype', op_exec, False)))
    ip.ex_stack.append(iter([PSObject('operatortype', op_endfont, False)]))
    ip.ex_stack.append(iter(for_exec))

def op_setfont(ip):
    font = ip.op_stack.pop()
    FontType = font.value.get('FontType', ip.null).value
    FontMatrix = font.value.get('FontMatrix', ip.null).value
    FontName = font.value.get('FontName', ip.null).value
    print(f'setfont {FontType=} {FontName=}')
    ip.graphics_state.font = font

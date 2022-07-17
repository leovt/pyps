from psobject import PSObject
#import svgdevice
import cffdevice
import makefont

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
    ip.gsave()
    ip.graphics_state.CTM = [x.value for x in FontMatrix]

    def op_setcachedevice(ip):
        ury = ip.op_stack.pop().value
        urx = ip.op_stack.pop().value
        lly = ip.op_stack.pop().value
        llx = ip.op_stack.pop().value
        wy = ip.op_stack.pop().value
        wx = ip.op_stack.pop().value
        metrics.append((wx,wy,llx,lly,urx,ury))
        glyphdevice = cffdevice.CFFDevice()
        glyphs.append(glyphdevice)
        ip.page_device = glyphdevice

    def op_endfont(ip):
        r = ip.dict_stack.pop()
        ip.grestore()
        ip.page_device = originaldevice
        fid = next(ip.ids)
        font.value['FID'] = PSObject('fonttype', fid, True)
        fontobj = Font(font, metrics)
        fontobj.ttx = makefont.Font()
        fontobj.ttx.family_name = f'FID{fid}'
        fontobj.ttx.font_matrix = ' '.join(str(x.value) for x in font.value['FontMatrix'].value)
        ip.fonts[fid] = fontobj
        ip.op_stack.append(font)
        for i, (glyph, mtx) in enumerate(zip(glyphs,metrics)):
            glname = makefont.glyphname.get(i, f'glyph{i:04x}')
            cs = f'{mtx[0]} {" ".join(glyph.current_page)} endchar'
            fontobj.ttx.glyphs.append(makefont.Glyph(name=glname, code_point=i, width=mtx[0], lsb=mtx[2], charstring=cs))
            print(glname)
        with open(f'fonts/FID{fid}.ttx', 'w') as f:
            fontobj.ttx.write_ttx(f)
        breakpoint()


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

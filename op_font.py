from psobject import PSObject
import svgdevice
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
    key = ip.op_stack.pop()
    print(f'findfont {key=}')
    ip.op_stack.append(ip.fonts[key])

def op_scalefont(ip):
    scale = ip.op_stack.pop().value
    font = ip.op_stack[-1] #TODO: should we make a copy instead of modifying in place?
    print(f'scalefont {scale=}')
    sm = font.value.get('ScaleMatrix', 1)
    sm *= scale
    font.value['ScaleMatrix'] = sm
    ma = font.value['FontMatrix'].value
    ma[0].value *= scale
    ma[3].value *= scale

def op_definefont(ip):
    from op_base import op_exec
    font = ip.op_stack.pop()
    key = ip.op_stack.pop()
    FontType = font.value.get('FontType', ip.null).value
    FontMatrix = font.value.get('FontMatrix', ip.null).value
    FontName = font.value.get('FontName', ip.null).value
    print(f'definefont {FontType=} {FontName=}')

    encoding = [x.value for x in font.value['Encoding'].value]
    glyph_encoding = [(cp, name) for (cp, name) in enumerate(encoding) if name != '.notdef']
    if '.notdef' in encoding:
        glyph_encoding.insert(0, (None, '.notdef'))
    metrics = []
    glyphs = []

    originaldevice = ip.page_device
    ip.gsave()
    ip.graphics_state.CTM = [1, 0, 0, 1, 0, 0]

    def op_setcachedevice(ip):
        ury = ip.op_stack.pop().value
        urx = ip.op_stack.pop().value
        lly = ip.op_stack.pop().value
        llx = ip.op_stack.pop().value
        wy = ip.op_stack.pop().value
        wx = ip.op_stack.pop().value
        metrics.append((wx,wy,llx,lly,urx,ury))
        #glyphdevice = svgdevice.GlyphDevice()
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

        filename_base = f'fonts/FID{fid}'
        filename_ttx = filename_base + '.ttx'
        filename_woff = filename_base + '.woff'
        font.value['*filename*'] = filename_woff
        font.value['*family*'] = f'FID{fid}'

        ip.fonts[key] = font
        ip.op_stack.append(font)

        for (cp, name), glyph, mtx in zip(glyph_encoding, glyphs, metrics):
            cs = f'{mtx[0]} {" ".join(glyph.current_page)} endchar'
            fontobj.ttx.add_glyph(makefont.Glyph(name=name, code_point=cp, width=mtx[0], lsb=mtx[2], charstring=cs))
            print(cp, name)

        em = 4 * fontobj.ttx.avg_char_width() # rule of thumb for latin

        with open(filename_ttx, 'w') as f:
            fontobj.ttx.write_ttx(f)
        from fontTools import ttLib
        tt = ttLib.TTFont(flavor='woff')
        tt.importXML(filename_ttx)
        tt.save(filename_woff)

    ip.dict_stack.push({'setcachedevice': PSObject('operatortype', op_setcachedevice, False)})

    breakpoint()

    if 'BuildGlyph' in font.value:
        proc = font.value['BuildGlyph']
        for_exec = (x for cp, name in glyph_encoding for x in (
                                    font, PSObject('nametype', name, True), proc, PSObject('operatortype', op_exec, False)))
    else:
        proc = font.value['BuildChar']
        for_exec = (x for cp, name in glyph_encoding for x in (
                                    font, PSObject('integertype', cp, True), proc, PSObject('operatortype', op_exec, False)))
    ip.ex_stack.append(iter([PSObject('operatortype', op_endfont, False)]))
    ip.ex_stack.append(iter(for_exec))


def op_setfont(ip):
    font = ip.op_stack.pop()
    FontType = font.value.get('FontType', ip.null).value
    FontMatrix = font.value.get('FontMatrix', ip.null).value
    FontName = font.value.get('FontName', ip.null).value
    print(f'setfont {FontType=} {FontName=}')
    ip.graphics_state.font = font

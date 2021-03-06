import os
import html
import re
import io
import binascii

import png
import bmoutline
from png import widen_bytes

def escape(txt):
    return html.escape(re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', txt))

def svgpath(sp):
    if sp[0] == 'Z':
        return 'Z'
    else:
        t,(x,y) = sp
        return f'{t} {x} {841.9-y}'

class SVGDevice:
    def __init__(self):
        self.pages = []
        self.current_page = []
        self.options = {'imagemask_as_png': False, 'draw_glyphs': False}
        self.used_fonts = {}

    def showpage(self, gs):
        self.pages.append(self.current_page)
        self.current_page = []

    def stroke(self, gs):
        gs.current_path.transform(1, 0, 0, -1, 0, 841.9)
        d = gs.current_path.svg()
        r,g,b = gs.color
        color = f'rgb({100*r}%, {100*g}%, {100*b}%)'
        self.current_page.append(f'<path d="{d}" fill="None" stroke="{color}" stroke-width="{gs.line_width}"/>')

    def fill(self, gs):
        gs.current_path.transform(1, 0, 0, -1, 0, 841.9)
        d = gs.current_path.svg()
        r,g,b = gs.color
        color = f'rgb({100*r}%, {100*g}%, {100*b}%)'
        self.current_page.append(f'<path d="{d}" fill="{color}"/>')

    def show(self, text, gs):
        if self.options['draw_glyphs']:
            x,y = gs.transform(*gs.current_point)

        else:
            family = gs.font.value['*family*']
            self.used_fonts[family] = gs.font.value['*filename*']
            x,y = gs.transform(*gs.current_point)
            #breakpoint()
            s = gs.font.value.get('ScaleMatrix', 1)
            self.current_page.append(f'<text x="{x}" y="{841.9-y}" font-size="{s}" font-family="{family}">{escape(text)}</text>')
            gs.current_point = (x+5*len(text), y)

    def imagemask(self, size, imagedata, pivot, matrix, gs):
        orig = imagedata
        if not pivot:
            imagedata = bytes(255-x for x in imagedata)
        CTM = ' '.join(map(str, gs.CTM))
        a,b,c,d,e,f = matrix
        det = a*d-b*c
        IMA = (d/det, -b/det, -c/det, a/det, (c*f-d*e)/det, (b*e-a*f)/det)
        IMA = ' '.join(map(str, IMA))
        if self.options['imagemask_as_png']:
            bio = io.BytesIO()
            png.png_mask(bio, *size, imagedata)
            b64 = binascii.b2a_base64(bio.getvalue(), newline=False).decode('ascii')
            imageurl = f'data:image/png;base64,{b64}'
            self.current_page.append(f'<image width="{size[0]}" height="{size[1]}" href="{imageurl}" transform="scale(1 -1) translate(0 -841.9) matrix({CTM}) matrix({IMA})" />')
        else:
            width, height = size
            stride = (width+7)//8
            bitmap = [list(widen_bytes(imagedata[i:i+stride]))[:width] for i in range(0,stride*height,stride)]
            path = bmoutline.edges(bitmap)
            self.current_page.append(f'<path d="{path.svg()}" transform="scale(1 -1) translate(0 -841.9) matrix({CTM}) matrix({IMA})" />')
        self.current_page.append(f'<!-- original data {orig!r}-->')


    def write(self, fname):
        root, ext = os.path.splitext(fname)
        digits = len(str(len(self.pages)))
        for page_no, page in enumerate(self.pages, 1):
            if len(self.pages) == 1:
                fname_page = fname
            else:
                fname_page = f'{root}_{page_no:0{digits}d}{ext}'
            with open(fname_page, 'w') as f:
                f.write('<svg'
                        ' xmlns="http://www.w3.org/2000/svg"'
                        ' width="210mm"'
                        ' height="297mm"'
                        ' viewBox="0 0 595.3 841.9"'
                        #' transform="translate(0, 841.9) scale(1, -1)"'
                        '>\n')
                if self.used_fonts:
                    f.write('  <style>\n')
                    for family, filename in self.used_fonts.items():
                        f.write(f'    @font-face{{font-family: "{family}"; src: url("{filename}")}};\n')
                    f.write('  </style>\n')
                for element in page:
                    f.write(f'  {element}\n')
                f.write('</svg>\n')

class GlyphDevice(SVGDevice):
    pass

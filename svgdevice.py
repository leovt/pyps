import os
import html
import re
import io
import binascii

import png

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

    def showpage(self, gs):
        self.pages.append(self.current_page)
        self.current_page = []

    def stroke(self, gs):
        d = ' '.join(svgpath(p) for subpath in gs.current_path
                for p in subpath)
        r,g,b = gs.color
        color = f'rgb({100*r}%, {100*g}%, {100*b}%)'
        self.current_page.append(f'<path d="{d}" fill="None" stroke="{color}" stroke-width="{gs.line_width}"/>')

    def fill(self, gs):
        d = ' '.join(svgpath(p) for subpath in gs.current_path
                for p in subpath)
        r,g,b = gs.color
        color = f'rgb({100*r}%, {100*g}%, {100*b}%)'
        self.current_page.append(f'<path d="{d}" fill="{color}"/>')

    def show(self, text, gs):
        x,y = gs.transform(*gs.current_point)
        #breakpoint()
        s = gs.font.value.get('ScaleMatrix', 1)
        s = 8
        self.current_page.append(f'<text x="{x}" y="{841.9-y}" font-size="{s}">{escape(text)}</text>')
        gs.current_point = (x+5*len(text), y)

    def imagemask(self, size, imagedata, pivot, matrix, gs):
        orig = imagedata
        if not pivot:
            imagedata = bytes(255-x for x in imagedata)
        bio = io.BytesIO()
        png.png_mask(bio, *size, imagedata)
        b64 = binascii.b2a_base64(bio.getvalue(), newline=False).decode('ascii')
        imageurl = f'data:image/png;base64,{b64}'
        CTM = ' '.join(map(str, gs.CTM))
        a,b,c,d,e,f = matrix
        det = a*d-b*c
        IMA = (d/det, -b/det, -c/det, a/det, (c*f-d*e)/det, (b*e-a*f)/det)
        IMA = ' '.join(map(str, IMA))
        self.current_page.append(f'<image width="{size[0]}" height="{size[1]}" href="{imageurl}" transform="scale(1 -1) translate(0 -841.9) matrix({CTM}) matrix({IMA}) scale(1 -1) translate(0 -{size[1]})" />')
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

                for element in page:
                    f.write(f'  {element}\n')
                f.write('</svg>\n')

class GlyphDevice(SVGDevice):
    pass

import os

class SVGDevice:
    def __init__(self):
        self.pages = []
        self.current_page = []

    def showpage(self, gs):
        self.pages.append(self.current_page)
        self.current_page = []

    def stroke(self, gs):
        d = ' '.join(str(t) for subpath in gs.current_path
                for segment in subpath
                for t in segment)
        r,g,b = gs.color
        color = f'rgb({100*r}%, {100*g}%, {100*b}%)'
        self.current_page.append(f'<path d="{d}" fill="None" stroke="{color}" stroke-width="{gs.line_width}"/>')

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
                        ' transform="translate(0, 841.9) scale(1, -1)"'
                        '>\n')

                for element in page:
                    f.write(f'  {element}\n')
                f.write('</svg>\n')

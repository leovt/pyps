'''
variables in template.ttx

{created_dt}
{avg_char_width}
{ascent}
{descent}
{line_gap}
{win_ascent}
{win_descent}
{family_name}
{unique_id}
{glyph_id_tags}
{unicode_map_tags}
{charstring_tags}
{mtx_tags}
'''

import datetime
import uuid
from dataclasses import dataclass

glyphname = {}
with open('glyphlist.txt') as f:
    for line in f:
        if line.startswith('#'):
            continue
        name, codepoint = line.split(';')
        codepoint = int(codepoint.strip().replace(' ', ''), 16)
        if codepoint in glyphname:
            print(f'another name for {codepoint:04X} {glyphname[codepoint]} - {name}')
        else:
            glyphname[codepoint] = name.strip()

@dataclass
class Glyph:
    name: str
    code_point: int
    charstring: str
    width: int
    lsb: int

    def glyph_id_tag(self):
        return f'<GlyphID name="{self.name}"/>'

    def unicode_map_tag(self):
        if self.code_point is None:
            return ''
        return f'<map code="0x{self.code_point:x}" name="{self.name}"/>'


    def charstring_tag(self):
        return f'<CharString name="{self.name}">{self.charstring}</CharString>'

    def mtx_tag(self):
        return f'<mtx name="{self.name}" width="{self.width}" lsb="{self.lsb}"/>'

class Font:
    template_path = 'template.ttx'

    def __init__(self):
        self.glyphs = []

    def add_glyph(self, glyph):
        if self.glyphs and glyph.name == '.notdef':
            assert False, '.notdef must be the first glyph in the font.'

        if not self.glyphs and glyph.name != '.notdef':
            # add a .notdef glyph if none is defined already
            notdef = Glyph(name='.notdef', code_point=None, width=500, lsb=50, charstring='500 450 hmoveto 750 -400 -750 vlineto 50 50 rmoveto 650 300 -650 vlineto endchar')
            self.glyphs = [notdef]
        self.glyphs.append(glyph)

    def template(self):
        with open(self.template_path) as f:
            return f.read()

    def avg_char_width(self):
        nonzero_width_glyph_count = sum(1 for g in self.glyphs if g.width)
        total_glyph_width = sum(g.width for g in self.glyphs)
        if nonzero_width_glyph_count:
            return total_glyph_width / nonzero_width_glyph_count
        return 0



    def write_ttx(self, f):
        template = self.template()
        fields = {
            'created_dt': datetime.datetime.utcnow(),
            'avg_char_width': int(self.avg_char_width()),
            'ascent': '0',
            'descent': '0',
            'line_gap': '0',
            'win_ascent': '0',
            'win_descent': '0',
            'font_matrix': self.font_matrix,
            'family_name': self.family_name,
            'unique_id': uuid.uuid4(),
            'glyph_id_tags': '\n'.join(g.glyph_id_tag() for g in self.glyphs),
            'unicode_map_tags': '\n'.join(g.unicode_map_tag() for g in self.glyphs),
            'charstring_tags': '\n'.join(g.charstring_tag() for g in self.glyphs),
            'mtx_tags': '\n'.join(g.mtx_tag() for g in self.glyphs),
        }
        f.write(template.format(**fields))

if __name__ == '__main__':
    font = Font()
    font.family_name = 'F1'
    font.font_matrix = '0.001 0 0 0.001 0 0'
    font.glyphs.append(Glyph(name='A', code_point=0x41, width=450, lsb=50,
        charstring='''450 50 50 rmoveto
150 50 -50 50 200 -50 -50 -50 150 50 -50 150 -50 100 -50 150 -50 -150 -50 -100 -50 -100 -50 -50 -50 -50 hlineto
150 150 rmoveto
50 50 100 50 -100 50 -50 -150 vlineto
endchar'''))
    font.glyphs.append(Glyph(name='F', code_point=0x46, width=450, lsb=50,
        charstring='''450 50 50 rmoveto
150 50 -50 150 50 -50 50 150 -50 -50 -50 150 150 -50 50 100 -300 -50 50 -350 -50 hlineto
endchar'''))
    with open('F1.ttx', 'w') as f:
        font.write_ttx(f)

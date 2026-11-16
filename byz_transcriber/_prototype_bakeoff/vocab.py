"""PROTOTYPE (throwaway): component vocabulary, quantity/slot tables, Glyph->Group assembly, .byzx export.

Shapes follow decision "Printed glyph vocabulary and Neanes mapping table" (#82): atomic components,
optional position relative to parent, two tables, one `dot`, whole-unit mode_key. Only the subset seen in
the bake-off sample is tabled; anything else -> unmapped_combo.
"""
import json

BASES = {'ison', 'oligon', 'petasti', 'apostrophos', 'elaphron', 'chamili', 'yporroi', 'running_elaphron'}
QUANTITY_ATTACH = {'kentima', 'kentimata', 'ypsili', 'apostrophos', 'elaphron', 'chamili', 'yporroi',
                   'running_elaphron', 'ison', 'oligon'}  # neumes stacked on oligon/petasti
SLOT = {'klasma', 'gorgon', 'digorgon', 'trigorgon', 'argon', 'apli', 'dipli', 'tripli', 'vareia', 'psifiston',
        'omalon', 'heteron', 'antikenoma', 'endofonon', 'dot', 'diesis', 'yfesis'}
MARTYRIA_NOTES = {'m_ni', 'm_pa', 'm_vou', 'm_ga', 'm_di', 'm_ke', 'm_zo'}
MARTYRIA_ROOTS = {'r_alpha', 'r_delta', 'r_legetos', 'r_nana', 'r_varys', 'r_tilt', 'r_squiggle'}

# quantity table: (base, frozenset((component, position))) -> QuantitativeNeume
Q = {}
def q(base, enum, *att):
    Q[(base, frozenset(att))] = enum
for b, e in [('ison', 'Ison'), ('oligon', 'Oligon'), ('petasti', 'Petasti'), ('apostrophos', 'Apostrophos'),
             ('elaphron', 'Elaphron'), ('chamili', 'Hamili'), ('yporroi', 'Hyporoe'),
             ('running_elaphron', 'RunningElaphron')]:
    q(b, e)
q('apostrophos', 'ElaphronPlusApostrophos', ('elaphron', 'right'))
q('elaphron', 'ElaphronPlusApostrophos', ('apostrophos', 'left'))
q('ison', 'IsonPlusApostrophos', ('apostrophos', 'right'))
q('apostrophos', 'DoubleApostrophos', ('apostrophos', 'right'))
q('chamili', 'HamiliPlusApostrophos', ('apostrophos', 'right'))
q('chamili', 'HamiliPlusElaphron', ('elaphron', 'right'))
for base, pre in [('oligon', 'Oligon'), ('petasti', 'Petasti')]:
    q(base, pre + 'PlusKentimaAbove', ('kentima', 'above'))
    q(base, pre + 'PlusHypsiliRight', ('ypsili', 'right'))
    q(base, pre + 'PlusHypsiliLeft', ('ypsili', 'left'))
    q(base, pre + 'PlusHypsiliPlusKentimaHorizontal', ('ypsili', 'right'), ('kentima', 'left'))
    q(base, pre + 'PlusHypsiliPlusKentimaVertical', ('ypsili', 'above'), ('kentima', 'above'))
    for n, nm in [('ison', 'Ison'), ('apostrophos', 'Apostrophos'), ('elaphron', 'Elaphron'),
                  ('chamili', 'Hamili'), ('yporroi', 'Hyporoe'), ('running_elaphron', 'RunningElaphron')]:
        e = {'Ison': pre + 'PlusIson' if base == 'oligon' else 'PetastiWithIson',
             'Hamili': pre + ('PlusHamili' if base == 'oligon' else 'Hamili')}.get(nm, pre + 'Plus' + nm)
        q(base, e, (n, 'above'))
    q(base, pre + 'PlusHyporoe', ('yporroi', 'below'))
    q(base, pre + 'PlusElaphronPlusApostrophos', ('elaphron', 'above'), ('apostrophos', 'above'))
q('petasti', 'PetastiPlusOligon', ('oligon', 'above'))
q('oligon', 'OligonPlusKentimaBelow', ('kentima', 'below'))
q('oligon', 'OligonPlusKentemata', ('kentimata', 'above'))
q('oligon', 'KentemataPlusOligon', ('kentimata', 'left'))
q('oligon', 'OligonPlusApostrophosPlusKentemata', ('apostrophos', 'above'), ('kentimata', 'above'))
q('oligon', 'OligonPlusElaphronPlusKentemata', ('elaphron', 'above'), ('kentimata', 'above'))
q('oligon', 'OligonPlusHyporoePlusKentemata', ('yporroi', 'above'), ('kentimata', 'above'))
q('oligon', 'OligonPlusIsonPlusKentemata', ('ison', 'above'), ('kentimata', 'above'))
q('oligon', 'OligonPlusKentemataPlusHypsiliRight', ('kentimata', 'above'), ('ypsili', 'right'))
q('oligon', 'OligonPlusKentemataPlusHypsiliLeft', ('kentimata', 'above'), ('ypsili', 'left'))
q('kentimata', 'Kentemata')

# slot table: (component, position) -> (Note field, enum); position None = any
S = {
    ('klasma', 'above'): ('timeNeume', 'Klasma_Top'), ('klasma', 'below'): ('timeNeume', 'Klasma_Bottom'),
    ('apli', None): ('timeNeume', 'Hapli'), ('dipli', None): ('timeNeume', 'Dipli'),
    ('tripli', None): ('timeNeume', 'Tripli'),
    ('gorgon', 'above'): ('gorgonNeume', 'Gorgon_Top'), ('gorgon', 'below'): ('gorgonNeume', 'Gorgon_Bottom'),
    ('digorgon', None): ('gorgonNeume', 'Digorgon'), ('trigorgon', None): ('gorgonNeume', 'Trigorgon'),
    ('argon', None): ('gorgonNeume', 'Argon'),
    ('psifiston', None): ('vocalExpressionNeume', 'Psifiston'),
    ('omalon', None): ('vocalExpressionNeume', 'Homalon'),
    ('heteron', None): ('vocalExpressionNeume', 'Heteron'),
    ('antikenoma', None): ('vocalExpressionNeume', 'Antikenoma'),
    ('endofonon', None): ('vocalExpressionNeume', 'Endofonon'),
    ('diesis', None): ('accidental', 'Sharp_2_Left'), ('yfesis', None): ('accidental', 'Flat_2_Right'),
}
NOTE = {'m_ni': 'Ni', 'm_pa': 'Pa', 'm_vou': 'Vou', 'm_ga': 'Ga', 'm_di': 'Thi', 'm_ke': 'Ke', 'm_zo': 'Zo'}
ROOT = {'r_alpha': 'Alpha', 'r_delta': 'Delta', 'r_legetos': 'Legetos', 'r_nana': 'Nana', 'r_varys': 'Zo',
        'r_tilt': 'Tilt', 'r_squiggle': 'Squiggle'}


def group_to_element(g, thr=0.5):
    """g = dict(base=id, attach=[(id, pos)], conf=float) -> (element, flags)."""
    flags = []
    base, att = g['base'], g.get('attach', [])
    if base == 'martyria':
        n = [a for a, _ in att if a in NOTE]; r = [a for a, _ in att if a in ROOT]
        if not n or not r:
            return {'elementType': 'Martyria', 'auto': True}, ['unmapped_combo']
        return {'elementType': 'Martyria', 'note': NOTE[n[0]], 'rootSign': ROOT[r[0]], 'scale': 'Diatonic'}, flags
    if base == 'unknown':
        return {'elementType': 'Note', 'quantitativeNeume': 'Ison'}, ['low_confidence']
    qatt = frozenset((a, p) for a, p in att if a in QUANTITY_ATTACH and a not in SLOT)
    sat = [(a, p) for a, p in att if a in SLOT]
    el = {'elementType': 'Note'}
    vareia = any(a == 'vareia' for a, _ in sat)
    dots = sum(1 for a, _ in sat if a == 'dot')
    if base == 'vareia_rest':
        el['quantitativeNeume'] = {0: 'VareiaDotted', 1: 'VareiaDotted', 2: 'VareiaDotted2',
                                   3: 'VareiaDotted3'}.get(dots, 'VareiaDotted4')
        return el, flags
    qn = Q.get((base, qatt))
    if qn is None:
        flags.append('unmapped_combo'); qn = Q.get((base, frozenset()), 'Ison')
    el['quantitativeNeume'] = qn
    if vareia:
        el['vareia'] = True
    for a, p in sat:
        if a in ('vareia',):
            continue
        if a == 'dot':
            if dots and 'gorgonNeume' in el:
                el['gorgonNeume'] = el['gorgonNeume'].replace('Gorgon_Top', 'GorgonDottedRight') if p == 'right' \
                    else el['gorgonNeume'].replace('Gorgon_Top', 'GorgonDottedLeft')
            continue
        m = S.get((a, p)) or S.get((a, None))
        if m is None:
            flags.append('unmapped_combo'); continue
        f, v = m
        if f in el:
            flags.append('unmapped_combo'); continue
        el[f] = v
    if g.get('conf', 1) < thr:
        flags.append('low_confidence')
    if g.get('ambiguous'):
        flags.append('ambiguous_attachment')
    return el, flags


def export(groups, path, title, thr=0.5):
    tpl = {
        'version': '1.1', 'appVersion': '0.0.0', 'documentProperties': {'title': title},
        'pageSetup': {'pageSize': 'Letter', 'pageSizeUnit': 'in', 'pageWidth': 816, 'pageHeight': 1056,
                      'topMargin': 96, 'bottomMargin': 96, 'leftMargin': 96, 'rightMargin': 96,
                      'headerMargin': 48, 'footerMargin': 48, 'firstPageNumber': 1},
        'staff': {'lyrics': {'text': ''}, 'elements': []},
    }
    els = tpl['staff']['elements']; nflag = 0
    for g in groups:
        if g.get('linebreak') and els:
            els[-1]['lineBreak'] = True
            continue
        el, flags = group_to_element(g, thr)
        if flags:
            nflag += 1
            el['annotations'] = [{'elementType': 'Annotation', 'x': 0, 'y': -30, 'text': '? ' + ','.join(sorted(set(flags)))}]
        els.append(el)
    els.append({'elementType': 'Empty'})
    json.dump(tpl, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return len([e for e in els if e['elementType'] != 'Empty']), nflag

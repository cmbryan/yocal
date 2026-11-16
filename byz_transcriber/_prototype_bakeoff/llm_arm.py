"""PROTOTYPE: vision-LLM arm. Parses llm/transcripts.txt (Claude's in-session reading) -> groups -> out/llm/<book>.byzx"""
import os, re, json
from vocab import export
CODES = dict(ol='oligon', pe='petasti', is_='ison', ap='apostrophos', el='elaphron', ch='chamili', yp='yporroi',
             re='running_elaphron', ke='kentima', kk='kentimata', ys='ypsili', kl='klasma', go='gorgon',
             dg='digorgon', ar='argon', va='vareia', ps='psifiston', om='omalon', he='heteron', an='antikenoma',
             dt='dot', a1='apli', a2='dipli', X='unknown')
CODES['is'] = 'ison'
POS = dict(a='above', b='below', l='left', r='right')
NOTES = dict(ni='m_ni', pa='m_pa', vou='m_vou', ga='m_ga', di='m_di', ke='m_ke', zo='m_zo')

def parse_group(tok):
    conf = 0.4 if '?' in tok else 0.9
    tok = tok.replace('?', '')
    if tok.startswith('M:'):
        n, r = tok[2:].split('/')
        return dict(base='martyria', attach=[(NOTES[n], None), ('r_' + r, None)], conf=conf)
    parts = tok.split('+')
    att = []
    for p in parts[1:]:
        c, pos = p.split('@')
        att.append((CODES[c], POS[pos]))
    return dict(base=CODES[parts[0]], attach=att, conf=conf)

def load():
    books = {}
    for line in open('llm/transcripts.txt', encoding='utf-8'):
        if line.startswith('#') or not line.strip():
            continue
        key, body = line.split(':', 1)
        book = key.split('-')[0]
        g = books.setdefault(book, [])
        if g:
            g.append(dict(linebreak=True))
        g += [parse_group(t) for t in body.split()]
    return books

if __name__ == '__main__':
    os.makedirs('out/llm', exist_ok=True)
    for book, groups in load().items():
        n, f = export(groups, f'out/llm/{book}.byzx', f'LLM {book}')
        print(book, 'groups', n, 'flagged', f)

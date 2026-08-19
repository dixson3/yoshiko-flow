#!/usr/bin/env python3
"""EXP-003 prototype plan.md EXTRACTOR.

Emits a structured JSON view of a yf-plan plan.md: epics -> issues (with
dependency + upstream edges), gates, success criteria, upstream rows, refs.

Deliberately a *measuring instrument*: it reports what it could not parse
(`unparsed`) rather than silently dropping it.
"""
import json
import re
import sys

# --- section splitting -------------------------------------------------------
H2 = re.compile(r'^##\s+(.+?)\s*$')
H3 = re.compile(r'^###\s+(.+?)\s*$')

# --- epic / issue grammar ----------------------------------------------------
EPIC = re.compile(r'^###\s+(?:\*\*)?Epic\s+([0-9A-Za-z]+)(?:\*\*)?\s*[:—-]\s*(.+?)\s*$')
# tolerate: "- Issue 1.1: ", "- **1.1**: ", "- 1.1: ", "- **Issue 1.1:** ",
#           "- **Issue 1.1: title**", "- Issue A.1: "
ISSUE = re.compile(
    r'^-\s+'
    r'(?:\*\*)?'                       # optional bold open
    r'(?:Issue\s+)?'                   # optional literal "Issue"
    r'(?P<id>[0-9A-Z]+(?:\.[0-9]+[a-z]?)+)'
    r'(?:\*\*)?'                       # optional bold close (before colon)
    # optional parenthetical between id and colon, possibly bolded:
    #   "2.2 (#100):"  /  "C.2 (reconcile step):"
    #   "B.3 **(staged — the self-maintaining tier, red-team C2)**:"
    r'\s*(?:\*\*)?\s*(?:\([^)]{0,90}\))?\s*(?:\*\*)?'
    r'\s*:\s*'
    r'(?P<rest>.*)$'
)
DEPENDS = re.compile(r'depends[- ]on:\s*(?P<val>.+?)\s*$', re.I)
RESOLVES = re.compile(r'resolves[- ]upstream:\s*(?P<val>.+?)\s*$', re.I)
IDREF = re.compile(r'\b([0-9A-Z]+(?:\.[0-9]+[a-z]?)+)\b')
UPNUM = re.compile(r'#(\d+)')

REQ = re.compile(r'\bREQ-[A-Z0-9]+-[0-9]+[a-z]?\b')
FILELINE = re.compile(r'([\w./\-]+\.(?:py|md|rs|toml|sh|json|yaml|yml)):(\d+)')

GATE_TITLE = re.compile(r'gate', re.I)
FIELD = re.compile(
    r'^\s*-?\s*\*{0,2}(Type|Approvers|Condition|Test|test_class|cwd|Blocks|Instructions)'
    r'\*{0,2}\s*:\s*(.*)$', re.I)


def strip_md(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    return s.strip()


def split_sections(lines):
    """Return {h2_title: (start, end)} over the *body* lines (fence-aware)."""
    out, cur, start, fence = {}, None, 0, False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith('```'):
            fence = not fence
            continue
        if fence:
            continue
        m = H2.match(ln)
        if m:
            if cur is not None:
                out.setdefault(cur, (start, i))
            cur, start = m.group(1), i + 1
    if cur is not None:
        out.setdefault(cur, (start, len(lines)))
    return out


def find_section(secs, *names):
    for n in names:
        for k in secs:
            if k.strip().lower() == n.lower():
                return secs[k]
    for n in names:
        for k in secs:
            if n.lower() in k.strip().lower():
                return secs[k]
    return None


def parse_epics(lines, span, unparsed):
    if not span:
        return []
    epics, cur_epic, cur_issue, fence = [], None, None, False
    state = {'epic': None, 'issue': None}

    def flush_issue():
        if state['issue'] is not None:
            iss = state['issue']
            iss['body'] = '\n'.join(iss['_body']).strip()
            del iss['_body']
            state['epic']['issues'].append(iss)
            state['issue'] = None

    for i in range(span[0], span[1]):
        ln = lines[i]
        if ln.lstrip().startswith('```'):
            fence = not fence
            if state['issue'] is not None:
                state['issue']['_body'].append(ln)
            continue
        if fence:
            if state['issue'] is not None:
                state['issue']['_body'].append(ln)
            continue

        m = EPIC.match(ln)
        if m:
            flush_issue()
            state['epic'] = {'id': m.group(1), 'name': strip_md(m.group(2)), 'issues': []}
            epics.append(state['epic'])
            continue
        if H3.match(ln):                     # a ### that is not an Epic heading
            flush_issue()
            unparsed.append({'line': i + 1, 'text': ln.strip(),
                             'why': 'h3-in-epics-not-epic-heading'})
            state['epic'] = None
            continue

        mi = ISSUE.match(ln)
        if mi and state['epic'] is not None:
            flush_issue()
            rest = mi.group('rest')
            title = strip_md(re.split(r'(?<=[.!?])\s', rest)[0] if rest else '')
            state['issue'] = {'id': mi.group('id'), 'title': title, '_body': [rest],
                              'depends_on': [], 'resolves_upstream': [], 'line': i + 1}
            continue
        if mi and state['epic'] is None:
            unparsed.append({'line': i + 1, 'text': ln.strip()[:80],
                             'why': 'issue-line-outside-any-epic'})
            continue

        if state['issue'] is not None:
            state['issue']['_body'].append(ln)

    flush_issue()

    for e in epics:
        for iss in e['issues']:
            for bl in iss['body'].split('\n'):
                md = DEPENDS.search(bl)
                if md:
                    v = md.group('val')
                    if v.strip() in ('—', '-', 'none', 'None'):
                        continue
                    # Comma-separated list; each element may be bolded and may
                    # carry a trailing parenthetical. Stop at the first element
                    # that does not START with an id, so prose tails like
                    # plan-010:290 "6.1, 6.2, 6.3 (consolidates with Issue 4.3)"
                    # do not leak a 4.3 edge.
                    v = v.replace('**', '').replace('`', '')
                    for chunk in re.split(r'\s*,\s*| and ', v):
                        c = chunk.strip()
                        mg = re.match(r'^(G\d+)\b', c)
                        if mg:                       # a GATE reference, not an issue
                            iss.setdefault('depends_on_gates', []).append(mg.group(1))
                            continue
                        mc = re.match(r'^([0-9A-Z]+(?:\.[0-9]+[a-z]?)+)\b', c)
                        if not mc:
                            break
                        iss['depends_on'].append(mc.group(1))
                mr = RESOLVES.search(bl)
                if mr:
                    val = mr.group('val')
                    for n in UPNUM.findall(val):
                        disp = re.search(r'#' + n + r'\s*\(([^)]+)\)', val)
                        iss['resolves_upstream'].append(
                            {'issue': int(n), 'disposition': disp.group(1) if disp else None})
            iss['depends_on'] = sorted(set(iss['depends_on']))
    return epics


def parse_gates(lines, span, unparsed):
    if not span:
        return []
    gates = []
    state = {'cur': None, 'field': None}
    fence = False

    def flush():
        cur = state['cur']
        if cur:
            t = (cur.get('test') or '').strip()
            cur['test_is_executable'] = bool(
                t and not t.lower().startswith('*(none') and not t.lower().startswith('(none')
                and 'none —' not in t.lower()[:12] and '```' in t or
                bool(t and re.search(r'^(uv |bd |git |grep |python|pytest|\./|set -|yf |cargo )',
                                     t, re.M)))
            gates.append(cur)
            state['cur'] = None

    for i in range(span[0], span[1]):
        ln = lines[i]
        if ln.lstrip().startswith('```'):
            fence = not fence
            if state['cur'] is not None and state['field'] == 'test':
                state['cur']['test'] = (state['cur'].get('test') or '') + '\n' + ln
            continue
        if fence:
            if state['cur'] is not None and state['field'] == 'test':
                state['cur']['test'] = (state['cur'].get('test') or '') + '\n' + ln
            continue
        m = H3.match(ln)
        if m:
            flush()
            raw = strip_md(m.group(1))
            kind = 'other'
            if re.search(r'^start gate', raw, re.I):
                kind = 'start'
            elif re.search(r'^capability gate', raw, re.I):
                kind = 'capability'
            elif re.search(r'reconcile', raw, re.I):
                kind = 'reconcile'
            elif GATE_TITLE.search(raw):
                kind = 'named'
            name = re.sub(r'^(Start|Capability|Reconcile)?\s*Gate\s*:?\s*', '', raw,
                          flags=re.I).strip()
            state['cur'] = {'kind': kind, 'name': name or raw, 'raw_heading': raw,
                            'type': None, 'approvers': [], 'condition': None, 'test': None,
                            'test_class': None, 'cwd': None, 'blocks': [], 'instructions': None,
                            'line': i + 1}
            state['field'] = None
            if not GATE_TITLE.search(raw):
                unparsed.append({'line': i + 1, 'text': raw,
                                 'why': 'h3-in-gates-section-without-gate-word'})
            continue
        if state['cur'] is None:
            continue
        mf = FIELD.match(ln)
        if mf:
            k, v = mf.group(1).lower(), mf.group(2).strip()
            state['field'] = k
            cur = state['cur']
            if k == 'type':
                cur['type'] = v
            elif k == 'approvers':
                cur['approvers'] = [x.strip() for x in re.split(r'[,/]', v) if x.strip()]
            elif k == 'blocks':
                cur['blocks'] = [x.strip() for x in re.split(r',', strip_md(v)) if x.strip()]
            else:
                cur[k] = v
            continue
        if state['field'] in ('condition', 'instructions', 'test') and ln.strip():
            cur = state['cur']
            cur[state['field']] = ((cur.get(state['field']) or '') + ' ' + ln.strip()).strip()
    flush()
    return gates


def parse_criteria(lines, span):
    """Three spellings coexist in the corpus:
       (a) ordered list "1. ..."         (plan-041..046, plan-001..)
       (b) bullet list  "- ..."          (plan-012, -017, -026, ...)
       (c) markdown table | # | Criterion | Verification |   (plan-039, -040)
    """
    if not span:
        return []
    tbl = parse_upstream(lines, span)          # same table reader
    if tbl and any('criterion' in k for r in tbl for k in r):
        out = []
        for n, r in enumerate(tbl, 1):
            ck = next((k for k in r if 'criterion' in k), None)
            vk = next((k for k in r if 'verif' in k), None)
            txt = (r.get(ck) or '') + ' ' + (r.get(vk) or '')
            out.append({'index': n, 'ordered': False, 'form': 'table',
                        'label': r.get('#') or r.get(list(r)[0]),
                        'text': strip_md(r.get(ck) or ''),
                        'commands': [x.strip() for x in re.findall(r'`([^`]{4,})`', txt)
                                     if re.match(r'^(uv |bd |git |grep |python|pytest|\./|'
                                                 r'set -|yf |cargo |sed |awk |for )', x.strip())]})
        return out
    out, fence = [], False
    state = {'cur': None}
    # Two spellings coexist in the corpus: an ordered list ("1. ...") and a
    # bullet list ("- ..."). Bullets get a synthesized 1-based index.
    NUM = re.compile(r'^(?:(\d+)\.|-)\s+(.*)$')
    seq = [0]
    for i in range(span[0], span[1]):
        ln = lines[i]
        if ln.lstrip().startswith('```'):
            fence = not fence
            if state['cur']:
                state['cur']['_t'].append(ln)
            continue
        if fence:
            if state['cur']:
                state['cur']['_t'].append(ln)
            continue
        m = NUM.match(ln)
        if m:
            if state['cur']:
                out.append(state['cur'])
            seq[0] += 1
            state['cur'] = {'index': int(m.group(1)) if m.group(1) else seq[0],
                            'ordered': bool(m.group(1)), '_t': [m.group(2)]}
        elif state['cur'] is not None:
            state['cur']['_t'].append(ln)
    if state['cur']:
        out.append(state['cur'])
    for c in out:
        txt = '\n'.join(c['_t']).strip()
        del c['_t']
        c['text'] = strip_md(txt.split('\n')[0])
        cmds = re.findall(r'`([^`]{4,})`', txt) + re.findall(r'```(?:bash|sh)?\n(.*?)```', txt, re.S)
        c['commands'] = [x.strip() for x in cmds if re.match(
            r'^(uv |bd |git |grep |python|pytest|\./|set -|yf |cargo |sed |awk )', x.strip())]
    return out


def parse_upstream(lines, span):
    if not span:
        return []
    rows, hdr = [], None
    for i in range(span[0], span[1]):
        ln = lines[i].strip()
        if not ln.startswith('|'):
            continue
        cells = [c.strip() for c in ln.strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
            continue
        if hdr is None:
            hdr = [c.lower() for c in cells]
            continue
        rows.append(dict(zip(hdr, cells)))
    return rows


def extract(path):
    text = open(path, encoding='utf-8').read()
    lines = text.split('\n')
    unparsed = []
    secs = split_sections(lines)
    epics = parse_epics(lines, find_section(secs, 'Epics'), unparsed)
    gates = parse_gates(lines, find_section(secs, 'Gates'), unparsed)
    crit = parse_criteria(lines, find_section(secs, 'Success Criteria'))
    ups = parse_upstream(lines, find_section(secs, 'Upstream Issues'))
    m = re.search(r'^\*\*Epic:\*\*\s*(\S+)', text, re.M)
    return {
        'path': path,
        'plan_epic_bead': m.group(1) if m else None,
        'sections_found': sorted(secs),
        'epics': epics,
        'gates': gates,
        'criteria': crit,
        'upstream_rows': ups,
        'refs': {'req_ids': sorted(set(REQ.findall(text))),
                 'file_lines': sorted({f'{a}:{b}' for a, b in FILELINE.findall(text)})},
        'unparsed': unparsed,
        'counts': {'epics': len(epics),
                   'issues': sum(len(e['issues']) for e in epics),
                   'gates': len(gates),
                   'criteria': len(crit),
                   'dep_edges': sum(len(i['depends_on']) for e in epics for i in e['issues'])},
    }


if __name__ == '__main__':
    print(json.dumps(extract(sys.argv[1]), indent=1))

#!/usr/bin/env python3
"""EXP-003 pour-fidelity comparator.

Compares the issue DAG extracted from a plan.md against the bead graph the
LLM "pour" (yf-plan SKILL.md 5.2a) actually created.

Join strategy (deliberately conservative — it never invents a mapping):
  epics : bd epic bead -> plan epic, by the number in the bead title
          ("Epic 3: ..." / "Epic: 3: ..."), else by exact name match.
  issues: task bead -> plan issue, by the leading "N.M" token in the bead
          TITLE. Task beads with no such token are reported as `unnumbered`,
          never guessed at.

Usage:  pour_fidelity.py <all-beads.json> <plan-dir> [...]
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_plan import extract  # noqa: E402

TITLE_ID = re.compile(r'^\s*(?:Issue\s+)?([0-9A-Z]+(?:\.[0-9]+[a-z]?)+)\s*[:.\s]')
EPIC_NUM = re.compile(r'^Epic\s*:?\s*([0-9A-Z]+)\s*:')
SCAFFOLD = re.compile(r'^\s*(Begin|Reconcile)\s*:', re.I)


def load_beads(path):
    beads = json.load(open(path))
    by_id = {b['id']: b for b in beads}
    kids = {}
    for b in beads:
        if b.get('parent'):
            kids.setdefault(b['parent'], []).append(b['id'])
    return by_id, kids


def descendants(root, kids):
    out, stack = [], list(kids.get(root, []))
    while stack:
        i = stack.pop()
        out.append(i)
        stack += kids.get(i, [])
    return out


def norm(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def compare(plan_md, epic_id, by_id, kids):
    ext = extract(plan_md)
    plan_epics = {e['id']: e for e in ext['epics']}
    plan_issues = {i['id']: i for e in ext['epics'] for i in e['issues']}
    plan_edges = {(i['id'], d) for i in plan_issues.values() for d in i['depends_on']
                  if d in plan_issues}
    plan_dangling = {(i['id'], d) for i in plan_issues.values() for d in i['depends_on']
                     if d not in plan_issues}

    res = {'plan': os.path.basename(os.path.dirname(plan_md)), 'epic_bead': epic_id,
           'extractor': ext['counts'], 'unparsed': ext['unparsed']}
    if epic_id not in by_id:
        res['error'] = 'epic bead not found in bd dump'
        return res

    desc = descendants(epic_id, kids)
    tasks = [by_id[i] for i in desc if by_id[i]['issue_type'] == 'task']
    gates = [by_id[i] for i in desc if by_id[i]['issue_type'] == 'gate']
    bepics = [by_id[i] for i in desc if by_id[i]['issue_type'] == 'epic']

    # --- epic mapping ---
    epic_map, epic_unmapped = {}, []
    for b in bepics:
        m = EPIC_NUM.match(b['title'].strip())
        if m and m.group(1) in plan_epics:
            epic_map[b['id']] = m.group(1)
            continue
        nm = re.sub(r'^Epic\b\s*(?::\s*)?(?:[0-9A-Z]{1,2}\s*:\s*)?', '', b['title'].strip())
        hit = [pe for pe in plan_epics.values() if norm(pe['name'])[:25] == norm(nm)[:25]]
        if len(hit) == 1:
            epic_map[b['id']] = hit[0]['id']
        else:
            epic_unmapped.append({'id': b['id'], 'title': b['title'][:60]})
    res['epics_cmp'] = {'plan': len(plan_epics), 'bd': len(bepics),
                        'mapped': len(epic_map), 'unmapped': epic_unmapped,
                        'match': len(plan_epics) == len(bepics)}

    # --- issue join ---
    bead_by_iid, unnumbered, scaffold, misfiled = {}, [], [], []
    for t in tasks:
        if SCAFFOLD.match(t['title']):
            scaffold.append({'id': t['id'], 'title': t['title'][:60]})
            continue
        m = TITLE_ID.match(t['title'])
        if not m:
            unnumbered.append({'id': t['id'], 'title': t['title'][:60],
                               'parent': t.get('parent')})
            continue
        key = m.group(1)
        bead_by_iid.setdefault(key, []).append(t['id'])
        pe = epic_map.get(t.get('parent'))
        if pe is not None and not key.startswith(pe + '.'):
            misfiled.append({'id': t['id'], 'title_key': key,
                             'parent_epic_maps_to': pe})

    res['bd'] = {'epics': len(bepics), 'tasks': len(tasks),
                 'joined_tasks': sum(len(v) for v in bead_by_iid.values()),
                 'unnumbered_tasks': len(unnumbered),
                 'scaffold_tasks': len(scaffold), 'gates': len(gates)}
    res['bd_unnumbered'] = unnumbered
    res['bd_misfiled'] = misfiled
    res['joinable'] = len(unnumbered) == 0 or len(bead_by_iid) > 0

    missing = sorted(set(plan_issues) - set(bead_by_iid))
    extra = sorted(set(bead_by_iid) - set(plan_issues))
    dup = sorted(k for k, v in bead_by_iid.items() if len(v) > 1)
    res['issues'] = {'plan_count': len(plan_issues), 'bead_count': len(bead_by_iid),
                     'missing_beads': missing, 'extra_beads': extra, 'duplicate_ids': dup}

    # --- per-epic counts (works even when titles carry no issue ids) ---
    per_epic = []
    for b in bepics:
        pe = epic_map.get(b['id'])
        n_b = len([1 for i in kids.get(b['id'], [])
                   if by_id[i]['issue_type'] == 'task' and not SCAFFOLD.match(by_id[i]['title'])])
        n_p = len(plan_epics[pe]['issues']) if pe in plan_epics else None
        per_epic.append({'bead': b['id'], 'plan_epic': pe, 'bd_tasks': n_b,
                         'plan_issues': n_p, 'match': n_p == n_b})
    res['per_epic'] = per_epic
    res['per_epic_all_match'] = all(p['match'] for p in per_epic) and not epic_unmapped

    # --- dependency edges ---
    iid_of = {b: k for k, v in bead_by_iid.items() for b in v}
    bd_edges, bd_edges_nonissue = set(), []
    for t in tasks:
        for dep in t.get('dependencies') or []:
            if dep.get('type') != 'blocks':
                continue
            a, b = iid_of.get(t['id']), iid_of.get(dep['depends_on_id'])
            if a and b:
                bd_edges.add((a, b))
            else:
                bd_edges_nonissue.append([t['id'], dep['depends_on_id']])
    res['edges'] = {'plan_count': len(plan_edges), 'bd_count': len(bd_edges),
                    'in_plan_not_bd': sorted(plan_edges - bd_edges),
                    'in_bd_not_plan': sorted(bd_edges - plan_edges),
                    'plan_dangling_targets': sorted(plan_dangling),
                    'bd_blocks_edges_touching_unjoined': sorted(bd_edges_nonissue)}

    res['gates'] = {'plan_count': len(ext['gates']), 'bd_count': len(gates),
                    'plan_names': [g['raw_heading'] for g in ext['gates']],
                    'bd_titles': [g['title'] for g in gates],
                    'match': len(ext['gates']) == len(gates)}

    res['verdict'] = {'issue_count_match': len(plan_issues) == len(bead_by_iid),
                      'issue_id_set_match': not missing and not extra and not dup,
                      'per_epic_count_match': res['per_epic_all_match'],
                      'edge_set_match': plan_edges == bd_edges,
                      'gate_count_match': len(ext['gates']) == len(gates),
                      'epic_count_match': len(plan_epics) == len(bepics)}
    res['clean'] = all(res['verdict'].values()) and not unnumbered and not misfiled
    return res


def main():
    by_id, kids = load_beads(sys.argv[1])
    out = []
    for d in sys.argv[2:]:
        pm = os.path.join(d, 'plan.md')
        if not os.path.exists(pm):
            out.append({'plan': os.path.basename(d.rstrip('/')), 'error': 'no plan.md'})
            continue
        txt = open(pm, encoding='utf-8').read()
        m = re.search(r'^\*\*Epic:\*\*\s*(\S+)', txt, re.M)
        if not m:
            out.append({'plan': os.path.basename(d.rstrip('/')), 'skipped': 'no **Epic:** field'})
            continue
        out.append(compare(pm, m.group(1), by_id, kids))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()

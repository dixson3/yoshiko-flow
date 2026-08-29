import importlib.util, sys, time, json
spec = importlib.util.spec_from_file_location("upmod", "/Users/james/.claude/skills/yf-beads-upstream/scripts/upstream.py")
up = importlib.util.module_from_spec(spec)
sys.modules["upmod"] = up
spec.loader.exec_module(up)

t0=time.time(); rows = up.load_universe_rows(); t1=time.time()
print(f"EXP001 universe rows={len(rows)} load_universe_rows={t1-t0:.2f}s", flush=True)
beads = {r["id"]: r for r in rows if r.get("id")}
print(f"EXP001 beads with id={len(beads)}", flush=True)

ids=sorted(beads)[:20]
t2=time.time()
for b in ids: up.deps_for_show(b)
t3=time.time()
print(f"EXP001 20 bd show calls={t3-t2:.2f}s per-call={(t3-t2)/20:.3f}s projected_full={(t3-t2)/20*len(beads):.1f}s", flush=True)

t4=time.time(); edges = up.collect_parent_edges(beads); t5=time.time()
print(f"EXP001 collect_parent_edges COMPLETED in {t5-t4:.1f}s edges={len(edges)}", flush=True)

# One-call candidate: read edges straight off the universe rows.
t6=time.time()
fast=[]
for r in rows:
    bid=r.get("id")
    if not bid: continue
    for dep in (r.get("dependencies") or []):
        if up.edge_type(dep)!="parent-child": continue
        tgt=dep.get("depends_on_id") or dep.get("id") or dep.get("target")
        if not tgt: continue
        fast.append(up.Edge(blocked=bid, blocker=tgt, dep_type=up.PARENT_CHILD, target=beads.get(tgt)))
t7=time.time()
print(f"EXP002 one-call edge derivation={t7-t6:.4f}s edges={len(fast)}", flush=True)

def key(e): return (e.blocked, e.blocker, e.dep_type)
s_slow={key(e) for e in edges}; s_fast={key(e) for e in fast}
print(f"EXP002 EQUIVALENT={s_slow==s_fast} slow_only={len(s_slow-s_fast)} fast_only={len(s_fast-s_slow)}", flush=True)
if s_slow-s_fast: print("  slow_only sample:", list(s_slow-s_fast)[:5])
if s_fast-s_slow: print("  fast_only sample:", list(s_fast-s_slow)[:5])

# targets resolve identically?
tslow={key(e): (e.target or {}).get("id") for e in edges}
tfast={key(e): (e.target or {}).get("id") for e in fast}
print(f"EXP002 targets identical={tslow==tfast}", flush=True)

t8=time.time(); lines = up.owner_claim_warning_lines(); t9=time.time()
print(f"EXP001 owner_claim_warning_lines COMPLETED in {t9-t8:.1f}s", flush=True)
print(json.dumps(lines, indent=1))

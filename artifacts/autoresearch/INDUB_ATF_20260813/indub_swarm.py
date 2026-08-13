import json, re, urllib.request, hashlib, time, random
BASE = "/Users/jean-marietassy/Documents/GitHub/helen_os_v1/artifacts/autoresearch/INDUB_ATF_20260813"
DS = json.load(open(f"{BASE}/dataset.json"))
train = [r for r in DS['records'] if not r['heldout']]
held  = [r for r in DS['records'] if r['heldout']]
M12 = "gemma4-12b:latest"
M26 = "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"

def check(rule, data):
    t, p = rule.get('type'), rule.get('params', {})
    try:
        if t == 'PHASE_PAIR_EQUAL_PRICE':
            pairs = {}
            for r in data:
                if r['phase']: pairs.setdefault((r['family'], r['no'], r['point'], r['length']), {})[r['phase']] = r['price_cents']
            both = [v for v in pairs.values() if 'OPEN' in v and 'TINT' in v]
            if not both: return None, 0
            return sum(1 for v in both if v['OPEN'] == v['TINT']) / len(both), len(both)
        if t == 'SIZE_LADDER':
            pts = [r['point'] for r in data if r['point']]
            if not pts: return None, 0
            ok = set(p.get('sizes', []))
            return sum(1 for x in pts if x in ok) / len(pts), len(pts)
        if t == 'PRICE_MONOTONE_SIZE':
            groups, ok, n = {}, 0, 0
            for r in data:
                if r['point']: groups.setdefault((r['family'], r['length'], r['phase']), []).append((r['point'], r['price_cents']))
            for g in groups.values():
                if len(g) < 2: continue
                g.sort(); n += 1
                if all(g[i+1][1] >= g[i][1] for i in range(len(g)-1)): ok += 1
            return (ok / n if n else None), n
        if t == 'PRICE_PER_UNIT_RANGE':
            u = p.get('unit', 'INCHES'); lo, hi = float(p.get('min', 0)), float(p.get('max', 1e9))
            xs = [r['price_cents'] / r['length'] for r in data if r['unit'] == u and r['length']]
            if not xs: return None, 0
            return sum(1 for x in xs if lo <= x <= hi) / len(xs), len(xs)
        if t == 'LENGTH_QUANTA':
            ok = set(p.get('lengths', []))
            xs = [r['length'] for r in data]
            return sum(1 for x in xs if x in ok) / len(xs), len(xs)
        if t == 'FAMILY_POINTS':
            fam = (p.get('family') or '').upper(); ok = set(p.get('points', []))
            xs = [r['point'] for r in data if r['family'] and fam in r['family'] and r['point']]
            if not xs: return None, 0
            return sum(1 for x in xs if x in ok) / len(xs), len(xs)
    except Exception:
        return None, 0
    return None, 0

def sample_evidence(seed, n=45):
    rng = random.Random(seed)
    rows = rng.sample(train, min(n, len(train)))
    return "\n".join(f"{r['family']}|no={r['no']}|pt={r['point']}|{r['phase'] or '-'}|{r['length']}{r['unit'][:2]}|{r['price_cents']}c" for r in rows)

def ollama(model, prompt, seed):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
        "options": {"num_predict": 500, "temperature": 0.85, "seed": seed}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1500) as r:
        return json.load(r)["response"]

TEMPLATES = """Rule types you may emit (JSON only, no prose):
PHASE_PAIR_EQUAL_PRICE {} | SIZE_LADDER {"sizes":[...]} | PRICE_MONOTONE_SIZE {} |
PRICE_PER_UNIT_RANGE {"unit":"INCHES","min":cents_per_unit,"max":...} |
LENGTH_QUANTA {"lengths":[...]} | FAMILY_POINTS {"family":"NAME","points":[...]} |
FREEFORM {"statement":"..."} (uncheckable, use sparingly)"""

rulebook, manifests, log = {}, [], []
for epoch in range(1, 21):
    model = M12 if epoch % 2 == 1 else M26
    worker = f"W{epoch:02d}-{'12b' if model==M12 else '26b'}"
    seed = 4200 + epoch
    top = sorted(rulebook.values(), key=lambda x: -(x['score'] or 0))[:6]
    fb = "\n".join(f"{r['rule']['type']} {json.dumps(r['rule'].get('params',{}))} -> heldout_support={r['score']:.2f} n={r['n']}" for r in top if r['score'] is not None) or "none yet"
    prompt = (f"You are worker {worker} in a grammar-induction swarm over an 1900 type-foundry catalogue dataset. "
        f"Goal: recover compact generative PRICING/STRUCTURE rules that predict held-out specimens. "
        f"TRAIN SAMPLE (family|no|point|phase|length|price_cents):\n{sample_evidence(seed)}\n\n"
        f"CURRENT RULEBOOK (train-scored):\n{fb}\n\n{TEMPLATES}\n\n"
        f'Return ONLY JSON: {{"rules":[{{"type":"...","params":{{...}},"statement":"..."}}]}} — max 4 rules, prefer refining weak ones or proposing untried types.')
    t0 = time.time()
    try:
        out = ollama(model, prompt, seed)
        err = None
    except Exception as e:
        out, err = "", str(e)
    dt = round(time.time() - t0, 1)
    manifests.append(dict(worker=worker, model=model, epoch=epoch, seed=seed,
        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()[:16],
        output_sha256=hashlib.sha256(out.encode()).hexdigest()[:16], secs=dt, error=err))
    m = re.search(r'\{.*\}', out, re.S)
    added = 0
    if m:
        try:
            for rule in json.loads(m.group(0)).get('rules', [])[:4]:
                key = rule.get('type', '') + json.dumps(rule.get('params', {}), sort_keys=True)
                sc, n = check(rule, train)   # train-scored during epochs; heldout only at the end
                rulebook[key] = dict(rule=rule, score=sc, n=n, by=worker)
                added += 1
        except Exception as e:
            err = f"parse: {e}"
    log.append(f"epoch {epoch:02d} {worker} {dt}s rules+{added} book={len(rulebook)} err={err}")
    print(log[-1], flush=True)

# FINAL: heldout evaluation (never shown to workers)
final = []
for key, entry in rulebook.items():
    sc, n = check(entry['rule'], held)
    verdict = 'UNCHECKABLE' if sc is None else ('SUPPORTED' if (sc >= 0.95 and n >= 4) else ('REFUTED' if sc < 0.80 else 'HOLD'))
    final.append(dict(rule=entry['rule'], by=entry['by'], train_support=entry['score'], heldout_support=sc, heldout_n=n, verdict=verdict))
json.dump(dict(manifests=manifests, log=log, n_rules=len(final), results=sorted(final, key=lambda x: -(x['heldout_support'] or 0))),
          open(f"{BASE}/indub_results.json", 'w'), indent=1)
print("=== FINAL HELDOUT VERDICTS ===")
for f in sorted(final, key=lambda x: -(x['heldout_support'] or 0)):
    print(f"{f['verdict']:11s} {f['rule']['type']:24s} {json.dumps(f['rule'].get('params',{}))[:60]:60s} held={f['heldout_support'] if f['heldout_support'] is None else round(f['heldout_support'],2)} n={f['heldout_n']} by={f['by']}")

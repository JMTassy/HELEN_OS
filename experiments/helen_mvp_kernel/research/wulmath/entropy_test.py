# -*- coding: utf-8 -*-
"""GOBLIN-1 IDEA #4, executed on the real 108-line corpus.

H(colour | mono_text): if a predictor recovers the vibration from the
text alone, the colour axis carries no bits and is decoration.
Leave-one-out cross-validation, multinomial naive Bayes, Laplace
smoothing. Nothing is fitted on the sample it scores.
"""
import re, math
from collections import Counter, defaultdict
from wul_data import LAWS, VIB

def toks(name, math_line):
    s = (name + " " + math_line).lower()
    s = re.sub(r"[_·|]", " ", s)
    return [t for t in re.findall(r"[a-zA-Z⊬⊢⊊⊋∧∨¬⊥≠≤≥→↦⇒⟺∈∉∀∃∅σψρΔΣκτεαπ]+", s)
            if len(t) > 1 or t in "⊬⊢⊊⊋∧∨¬⊥"]

DATA = [(toks(n, m), v) for _, n, m, v in LAWS]
CLASSES = sorted(VIB)

def train(rows):
    prior = Counter(v for _, v in rows)
    cnt = {c: Counter() for c in CLASSES}
    tot = {c: 0 for c in CLASSES}
    vocab = set()
    for f, v in rows:
        cnt[v].update(f); tot[v] += len(f); vocab |= set(f)
    return prior, cnt, tot, len(rows), max(len(vocab), 1)

def predict(model, feats):
    prior, cnt, tot, n, V = model
    best, bs = None, -1e18
    for c in CLASSES:
        if prior[c] == 0:
            continue
        s = math.log(prior[c] / n)
        for t in feats:
            s += math.log((cnt[c][t] + 1) / (tot[c] + V))
        if s > bs:
            bs, best = s, c
    return best

# ── leave-one-out ────────────────────────────────────────────────────
correct = 0
confusion = defaultdict(Counter)
misses = []
for i in range(len(DATA)):
    hold = DATA[i]
    model = train(DATA[:i] + DATA[i+1:])
    p = predict(model, hold[0])
    confusion[hold[1]][p] += 1
    if p == hold[1]:
        correct += 1
    else:
        misses.append((LAWS[i][0], LAWS[i][1], hold[1], p))

n = len(DATA)
acc = correct / n
majority = max(Counter(v for _, v in DATA).values()) / n
chance = 1 / len(CLASSES)

# empirical conditional entropy bound via Fano-style read of the errors
H_prior = -sum((c/n) * math.log2(c/n)
               for c in Counter(v for _, v in DATA).values())

print(f"n                       = {n}")
print(f"classes                 = {len(CLASSES)}")
print(f"chance baseline         = {chance:.4f}")
print(f"majority baseline       = {majority:.4f}")
print(f"H(colour)  prior        = {H_prior:.4f} bits")
print(f"LOO accuracy            = {acc:.4f}  ({correct}/{n})")
print(f"error rate              = {1-acc:.4f}  ({n-correct}/{n})")
print()
print("confusion (true -> predicted):")
for t in CLASSES:
    row = " ".join(f"{confusion[t][p]:>3}" for p in CLASSES)
    print(f"  v{t} {VIB[t][0]:<13} {row}   (n={sum(confusion[t].values())})")
print()
print("misclassified:")
for i, nm, t, p in misses:
    print(f"  {i:03d} {nm[:52]:<52} {t}->{p}")

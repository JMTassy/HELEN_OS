#!/usr/bin/env python3
"""
VISIBLE_GOBLIN_LIVE_STREAM_V0 — the live producer half.

Two REAL local Goblins run asynchronously and emit explicit, structured research
events THE INSTANT each is produced (never buffered to epoch end). Claude is
control plane only (launch/monitor/stop) — it does NOT paraphrase Goblin output;
the raw typed events land in an append-only NDJSON the operator tails directly.

  HER_GEMMA   = construct / branch / mutate     (gemma-4-26B)
  PREHAL_QWEN = attack / counterfeit / discriminate (Qwen-3.8 abliterated)

NO hidden chain-of-thought is exposed — only explicit research artifacts.
Every Garden transition is witnessed by exactly one event (∀δ ∃!e). Object ids
are assigned by the PRODUCER (stable identity), never by any renderer. Three
timestamps are distinct: emitted_at (model), observed_at (bus), trace_seq (bus).
authority=false · canon=false · ledger_effect=none · ΔA=0 · NO_CLAIM.
"""
import json, os, re, sys, threading, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
TRACE = ROOT / "traces" / "live_events.ndjson"
OLLAMA = "http://localhost:11434/api/chat"
HER = "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"
QWEN = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"
EPOCHS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
QUESTION = sys.argv[2] if len(sys.argv) > 2 else \
    "Search for a strange-but-formal mathematical object. authority=0, evidence=0."

now = lambda: datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Bus:
    """Append-only typed event bus. Assigns trace_seq + observed_at under lock."""
    def __init__(self, path):
        self.path = path; self.lock = threading.Lock(); self.seq = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists(): path.rename(path.with_suffix(".ndjson.bak"))  # fresh trace per run
        self.f = open(path, "a", buffering=1)

    def emit(self, ev):
        with self.lock:
            ev["trace_seq"] = self.seq; self.seq += 1
            ev["observed_at"] = now()
            self.f.write(json.dumps(ev, ensure_ascii=False) + "\n")
            self.f.flush(); os.fsync(self.f.fileno())
            # control-plane breadcrumb ONLY (id/op), never the goblin's content text
            print(f"  · emit trace_seq={ev['trace_seq']:03d} {ev['actor']:11s} {ev['op']:18s} {ev['object_id']}", flush=True)
        return ev


class Registry:
    def __init__(self): self.lock = threading.Lock(); self.n = 0; self.objs = []
    def new_id(self, prefix="O"):
        with self.lock: self.n += 1; return f"{prefix}_{self.n:03d}"
    def add(self, o):
        with self.lock: self.objs.append(o)
    def latest_unattacked(self):
        with self.lock:
            for o in reversed(self.objs):
                if not o.get("attacked"): return o
        return None
    def any(self):
        with self.lock: return self.objs[-1] if self.objs else None


def ollama(model, sysp, user, temp=0.9, npred=240, timeout=300):
    body = json.dumps({"model": model, "stream": False, "think": False,
        "keep_alive": "10m",
        "messages": [{"role": "system", "content": sysp}, {"role": "user", "content": user}],
        "options": {"temperature": temp, "num_predict": npred, "top_p": 0.95}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    t0 = now()
    with urllib.request.urlopen(req, timeout=timeout) as r: d = json.loads(r.read())
    m = d.get("message", {}) or {}
    return (m.get("content") or m.get("thinking") or "").strip(), t0


def field(t, k):
    m = re.search(rf"^{k}:\s*(.+?)\s*$", t, re.I | re.M); return m.group(1).strip() if m else ""


HER_SYS = ("You are HER/GEMMA, constructive heterodoxy in a NO-CLAIM math Garden. "
           "Emit ONE explicit research artifact in the exact template. No prose, no essay.")
QWEN_SYS = ("You are PRE-HAL/QWEN, adversarial heterodoxy in a NO-CLAIM math Garden. "
            "Attack the frame. Emit ONE explicit research artifact in the exact template. No prose.")


def ev(actor, op, oid, parents, **kw):
    base = {"event_id": uuid.uuid4().hex[:12], "epoch": kw.pop("epoch", 0), "actor": actor,
            "op": op, "object_id": oid, "parent_ids": parents,
            "distinction": "", "mechanism": "", "counterfeit": "", "discriminator": "",
            "next_move": "", "emitted_at": kw.pop("emitted_at", now())}
    base.update(kw); return base


def her_worker(bus, reg, done):
    for e in range(1, EPOCHS + 1):
        # PROPOSE
        try:
            raw, t0 = ollama(HER, HER_SYS, f"{QUESTION}\nEpoch {e}. Emit ONE NEW object:\n"
                             "OBJECT: <short name>\nDISTINCTION: <one structural distinction>\n"
                             "MECHANISM: <one line>\nNEXT: <one mutation>\nEND")
        except Exception as ex: raw, t0 = f"__ERR__ {ex}", now()
        oid = reg.new_id("O")
        o = {"id": oid, "name": field(raw, "OBJECT") or f"object {oid}",
             "distinction": field(raw, "DISTINCTION"), "epoch": e}
        reg.add(o)
        bus.emit(ev("HER_GEMMA", "PROPOSE", oid, [], epoch=e, emitted_at=t0,
                    distinction=o["distinction"], mechanism=field(raw, "MECHANISM"),
                    next_move=field(raw, "NEXT")))
        # MUTATE the object into a child
        try:
            raw, t0 = ollama(HER, HER_SYS, f"Parent object «{o['name']}» — {o['distinction']}\n"
                             "Mutate into a STRUCTURALLY distinct child:\nOBJECT: <name>\n"
                             "DISTINCTION: <delta vs parent>\nMECHANISM: <one line>\nNEXT: <one>\nEND")
        except Exception as ex: raw, t0 = f"__ERR__ {ex}", now()
        cid = reg.new_id("O")
        c = {"id": cid, "name": field(raw, "OBJECT") or f"child {cid}",
             "distinction": field(raw, "DISTINCTION"), "epoch": e}
        reg.add(c)
        bus.emit(ev("HER_GEMMA", "MUTATE", cid, [oid], epoch=e, emitted_at=t0,
                    distinction=c["distinction"], mechanism=field(raw, "MECHANISM"),
                    next_move=field(raw, "NEXT")))
    done.set()


def qwen_worker(bus, reg, her_done):
    handled = set()
    while not (her_done.is_set() and _all_handled(reg, handled)):
        o = _next_target(reg, handled)
        if not o:
            time.sleep(0.4); continue
        handled.add(o["id"]); e = o["epoch"]
        # COUNTERFEIT
        try:
            raw, t0 = ollama(QWEN, QWEN_SYS, f"Target object «{o['name']}» — {o['distinction']}\n"
                             "Construct its nearest boring counterfeit:\nCOUNTERFEIT: <ordinary look-alike>\n"
                             "WHY: <one line>\nEND", npred=260)
        except Exception as ex: raw, t0 = f"__ERR__ {ex}", now()
        cf = field(raw, "COUNTERFEIT")
        bus.emit(ev("PREHAL_QWEN", "COUNTERFEIT", o["id"], [o["id"]], epoch=e, emitted_at=t0,
                    counterfeit=cf, mechanism=field(raw, "WHY")))
        # DISCRIMINATE
        try:
            raw, t0 = ollama(QWEN, QWEN_SYS, f"Object «{o['name']}» vs counterfeit «{cf[:60]}».\n"
                             "Cheapest test that separates them:\nDISCRIMINATOR: <x*>\nEND", npred=220)
        except Exception as ex: raw, t0 = f"__ERR__ {ex}", now()
        disc = field(raw, "DISCRIMINATOR")
        did = reg.new_id("D")
        bus.emit(ev("PREHAL_QWEN", "DISCRIMINATE", did, [o["id"]], epoch=e, emitted_at=t0,
                    discriminator=disc))
        # verdict transition (Garden state change → must be witnessed)
        verdict_op = "HOLD" if (disc and o["distinction"]) else "COMPOST"
        bus.emit(ev("PREHAL_QWEN", verdict_op, o["id"], [o["id"]], epoch=e,
                    discriminator=disc, mechanism="disc∧distinction⇒HOLD else COMPOST"))


def _next_target(reg, handled):
    with reg.lock:
        for o in reg.objs:
            if o["id"] not in handled: return o
    return None
def _all_handled(reg, handled):
    with reg.lock: return all(o["id"] in handled for o in reg.objs)


def main():
    print("═" * 70)
    print(f"  VISIBLE_GOBLIN_LIVE_STREAM_V0 · producer · {EPOCHS} epochs · 2 async goblins")
    print(f"  HER={HER.split('/')[-1]}  QWEN={QWEN.split('/')[-1]}")
    print(f"  trace → {TRACE}   (tail it with: python3 live_goblins.py)")
    print("═" * 70, flush=True)
    bus = Bus(TRACE); reg = Registry(); her_done = threading.Event()
    th = threading.Thread(target=her_worker, args=(bus, reg, her_done))
    tq = threading.Thread(target=qwen_worker, args=(bus, reg, her_done))
    t0 = time.time(); th.start(); tq.start(); th.join(); tq.join()
    bus.emit(ev("CONTROL", "RUN_END", "-", [], epoch=EPOCHS,
                next_move=f"epochs={EPOCHS} wall_s={round(time.time()-t0,1)}"))
    print("═" * 70)
    print(f"  RUN_END · {bus.seq} events · {round(time.time()-t0,1)}s · trace at {TRACE.name}")
    print("═" * 70)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""tools/run_hal_epoch.py — HAL epoch runner. Non-sovereign. No ledger writes.

Runs a single HAL evaluation epoch: sends a task/hypothesis to the HAL model,
parses the verdict (PASS / FAIL / BLOCK), and prints a structured result.
No receipt is emitted; no ledger entry is written. authority=false.

Usage:
    python3 tools/run_hal_epoch.py --epoch E01 --task "hypothesis text"
    echo "task" | python3 tools/run_hal_epoch.py --epoch E01
    python3 tools/run_hal_epoch.py --epoch E01 --task "..." --json

Env:
    HAL_MODEL   = deepseek-r1:14b
    OLLAMA_URL  = http://localhost:11434/api/chat
"""
import sys, os, json, time, argparse, hashlib

# locate hal_driver alongside this file
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hal_driver import HalDriver

HAL_SYSTEM = (
    "You are HAL — the strict, non-sovereign gate agent of HELEN OS. "
    "You evaluate hypotheses with precision and no sentiment. "
    "You never write to the ledger. You never approve your own work. "
    "Respond with exactly two lines:\n"
    "VERDICT: <PASS|FAIL|BLOCK>\n"
    "REASON: <one paragraph, max 120 words>\n"
    "No other text."
)


def parse_verdict(text: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s.upper().startswith('VERDICT:'):
            v = s.split(':', 1)[1].strip().upper()
            if v in ('PASS', 'FAIL', 'BLOCK'):
                return v
    return 'UNKNOWN'


def run_epoch(epoch_id: str, task: str) -> dict:
    hal = HalDriver()
    ts  = int(time.time())

    if not hal.health():
        return {
            'epoch':     epoch_id,
            'status':    'ABORT',
            'reason':    'Ollama unreachable — check HAL_MODEL / OLLAMA_URL',
            'model':     hal.model,
            'url':       hal.url,
            'authority': False,
            'sovereign': False,
            'ts':        ts,
        }

    t0     = time.time()
    output = hal.think(task, system=HAL_SYSTEM)
    elapsed = round(time.time() - t0, 2)
    verdict = parse_verdict(output)

    # deterministic hash of canonical payload — not a ledger hash, just provenance
    canon = json.dumps({'epoch': epoch_id, 'task': task, 'output': output}, sort_keys=True)
    payload_hash = hashlib.sha256(canon.encode()).hexdigest()

    return {
        'epoch':        epoch_id,
        'status':       verdict,
        'task':         task,
        'output':       output,
        'model':        hal.model,
        'url':          hal.url,
        'elapsed_s':    elapsed,
        'payload_hash': payload_hash,
        'authority':    False,
        'sovereign':    False,
        'ts':           ts,
    }


def print_human(r: dict) -> None:
    print(f"EPOCH      : {r['epoch']}")
    print(f"MODEL      : {r['model']}")
    print(f"URL        : {r['url']}")
    print(f"STATUS     : {r['status']}")
    print(f"ELAPSED    : {r.get('elapsed_s', '?')}s")
    print(f"HASH       : {r.get('payload_hash', '')[:20]}…")
    print('─' * 64)
    print(r.get('output', r.get('reason', '')))
    print('─' * 64)
    print('authority=false  sovereign=false  NO_RECEIPT=NO_CLAIM')


def main() -> None:
    ap = argparse.ArgumentParser(description='HAL epoch runner — non-sovereign')
    ap.add_argument('--epoch', default='E00',   help='Epoch ID, e.g. E01')
    ap.add_argument('--task',  default=None,    help='Task / hypothesis string')
    ap.add_argument('--json',  action='store_true', help='Output JSON only (machine-readable)')
    args = ap.parse_args()

    task = args.task
    if not task and not sys.stdin.isatty():
        task = sys.stdin.read().strip()
    if not task:
        ap.error('Provide --task "..." or pipe task via stdin')

    result = run_epoch(args.epoch, task)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == '__main__':
    main()

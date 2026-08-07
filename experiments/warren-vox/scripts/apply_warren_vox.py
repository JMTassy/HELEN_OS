#!/usr/bin/env python3
"""Apply WARREN VOX — alter no mechanics, spend no credits.

One-liner:
  python3 experiments/warren-vox/scripts/apply_warren_vox.py --target surface.html

authority: false · claim: NO_CLAIM · paid_generation_calls: 0
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

VOX_ROOT = Path(__file__).resolve().parents[1]
TOKENS = VOX_ROOT / "tokens.css"
MARKER_BEGIN = "/* ===== WARREN-VOX-BEGIN"
MARKER_END = "/* ===== WARREN-VOX-END ===== */"
LINK_TAG = 'data-warren-vox="1"'

# Files we refuse to skin-mutate (mechanics / tests)
REFUSE_NAME_RE = re.compile(
    r"(^|/)(_?test_|test_|.*_test\.|.*_selftest\.|.*_gates\.|.*_sim\.js$|"
    r"selftest\.js$|verify\.js$|logic\.js$)",
    re.I,
)
REDUCER_RE = re.compile(
    r"/\*\s*=====\s*REDUCER-BEGIN.*?/\*\s*=====\s*REDUCER-END",
    re.S | re.I,
)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def extract_scripts(html: str) -> list[str]:
    return re.findall(r"<script\b[^>]*>(.*?)</script>", html, flags=re.S | re.I)


def scripts_fingerprint(html: str) -> str:
    parts = extract_scripts(html)
    blob = "\n".join(parts).encode("utf-8")
    return sha256_bytes(blob)


def refuse_target(path: Path) -> str | None:
    s = str(path).replace("\\", "/")
    if REFUSE_NAME_RE.search(s):
        return f"refused: mechanics/test filename pattern: {path.name}"
    if path.suffix.lower() not in {".html", ".htm"}:
        return f"refused: target must be .html (got {path.suffix!r})"
    return None


def strip_existing_vox(html: str) -> str:
    # Remove previous inline VOX block
    html = re.sub(
        r"\s*" + re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END) + r"\s*",
        "\n",
        html,
        flags=re.S,
    )
    # Remove previous link tags we injected
    html = re.sub(
        r'\s*<link[^>]+data-warren-vox="1"[^>]*>\s*',
        "\n",
        html,
        flags=re.I,
    )
    return html


def inject_link(html: str, rel_css: str) -> str:
    tag = f'<link rel="stylesheet" href="{rel_css}" {LINK_TAG} />\n'
    if re.search(r"</head>", html, re.I):
        return re.sub(r"</head>", tag + "</head>", html, count=1, flags=re.I)
    # no head — prepend
    return tag + html


def inject_inline(html: str, css: str) -> str:
    block = f"<style>\n{MARKER_BEGIN} (auto-injected, do not put mechanics here) ===== */\n{css}\n{MARKER_END}\n</style>\n"
    if re.search(r"</head>", html, re.I):
        return re.sub(r"</head>", block + "</head>", html, count=1, flags=re.I)
    return block + html


def ensure_body_class(html: str, family: str) -> str:
    """Add data-vox family on <body> if missing — visual only."""
    m = re.search(r"<body([^>]*)>", html, re.I)
    if not m:
        return html
    attrs = m.group(1)
    if re.search(r"data-vox\s*=", attrs, re.I):
        # replace family value only
        new_attrs = re.sub(
            r'data-vox\s*=\s*["\'][^"\']*["\']',
            f'data-vox="{family}"',
            attrs,
            count=1,
            flags=re.I,
        )
    else:
        new_attrs = attrs + f' data-vox="{family}"'
    # also ensure vox-page class for layout if body has class attr
    if re.search(r"class\s*=", new_attrs, re.I):
        if "vox-page" not in new_attrs:
            new_attrs = re.sub(
                r'class\s*=\s*"([^"]*)"',
                r'class="\1 vox-page"',
                new_attrs,
                count=1,
                flags=re.I,
            )
            new_attrs = re.sub(
                r"class\s*=\s*'([^']*)'",
                r"class='\1 vox-page'",
                new_attrs,
                count=1,
                flags=re.I,
            )
    else:
        new_attrs = new_attrs + ' class="vox-page"'
    return html[: m.start()] + f"<body{new_attrs}>" + html[m.end() :]


def ensure_law_footer(html: str) -> str:
    if "Garden ADMIT" in html and "VOX skin" in html:
        return html
    footer = (
        '\n<p class="vox-law-static">'
        "Garden ADMIT ≠ Kernel ADMISSION · authority=false · VOX skin only"
        "</p>\n"
    )
    if re.search(r"</body>", html, re.I):
        return re.sub(r"</body>", footer + "</body>", html, count=1, flags=re.I)
    return html + footer


def apply_vox(
    target: Path,
    out: Path | None,
    family: str,
    mode: str,
    force: bool,
) -> dict:
    reason = refuse_target(target)
    if reason and not force:
        return {"ok": False, "error": reason}

    if not TOKENS.is_file():
        return {"ok": False, "error": f"tokens.css missing: {TOKENS}"}

    raw = target.read_text(encoding="utf-8")
    before_fp = scripts_fingerprint(raw)

    # Refuse if someone asks us to rewrite a file that IS only a reducer extract — N/A for html
    # Soft warn if REDUCER markers present: we still only inject CSS, never rewrite that region.
    has_reducer = bool(REDUCER_RE.search(raw))

    html = strip_existing_vox(raw)
    css = TOKENS.read_text(encoding="utf-8")

    if mode == "link":
        dest = out or target
        rel_s = posix_relpath(TOKENS, dest.parent)
        html = inject_link(html, rel_s)
    else:
        html = inject_inline(html, css)

    html = ensure_body_class(html, family)
    html = ensure_law_footer(html)

    after_fp = scripts_fingerprint(html)
    if before_fp != after_fp:
        return {
            "ok": False,
            "error": "ABORT: script fingerprint changed — VOX must not alter mechanics",
            "before": before_fp,
            "after": after_fp,
        }

    dest = out or target
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "target": str(target),
        "out": str(dest),
        "family": family,
        "mode": mode,
        "script_sha256": after_fp,
        "reducer_present": has_reducer,
        "paid_generation_calls": 0,
        "authority": False,
        "claim": "NO_CLAIM",
    }


def posix_relpath(target: Path, start: Path) -> str:
    import os

    return Path(os.path.relpath(target, start)).as_posix()


def main() -> int:
    p = argparse.ArgumentParser(
        description='Apply WARREN VOX: "alter no mechanics, spend no credits"'
    )
    p.add_argument("--target", required=True, help="HTML surface to skin")
    p.add_argument(
        "--out",
        default="",
        help="Write to this path (default: overwrite target). Prefer --out for demos.",
    )
    p.add_argument(
        "--family",
        default="day",
        choices=["day", "night", "glow"],
        help="Token family (CSS only)",
    )
    p.add_argument(
        "--mode",
        default="inline",
        choices=["inline", "link"],
        help="inline embeds tokens.css; link references it",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Override filename refuse list (still never mutates script bodies)",
    )
    args = p.parse_args()

    target = Path(args.target).resolve()
    if not target.is_file():
        print(f"FAIL: target not found: {target}", file=sys.stderr)
        return 2

    out = Path(args.out).resolve() if args.out else None
    result = apply_vox(target, out, args.family, args.mode, args.force)
    if not result.get("ok"):
        print(f"FAIL: {result.get('error')}", file=sys.stderr)
        return 1

    print("VOX_APPLY_OK")
    for k, v in result.items():
        if k == "ok":
            continue
        print(f"  {k}: {v}")
    print('  one_liner_intent: "Apply WARREN VOX, alter no mechanics, spend no credits"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

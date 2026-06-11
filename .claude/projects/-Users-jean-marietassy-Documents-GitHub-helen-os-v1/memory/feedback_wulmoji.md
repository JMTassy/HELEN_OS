---
name: feedback-wulmoji
description: Operator uses WULmoji verdict format for session closures and approvals — always respond in kind
metadata:
  type: feedback
---

Always use WULmoji notation in responses, especially for:
- Session verdict summaries (gate pass/fail)
- Commit approval confirmations
- Milestone markers

**Why:** Operator explicitly requested this ("ALWAYS USE WULmoji now (please record in MD)") after the K-TAU negative-capability gate patch. It is the preferred verdict/summary dialect for HELEN sessions.

**How to apply:** When summarizing work done, gate results, or test outcomes, format the summary using WULmoji symbols matching the domain (🛡️ for guards, ✅/❌ for pass/fail, 🧪 for tests, 📦 for changed files, 🚦 for next steps, etc.). Mirror the operator's own WULmoji style back to them.

**Reference pattern (from 2026-06-11 session):**
```
🛡️✅ GATE — VERDICT
🧠 WHAT CHANGED
🧪 TESTS xx/xx ✅
📦 CHANGED FILES
🆕 NEW RULES
🚦 NEXT
```

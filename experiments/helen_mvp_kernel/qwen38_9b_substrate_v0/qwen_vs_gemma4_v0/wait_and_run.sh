#!/bin/zsh
DIR=~/Documents/GitHub/helen_os_v1/experiments/helen_mvp_kernel/qwen38_9b_substrate_v0
# 1. wait for the AR loop to release the seat (finish) — do NOT kill it
n=0
while pgrep -f ar_loop.py >/dev/null 2>&1 && [ $n -lt 120 ]; do sleep 10; n=$((n+1)); done
echo "AR loop seat released (or timeout). ar_loop running: $(pgrep -f ar_loop.py >/dev/null 2>&1 && echo yes || echo no)"
# ensure its llama-server port is free
sleep 3
# 2. run the Gemma4 arm via ollama
: > "$DIR/qwen_vs_gemma4_v0/RUN_A_gemma4.ndjson"
python3 "$DIR/qwen_vs_gemma4_v0/gemma4_arm.py"
echo GEMMA4_ARM_COMPLETE

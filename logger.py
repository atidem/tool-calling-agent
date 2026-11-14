import json
from datetime import datetime
from pathlib import Path

#######################################################
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "agent_runs.jsonl"
PRICES = {
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0},
}
#######################################################


def saveLog(question, answer, turns, model):
    
    LOG_DIR.mkdir(exist_ok=True)
    totalIn = sum(t["input_tokens"] for t in turns)
    totalOut = sum(t["output_tokens"] for t in turns)
    totalDuration = round(sum(t["duration_sec"] for t in turns), 2)
    costUsd = calcCost(model, totalIn, totalOut)
    log = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "question": question,
        "answer": answer,
        "total_input_tokens": totalIn,
        "total_output_tokens": totalOut,
        "cost_usd": costUsd,
        "total_duration_sec": totalDuration,
        "turns": turns,
    }

    line = json.dumps(log, ensure_ascii=False)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def calcCost(model, inputTokens, outputTokens):
    price = PRICES.get(model)
    if price is None:
        return None
    cost = inputTokens / 1_000_000 * price["input"] + outputTokens / 1_000_000 * price["output"]
    return round(cost, 6)
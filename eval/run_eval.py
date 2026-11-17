import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import runAgent, MODEL
from logger import calcCost

#######################################################

QUESTIONS_FILE = ROOT / "eval" / "questions.json"
RESULTS_DIR = ROOT / "eval" / "results"
PAUSE_SEC = 3


#######################################################

def normalize(text):
    return text.lower().replace(",", "")

def checkTools(expected, called):
    if expected is None:
        return True, ""
    if not expected:
        if called:
            return False, f"expected no tools, called {sorted(called)}"
        return True, ""
    missing = [t for t in expected if t not in called]
    if missing:
        return False, f"missing tools {missing}"
    return True, ""

def checkAnswer(answer, mustInclude, mustNotInclude):
    text = normalize(answer)
    missing = [w for w in mustInclude if normalize(w) not in text]
    if missing:
        return False, f"missing words {missing}"
    leaked = [w for w in mustNotInclude if normalize(w) in text]
    if leaked:
        return False, f"forbidden words {leaked}"
    return True, ""

def runCase(case):
    answerText, turns = runAgent(case["question"])
    calledTools = {name for t in turns for name in t["tools"]}

    toolsOk, toolsReason = checkTools(case["expected_tools"], calledTools)
    answerOk, answerReason = checkAnswer(answerText, case["must_include"], case["must_not_include"])

    totalIn = sum(t["input_tokens"] for t in turns)
    totalOut = sum(t["output_tokens"] for t in turns)

    return {
        "id": case["id"],
        "category": case["category"],
        "passed": toolsOk and answerOk,
        "reason": "; ".join(r for r in [toolsReason, answerReason] if r),
        "tools_called": sorted(calledTools),
        "turns": len(turns),
        "cost_usd": calcCost(MODEL, totalIn, totalOut),
        "answer": answerText,
    }

def main():
    cases = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    results = []

    for i, case in enumerate(cases, start=1):
        print(f"[{i}/{len(cases)}] {case['id']} ...", end=" ", flush=True)
        result = runCase(case)
        results.append(result)
        print("PASS" if result["passed"] else f"FAIL ({result['reason']})")
        time.sleep(PAUSE_SEC)

        passedCount = sum(1 for r in results if r["passed"])
        totalCost = sum(r["cost_usd"] or 0 for r in results)

        print("\n" + "=" * 50)
        print(f"Model: {MODEL}")
        print(f"Score: {passedCount}/{len(results)}")
        print(f"Total cost: ${totalCost:.4f}")

        failed = [r for r in results if not r["passed"]]
        if failed:
            print("\nFailed cases:")
            for r in failed:
                print(f"- {r['id']}: {r['reason']}")


    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    outFile = RESULTS_DIR / f"results_{MODEL}_{stamp}.json"
    outFile.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved to {outFile.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
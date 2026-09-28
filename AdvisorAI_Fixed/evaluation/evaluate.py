import json
from graph.advising_graph import build_graph

with open("evaluation/test_cases.json") as f:
    cases = json.load(f)

graph = build_graph()
passed = 0
for case in cases:
    result = graph.invoke(case)
    ok = result["validation"]["valid"]
    passed += int(ok)
    print(case["student_id"], result["draft_plan"], "PASS" if ok else "CHECK")

print(f"Validator first/final pass rate: {passed}/{len(cases)}")

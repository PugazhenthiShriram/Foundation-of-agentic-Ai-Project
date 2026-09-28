from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from tools.academic_tools import (
    get_transcript, check_prerequisites, check_degree_requirements,
    check_schedule_conflict, search_catalog
)

class AdvisingState(TypedDict, total=False):
    student_id: str
    request: str
    profile: dict
    evidence: list
    draft_plan: list
    validation: dict
    iteration: int
    status: str

def profile_node(s):
    s["profile"] = get_transcript(s["student_id"])
    s["iteration"] = s.get("iteration", 0)
    return s

def retrieval_node(s):
    p = s["profile"]
    degree = check_degree_requirements(p["major"], p["completed"])
    evidence = []
    for code in degree["remaining_required"]:
        course = next((x for x in search_catalog(code, 3) if x["code"] == code), None)
        if course: evidence.append(course)
    s["evidence"] = evidence
    return s

def planning_node(s):
    completed = set(s["profile"]["completed"])
    candidates = []
    for c in s["evidence"]:
        if c["code"] not in completed and all(x in completed for x in c["prerequisites"]):
            candidates.append(c)
    # Demonstration credit cap: 15 credits.
    plan, credits = [], 0
    for c in candidates:
        if credits + c["credits"] <= 15:
            plan.append(c["code"]); credits += c["credits"]
    s["draft_plan"] = plan
    return s

def validator_node(s):
    completed = s["profile"]["completed"]
    plan = s["draft_plan"]
    errors = []
    for code in plan:
        r = check_prerequisites(code, completed)
        if not r["valid"]:
            errors.append({"type":"prerequisite","course":code,"missing":r["missing"]})
    sc = check_schedule_conflict(plan)
    if not sc["valid"]:
        errors.append({"type":"schedule","conflicts":sc["conflicts"]})
    s["validation"] = {"valid": not errors, "errors": errors}
    s["status"] = "validated" if not errors else "needs_correction"
    s["iteration"] += 1
    return s

def route(s):
    if s["validation"]["valid"] or s["iteration"] >= 3:
        return END
    return "planning"

def build_graph():
    g = StateGraph(AdvisingState)
    g.add_node("profile", profile_node)
    g.add_node("retrieval", retrieval_node)
    g.add_node("planning", planning_node)
    g.add_node("validator", validator_node)
    g.set_entry_point("profile")
    g.add_edge("profile", "retrieval")
    g.add_edge("retrieval", "planning")
    g.add_edge("planning", "validator")
    g.add_conditional_edges("validator", route, {"planning":"planning", END:END})
    return g.compile()

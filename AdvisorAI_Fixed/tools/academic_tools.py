import json, os

BASE = os.path.dirname(os.path.dirname(__file__))

def load(name):
    with open(os.path.join(BASE, "database", name), encoding="utf-8") as f:
        return json.load(f)

def get_transcript(student_id):
    for s in load("students.json"):
        if s["student_id"] == student_id:
            return s
    raise ValueError(f"Student {student_id} not found")

def get_course(code):
    for c in load("catalog.json"):
        if c["code"] == code:
            return c
    return None

def search_catalog(query, k=5):
    q = query.lower()
    courses = load("catalog.json")
    scored = []
    for c in courses:
        text = json.dumps(c).lower()
        score = sum(1 for token in q.split() if token in text)
        scored.append((score, c))
    return [c for score, c in sorted(scored, key=lambda x:x[0], reverse=True)[:k] if score > 0]

def check_prerequisites(course_code, completed_courses):
    c = get_course(course_code)
    if not c:
        return {"valid": False, "error": "Course not found"}
    missing = [p for p in c["prerequisites"] if p not in completed_courses]
    return {"valid": not missing, "course": course_code, "missing": missing}

def check_degree_requirements(major, completed_courses):
    req = load("requirements.json")[major]
    remaining = [x for x in req["required"] if x not in completed_courses]
    return {"remaining_required": remaining, "electives_remaining": req["electives"]}

def check_schedule_conflict(course_list):
    schedules = load("schedule.json")
    seen = {}
    conflicts = []
    for code in course_list:
        slot = schedules.get(code)
        if not slot: continue
        if slot in seen:
            conflicts.append([seen[slot], code, slot])
        seen[slot] = code
    return {"valid": not conflicts, "conflicts": conflicts}

import streamlit as st
from graph.advising_graph import build_graph
from tools.academic_tools import check_prerequisites, check_schedule_conflict

st.set_page_config(page_title="AdvisorAI", page_icon="🎓", layout="wide")

if "result" not in st.session_state:
    st.session_state.result = None
if "approval" not in st.session_state:
    st.session_state.approval = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "reject_mode" not in st.session_state:
    st.session_state.reject_mode = False

def validate_plan(plan, completed):
    errors = []
    for course in plan:
        r = check_prerequisites(course, completed)
        if not r["valid"]:
            errors.append(f"{course}: missing {', '.join(r['missing'])}")
    s = check_schedule_conflict(plan)
    if not s["valid"]:
        for x in s["conflicts"]:
            errors.append(f"Schedule conflict: {x[0]} and {x[1]} ({x[2]})")
    return not errors, errors

with st.sidebar:
    st.header("👨‍🎓 Student")
    student_id = st.selectbox("Student ID", ["STU001", "STU002"])
    request = st.text_area("Advising request",
        "What courses should I take next semester?")
    generate = st.button("🎯 Generate Academic Plan", type="primary",
                         use_container_width=True)

if generate:
    st.session_state.approval = None
    st.session_state.edit_mode = False
    st.session_state.reject_mode = False
    with st.spinner("Running Profile → Retrieval → Planning → Validation..."):
        st.session_state.result = build_graph().invoke(
            {"student_id": student_id, "request": request})

st.title("🎓 AdvisorAI")
st.caption("Multi-Agent Academic Advising System with Agentic RAG")

result = st.session_state.result
if result is None:
    st.info("Select a student and click Generate Academic Plan.")
    st.stop()

profile = result["profile"]
a,b,c,d = st.columns(4)
a.metric("GPA", profile["gpa"])
b.metric("Completed", len(profile["completed"]))
c.metric("Iterations", result["iteration"])
d.metric("Major", profile["major"])

st.subheader(f"📚 Proposed Course Plan — {profile['name']}")
plan = result["draft_plan"]
if plan:
    for course in plan:
        st.success(f"📘 {course}")
else:
    st.warning("No automatically valid courses were found.")

with st.expander("🔎 Retrieved Academic Evidence"):
    st.json(result["evidence"])

st.subheader("✅ Validator")
if result["validation"]["valid"]:
    st.success("Prerequisites, degree logic, and schedule checks passed.")
else:
    st.error("Validator found issues.")
    st.json(result["validation"])

st.divider()
st.subheader("👨‍🏫 Human-in-the-Loop Approval")
st.info("The plan is NOT final until an academic advisor reviews it.")

if st.session_state.approval == "approved":
    st.success("🎉 PLAN APPROVED — Advisor approval recorded.")
elif st.session_state.approval == "rejected":
    st.error("❌ PLAN REJECTED — Advisor rejection recorded.")
elif st.session_state.approval == "edited":
    st.warning("✏️ Edited plan passed validation and is awaiting approval.")

x,y,z = st.columns(3)

with x:
    if st.button("✅ Approve Plan", use_container_width=True):
        if result["validation"]["valid"]:
            st.session_state.approval = "approved"
            st.session_state.edit_mode = False
            st.session_state.reject_mode = False
            st.rerun()
        else:
            st.error("Cannot approve: Validator found errors.")

with y:
    if st.button("✏️ Edit & Revalidate", use_container_width=True):
        st.session_state.edit_mode = True
        st.session_state.reject_mode = False

with z:
    if st.button("❌ Reject", use_container_width=True):
        st.session_state.reject_mode = True
        st.session_state.edit_mode = False

if st.session_state.edit_mode:
    st.divider()
    st.subheader("✏️ Edit Course Plan")
    edited = st.text_input("Course codes separated by commas",
                           value=", ".join(plan))
    if st.button("🔍 Validate Edited Plan", type="primary"):
        new_plan = [v.strip().upper() for v in edited.split(",") if v.strip()]
        valid, errors = validate_plan(new_plan, profile["completed"])
        if valid:
            result["draft_plan"] = new_plan
            result["validation"] = {"valid": True, "errors": []}
            st.session_state.result = result
            st.session_state.approval = "edited"
            st.session_state.edit_mode = False
            st.rerun()
        else:
            st.error("❌ Edited plan failed validation.")
            for error in errors:
                st.warning(error)

if st.session_state.reject_mode:
    st.divider()
    st.subheader("❌ Reject Plan")
    reason = st.text_area("Advisor comments / reason for rejection")
    if st.button("Submit Rejection", type="primary"):
        if reason.strip():
            st.session_state.approval = "rejected"
            st.session_state.reject_mode = False
            st.rerun()
        else:
            st.warning("Please enter a reason.")

with st.expander("🧾 Audit / Agent State"):
    st.json({"draft_plan": result["draft_plan"],
             "validation": result["validation"],
             "iterations": result["iteration"],
             "approval": st.session_state.approval})

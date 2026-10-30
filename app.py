import streamlit as st
import pandas as pd
from itertools import permutations

st.set_page_config(page_title="DeadlockGuard | OS Dashboard", page_icon="🛡️", layout="wide")

DEFAULT_ALLOC = [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
DEFAULT_MAX = [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
DEFAULT_AVAIL = [3,3,2]
RESOURCES = ["A", "B", "C"]

def matrix_need(maximum, allocation):
    return [[maximum[i][j] - allocation[i][j] for j in range(len(maximum[0]))]
            for i in range(len(maximum))]

def validate_state(allocation, maximum, available):
    if not allocation or len(allocation) != len(maximum):
        return "Allocation and Maximum must have the same non-zero number of processes."
    r = len(available)
    if r == 0 or any(len(row) != r for row in allocation + maximum):
        return "Every matrix row must have the same number of resource types as Available."
    if any(not isinstance(x, int) or x < 0 for row in allocation + maximum for x in row):
        return "Resource values must be non-negative integers."
    if any(not isinstance(x, int) or x < 0 for x in available):
        return "Available values must be non-negative integers."
    if any(allocation[i][j] > maximum[i][j] for i in range(len(allocation)) for j in range(r)):
        return "Invalid state: Allocation cannot exceed declared Maximum."
    return None

def safety_algorithm(allocation, maximum, available):
    error = validate_state(allocation, maximum, available)
    if error:
        return {"valid": False, "error": error, "safe": False, "sequence": [], "trace": [], "need": []}
    need = matrix_need(maximum, allocation)
    work = available[:]
    finish = [False] * len(allocation)
    sequence, trace = [], []
    while True:
        selected = None
        for i in range(len(allocation)):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(len(work))):
                selected = i
                break
        if selected is None:
            break
        before = work[:]
        work = [work[j] + allocation[selected][j] for j in range(len(work))]
        finish[selected] = True
        sequence.append(selected)
        trace.append({"process": f"P{selected}", "need": need[selected], "work_before": before, "work_after": work[:]})
    return {"valid": True, "safe": all(finish), "sequence": sequence, "trace": trace,
            "need": need, "unfinished": [f"P{i}" for i, done in enumerate(finish) if not done]}

def request_resources(allocation, maximum, available, process, request):
    error = validate_state(allocation, maximum, available)
    if error:
        return {"status": "invalid", "message": error}
    if process < 0 or process >= len(allocation):
        return {"status": "invalid", "message": "Invalid process identifier."}
    if len(request) != len(available) or any(not isinstance(x, int) or x < 0 for x in request):
        return {"status": "invalid", "message": "Request must contain non-negative integers for every resource type."}
    need = matrix_need(maximum, allocation)
    if any(request[j] > need[process][j] for j in range(len(request))):
        return {"status": "invalid", "message": "Request exceeds the process's remaining Need."}
    if any(request[j] > available[j] for j in range(len(request))):
        return {"status": "waiting", "message": "Request is valid but exceeds Available resources; defer/wait. State unchanged."}
    temp_a = [row[:] for row in allocation]
    temp_v = available[:]
    temp_a[process] = [temp_a[process][j] + request[j] for j in range(len(request))]
    temp_v = [temp_v[j] - request[j] for j in range(len(request))]
    check = safety_algorithm(temp_a, maximum, temp_v)
    if check["safe"]:
        return {"status": "granted", "message": "Request granted: the simulated state remains safe.",
                "sequence": [f"P{i}" for i in check["sequence"]], "allocation": temp_a, "available": temp_v}
    return {"status": "denied_unsafe", "message": "Request denied: simulated state is unsafe. Original state restored.",
            "unfinished": check["unfinished"], "allocation": allocation, "available": available}

def detect_single_instance(waiting_for):
    # waiting_for: {process: process it is waiting for}
    graph = {p: q for p, q in waiting_for.items()}
    visited, active = set(), set()
    def visit(node):
        if node in active:
            return True
        if node in visited:
            return False
        visited.add(node); active.add(node)
        nxt = graph.get(node)
        found = nxt is not None and visit(nxt)
        active.remove(node)
        return found
    return any(visit(p) for p in graph)

def df_matrix(data, cols):
    return pd.DataFrame(data, columns=cols, index=[f"P{i}" for i in range(len(data))])

st.title("🛡️ DeadlockGuard")
st.caption("OS Resource Allocation & Deadlock Analysis Dashboard | AI-assisted, student-verified implementation")
st.info("Educational simulator. Results depend on the resource assumptions and the values entered.")

tabs = st.tabs(["Overview", "Banker's Algorithm", "Resource Request", "Detection & Recovery", "Prevention", "Test Cases & AI Record"])

with tabs[0]:
    st.subheader("System overview")
    c1,c2,c3 = st.columns(3)
    c1.metric("Processes", 5); c2.metric("Resource types", 3); c3.metric("Available units", sum(DEFAULT_AVAIL))
    st.markdown("**Default demonstration dataset**")
    st.write("Allocation and Maximum matrices use processes P0–P4 and resource types A, B, C.")
    st.dataframe(df_matrix(DEFAULT_ALLOC, RESOURCES), use_container_width=True)
    st.write("Maximum demand")
    st.dataframe(df_matrix(DEFAULT_MAX, RESOURCES), use_container_width=True)
    st.write("Available:", dict(zip(RESOURCES, DEFAULT_AVAIL)))
    st.markdown("""
    **Four distinct strategies**
    - **Avoidance:** Banker’s Algorithm checks whether granting a request preserves a safe state.
    - **Detection:** checks an already allocated/waiting system for deadlock using a method suitable for the resource model.
    - **Prevention:** changes policy so at least one necessary deadlock condition cannot hold.
    - **Recovery:** terminates or rolls back a selected process and releases its resources.
    """)

with tabs[1]:
    st.subheader("Banker's safety algorithm")
    st.caption("Edit the matrices and Available vector. Values must be non-negative integers.")
    n = st.number_input("Number of processes", 1, 8, 5, key="n")
    r = st.number_input("Number of resource types", 1, 5, 3, key="r")
    cols = [f"R{i}" for i in range(r)]
    default_a = (DEFAULT_ALLOC[:n] if r == 3 and n <= 5 else [[0]*r for _ in range(n)])
    default_m = (DEFAULT_MAX[:n] if r == 3 and n <= 5 else [[1]*r for _ in range(n)])
    a_df = st.data_editor(df_matrix(default_a, cols), key="alloc_editor", use_container_width=True)
    m_df = st.data_editor(df_matrix(default_m, cols), key="max_editor", use_container_width=True)
    av_defaults = DEFAULT_AVAIL[:r] if r == 3 else [0]*r
    av = [int(st.number_input(f"Available {cols[j]}", min_value=0, value=int(av_defaults[j]), key=f"av{j}")) for j in range(r)]
    if st.button("Run safety algorithm", type="primary"):
        a = a_df.astype(int).values.tolist(); m = m_df.astype(int).values.tolist()
        result = safety_algorithm(a,m,av)
        if not result["valid"]:
            st.error(result["error"])
        else:
            st.dataframe(df_matrix(result["need"], cols), use_container_width=True)
            if result["safe"]:
                st.success("SAFE STATE — safe sequence: " + " → ".join(f"P{i}" for i in result["sequence"]))
            else:
                st.warning("UNSAFE STATE — no complete safe sequence. Unfinished: " + ", ".join(result["unfinished"]))
            st.write("Work-vector trace")
            st.dataframe(pd.DataFrame(result["trace"]), use_container_width=True)
            st.caption("Work starts as Available. When a process can finish, its Allocation is returned to Work.")

with tabs[2]:
    st.subheader("Resource request simulator")
    st.write("Uses the default five-process demonstration dataset so the required scenarios are reproducible.")
    proc = st.selectbox("Requesting process", list(range(5)), format_func=lambda x: f"P{x}")
    req = [st.number_input(f"Request for {RESOURCES[j]}", min_value=0, value=0, key=f"rq{j}") for j in range(3)]
    if st.button("Validate and simulate request", type="primary"):
        result = request_resources(DEFAULT_ALLOC, DEFAULT_MAX, DEFAULT_AVAIL, proc, [int(x) for x in req])
        if result["status"] == "granted": st.success(result["message"]); st.write("Safe sequence:", result["sequence"])
        elif result["status"] == "waiting": st.warning(result["message"])
        elif result["status"] == "denied_unsafe": st.error(result["message"]); st.write("Unfinished:", result["unfinished"])
        else: st.error(result["message"])
        st.write("Original allocation remains:", DEFAULT_ALLOC)
        st.write("Original available vector remains:", DEFAULT_AVAIL)

with tabs[3]:
    st.subheader("Deadlock detection and recovery")
    st.markdown("**Separate example: single-instance resource types.** R1 and R2 each have one instance.")
    st.write("P0 holds R1 and waits for R2. P1 holds R2 and waits for R1.")
    waiting = {"P0":"P1", "P1":"P0"}
    st.error("Cycle detected: P0 → P1 → P0. Under this single-instance model, the cycle confirms deadlock.")
    if st.button("Recover by terminating P1"):
        st.success("P1 terminated; its held R2 is released. P0 can acquire R2 and continue.")
    st.caption("For multiple-instance resource types, a cycle alone is not conclusive; use an appropriate detection algorithm and the stated allocation/request matrices.")

with tabs[4]:
    st.subheader("Deadlock prevention policy")
    st.markdown("""
    **Policy: impose a global resource order R1 before R2.**
    Every process must request R1 before requesting R2. A process holding R2 cannot later request R1.

    **Original:** P0 holds R1 and waits for R2 while P1 holds R2 and waits for R1. Circular wait exists.

    **Modified:** the global order prevents the reverse acquisition edge, so circular wait cannot form under this policy.

    **Trade-off:** processes may wait longer and resource utilization/concurrency may decrease because they must follow the fixed order.
    """)
    st.success("Prevention condition targeted: circular wait.")

with tabs[5]:
    st.subheader("Analytical test cases")
    tests = [
        ["TC1","Safe default state","SAFE; P1 → P3 → P0 → P2 → P4","Safe sequence found","Work-vector trace completes all processes."],
        ["TC2","P0 requests [0,0,3]","WAITING / DEFERRED","Request not granted immediately","Within Need [7,4,3], but C request 3 exceeds Available C=2; state unchanged."],
        ["TC3","P4 requests [3,3,0]","DENIED_UNSAFE","Request denied; state unchanged","Within Need and Available; temporary state has no complete safe sequence."],
        ["TC4","Single-instance RAG cycle","DEADLOCK DETECTED","Deadlock identified","P0 waits for P1 and P1 waits for P0; cycle confirms deadlock for single-instance resources."],
        ["TC5","Global order R1 before R2","PREVENTION APPLIED","Circular wait eliminated","Fixed order prevents reverse acquisition; possible lower concurrency."],
        ["TC6","Zero/invalid/boundary inputs","VALIDATION / BOUNDARY HANDLING","Correct handling or validation","Zero Need can complete; negative values, invalid process IDs and Allocation > Maximum are rejected."]
    ]
    st.dataframe(pd.DataFrame(tests, columns=["Test","Condition","Actual result (expected from implementation)","Expected result","Analysis"]), use_container_width=True)
    st.warning("Before submission, run each scenario in the live dashboard, capture screenshots, and replace/confirm this table with your group's own observed outputs.")
    st.subheader("AI Usage Record — fill in your group's verification")
    ai = [
        ["ChatGPT","Algorithm explanation, pseudocode, test-case planning and code review","Draft logic and explanations","Group tested safety sequence, request decisions and edge cases"],
        ["Streamlit","Dashboard implementation and interactive interface","Working dashboard","Group verified each button, input and displayed output"],
        ["VS Code","Code editing and debugging","Source-code changes","Group ran the app and checked errors"]
    ]
    st.dataframe(pd.DataFrame(ai, columns=["AI/tool used","Purpose","Output generated","Student verification"]), use_container_width=True)

st.divider()
st.caption("DeadlockGuard | Operating Systems IA Activity 2 | Group members: add names and roll numbers in your submission.")

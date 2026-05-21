# acn/dashboard/consensus_dashboard.py
"""
ACN Consensus Dashboard: Real-time L0-L3 layered memory observability.

Shows:
- Swarm health metrics with live memory layer counts
- L0 Conversation timeline
- L1 Atom distribution and growth
- L2 Scenario pattern cards
- L3 Persona evolution (confidence maps, heuristics, biases)
- Cross-layer evolution timeline

Run: streamlit run acn/dashboard/consensus_dashboard.py

[CITATION: SelfInterview2026]
[CITATION: LAYERED-MEMORY]
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
from datetime import datetime

st.set_page_config(page_title="ACN Layered Memory Observatory", layout="wide")

# ── Data Loading ─────────────────────────────────────────────────────
@st.cache_data(ttl=2)
def load_dashboard_state() -> Dict[str, Any]:
    """Load the latest dashboard state from the collector's JSON file."""
    import sys
    sys.path.insert(0, "acn/src")
    from dashboard.data_collector import DashboardDataCollector
    return DashboardDataCollector.load_for_dashboard()

state = load_dashboard_state()

# ── Sidebar: System Status ─────────────────────────────────────────
st.sidebar.header("🧠 ACN System Status")

swarm = state.get("swarm", {})
consensus = state.get("consensus", {})
last_updated = state.get("last_updated", 0)

st.sidebar.metric("Active Twins", swarm.get("total_twins", 0))
st.sidebar.metric("L0 Traces", swarm.get("total_l0_traces", 0))
st.sidebar.metric("L1 Atoms", swarm.get("total_l1_atoms", 0))
st.sidebar.metric("L2 Scenarios", swarm.get("total_l2_scenarios", 0))
st.sidebar.metric("L3 Personas", swarm.get("total_l3_personas", 0))

if last_updated:
    ago = datetime.now().timestamp() - last_updated
    st.sidebar.caption(f"Last update: {ago:.1f}s ago")
else:
    st.sidebar.caption("No data yet — run a swarm deliberation")

# Twin selector
twins = state.get("twins", {})
twin_options = ["(All Twins)"] + list(twins.keys())
selected_twin = st.sidebar.selectbox("🔍 Select Twin", twin_options)

auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (2s)", value=True)
if auto_refresh:
    st.sidebar.caption("Dashboard refreshes automatically")
    st_autorefresh = st.empty()

# ── Header ───────────────────────────────────────────────────────────
st.title("🧠 ACN Layered Memory Observatory")
st.markdown("*Real-time L0→L1→L2→L3 memory evolution for digital twins*")

# ── Top Row: Consensus + Swarm Health ──────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    score = consensus.get("score", 0.0)
    st.metric("Consensus Score", f"{score:.2f}")
    if score >= 0.75:
        st.success("✅ Reached")
    elif score >= 0.5:
        st.warning("⚠️ Partial")
    else:
        st.error("❌ None")

with col2:
    acad = consensus.get("academic_support", 0.0)
    st.metric("Academic Support", f"{acad:.2f}")
    if acad >= 0.8:
        st.success("📖 Strong")
    elif acad >= 0.5:
        st.warning("📖 Moderate")
    else:
        st.error("📖 Weak")

with col3:
    dissent = consensus.get("dissent_detected", False)
    if dissent:
        st.error("🚨 DISSENT")
        st.caption("Agents agree but literature contradicts")
    elif score > 0.95:
        st.warning("⚠️ GROUPTHINK RISK")
    else:
        st.success("✅ Healthy")

with col4:
    st.metric("Memory Layers", f"{swarm.get('total_l3_personas', 0)}L3 / {swarm.get('total_l2_scenarios', 0)}L2")

st.divider()

# ── Main Tabs ────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Overview",
    "💬 L0: Conversation",
    "⚛️ L1: Atoms",
    "🔄 L2: Scenarios",
    "👤 L3: Persona",
    "📈 Evolution",
    "🖥️ VM Cluster",
])

# ── Tab 0: Overview ──────────────────────────────────────────────────
with tabs[0]:
    st.header("Swarm Overview")

    # Layer distribution bar chart
    layer_data = {
        "Layer": ["L0 Conversation", "L1 Atoms", "L2 Scenarios", "L3 Persona"],
        "Count": [
            swarm.get("total_l0_traces", 0),
            swarm.get("total_l1_atoms", 0),
            swarm.get("total_l2_scenarios", 0),
            swarm.get("total_l3_personas", 0),
        ],
    }
    fig = px.bar(
        layer_data, x="Layer", y="Count",
        color="Layer",
        color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96", "#AB63FA"],
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

    # Twin summary table
    if twins:
        st.subheader("Twin Memory Profiles")
        twin_rows = []
        for tid, tdata in twins.items():
            lc = tdata.get("layer_counts", {})
            twin_rows.append({
                "Twin": tdata.get("name", tid),
                "Cluster": tdata.get("cluster", ""),
                "L0": lc.get("l0", 0),
                "L1": lc.get("l1", 0),
                "L2": lc.get("l2", 0),
                "L3": lc.get("l3", 0),
            })
        st.dataframe(twin_rows, use_container_width=True)
    else:
        st.info("No twin data available. Run a deliberation to populate.")

    # Recent events
    events = state.get("recent_events", [])
    if events:
        st.subheader("Recent Events")
        for ev in events[-10:]:
            ts = datetime.fromtimestamp(ev.get("timestamp", 0)).strftime("%H:%M:%S")
            st.caption(f"[{ts}] {ev.get('type', 'event').upper()}: {ev}")

# ── Tab 1: L0 Conversation ───────────────────────────────────────────
with tabs[1]:
    st.header("💬 L0: Conversation Memory")
    st.caption("Raw reasoning traces and deliberation transcripts")

    twin_data = twins.get(selected_twin, {}) if selected_twin != "(All Twins)" else None

    if twin_data:
        traces = twin_data.get("l0_traces", [])
        st.metric("Traces for this twin", len(traces))
        for trace in traces[:10]:
            with st.expander(f"📝 {trace.get('trace_id', 'trace')} | {trace.get('timestamp', 0):.0f}"):
                st.write(trace.get("content_preview", "No preview"))
    elif selected_twin == "(All Twins)" and twins:
        all_traces = []
        for tid, td in twins.items():
            for t in td.get("l0_traces", []):
                t["twin"] = td.get("name", tid)
                all_traces.append(t)
        st.metric("Total traces across swarm", len(all_traces))
        for trace in sorted(all_traces, key=lambda x: x.get("timestamp", 0), reverse=True)[:10]:
            with st.expander(f"📝 {trace.get('twin', '')}: {trace.get('trace_id', '')}"):
                st.write(trace.get("content_preview", "No preview"))
    else:
        st.info("No L0 traces available for this twin.")

# ── Tab 2: L1 Atoms ──────────────────────────────────────────────────
with tabs[2]:
    st.header("⚛️ L1: Atom Memory")
    st.caption("Structured facts extracted from raw traces")

    if twins:
        # Collect all atoms across selected twins
        all_atoms = []
        target_twins = [selected_twin] if selected_twin != "(All Twins)" else list(twins.keys())
        for tid in target_twins:
            td = twins.get(tid, {})
            for a in td.get("l1_atoms", []):
                a["twin"] = td.get("name", tid)
                all_atoms.append(a)

        # Atom type distribution
        if all_atoms:
            from collections import Counter
            type_counts = Counter(a.get("atom_type", "unknown") for a in all_atoms)

            c1, c2 = st.columns(2)
            with c1:
                fig = px.pie(
                    names=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    title="Atom Type Distribution",
                    hole=0.4,
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.metric("Total Atoms", len(all_atoms))
                st.subheader("Type Breakdown")
                for atype, count in type_counts.most_common():
                    st.write(f"- **{atype}**: {count}")

            # Recent atoms table
            st.subheader("Recent Atoms")
            atom_rows = []
            for a in sorted(all_atoms, key=lambda x: x.get("confidence", 0), reverse=True)[:20]:
                atom_rows.append({
                    "Twin": a.get("twin", ""),
                    "Type": a.get("atom_type", ""),
                    "Content": a.get("content", "")[:80],
                    "Confidence": f"{a.get('confidence', 0):.2f}",
                    "Tags": ", ".join(a.get("tags", [])[:3]),
                })
            st.dataframe(atom_rows, use_container_width=True)
        else:
            st.info("No L1 atoms yet. Atoms are created when twins think and traces are atomized.")
    else:
        st.info("No twin data available.")

# ── Tab 3: L2 Scenarios ──────────────────────────────────────────────
with tabs[3]:
    st.header("🔄 L2: Scenario Memory")
    st.caption("Recurrent behavior patterns mined from atomic facts")

    if twins:
        all_scenarios = []
        target_twins = [selected_twin] if selected_twin != "(All Twins)" else list(twins.keys())
        for tid in target_twins:
            td = twins.get(tid, {})
            for s in td.get("l2_scenarios", []):
                s["twin"] = td.get("name", tid)
                all_scenarios.append(s)

        if all_scenarios:
            st.metric("Total Scenarios", len(all_scenarios))

            # Scenario cards
            cols = st.columns(2)
            for i, scen in enumerate(sorted(all_scenarios, key=lambda x: x.get("support_count", 0), reverse=True)[:10]):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.write(f"**{scen.get('template', 'Pattern')}**")
                        st.caption(f"Twin: {scen.get('twin', '')}")
                        st.write(f"📊 Support: {scen.get('support_count', 0)} | Confidence: {scen.get('confidence', 0):.2f}")
                        st.write(f"🔑 Keywords: {', '.join(scen.get('context_keywords', [])[:5])}")

            # Support distribution
            support_data = {
                "Scenario": [f"S{i+1}" for i in range(len(all_scenarios))],
                "Support": [s.get("support_count", 0) for s in all_scenarios],
            }
            fig = px.bar(
                support_data, x="Scenario", y="Support",
                title="Scenario Support Counts",
                color="Support",
                color_continuous_scale="Viridis",
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No L2 scenarios yet. Run consolidation (L1→L2) to mine patterns.")
    else:
        st.info("No twin data available.")

# ── Tab 4: L3 Persona ────────────────────────────────────────────────
with tabs[4]:
    st.header("👤 L3: Persona Memory")
    st.caption("Evolved cognitive profiles from scenario distillation")

    if twins:
        target_twins = [selected_twin] if selected_twin != "(All Twins)" else list(twins.keys())

        for tid in target_twins:
            td = twins.get(tid, {})
            persona = td.get("l3_persona")
            if persona:
                st.subheader(f"🎭 {td.get('name', tid)} — Persona v{persona.get('version', 1)}")

                # Confidence map radar
                conf_map = persona.get("confidence_map", {})
                if conf_map:
                    categories = list(conf_map.keys())[:8]
                    values = [conf_map.get(c, 0) for c in categories]
                    values.append(values[0])  # Close the radar
                    categories.append(categories[0])

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name='Confidence',
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=False,
                        height=400,
                        title="Confidence Map",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Heuristic calibration
                heuristics = persona.get("heuristic_evidence", {})
                if heuristics:
                    st.subheader("Heuristic Calibration")
                    h_data = {
                        "Heuristic": list(heuristics.keys()),
                        "Success Rate": [h.get("success_rate", 0.5) for h in heuristics.values()],
                        "Support Count": [h.get("support_count", 0) for h in heuristics.values()],
                    }
                    fig = px.bar(
                        h_data, x="Heuristic", y="Success Rate",
                        color="Support Count",
                        title="Empirical Heuristic Validation",
                        range_y=[0, 1],
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

                # Bias manifestations
                biases = persona.get("bias_manifestations", {})
                if biases:
                    st.subheader("Bias Manifestations")
                    for bias_name, contexts in biases.items():
                        st.write(f"**{bias_name}**: manifests in {', '.join(contexts[:5])}")

                # Expertise boundaries
                boundaries = persona.get("expertise_boundaries", {})
                if boundaries:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.success("**Strong Areas**: " + ", ".join(boundaries.get("strong_in", [])))
                    with c2:
                        st.error("**Weak Areas**: " + ", ".join(boundaries.get("weak_in", [])))
            else:
                st.info(f"No L3 persona for {td.get('name', tid)}. Run consolidation to distill.")
    else:
        st.info("No twin data available.")

# ── Tab 5: Evolution ─────────────────────────────────────────────────
with tabs[5]:
    st.header("📈 Cross-Layer Evolution")
    st.caption("How raw traces become structured knowledge")

    if twins:
        # Layer growth for each twin
        twin_names = []
        l0_counts = []
        l1_counts = []
        l2_counts = []
        l3_counts = []

        for tid, td in twins.items():
            lc = td.get("layer_counts", {})
            twin_names.append(td.get("name", tid))
            l0_counts.append(lc.get("l0", 0))
            l1_counts.append(lc.get("l1", 0))
            l2_counts.append(lc.get("l2", 0))
            l3_counts.append(lc.get("l3", 0))

        fig = go.Figure()
        fig.add_trace(go.Bar(name="L0 Traces", x=twin_names, y=l0_counts, marker_color="#636EFA"))
        fig.add_trace(go.Bar(name="L1 Atoms", x=twin_names, y=l1_counts, marker_color="#EF553B"))
        fig.add_trace(go.Bar(name="L2 Scenarios", x=twin_names, y=l2_counts, marker_color="#00CC96"))
        fig.add_trace(go.Bar(name="L3 Personas", x=twin_names, y=l3_counts, marker_color="#AB63FA"))
        fig.update_layout(
            barmode="group",
            title="Layer Growth per Twin",
            xaxis_title="Twin",
            yaxis_title="Count",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Compression ratio: L0 → L1
        total_l0 = sum(l0_counts)
        total_l1 = sum(l1_counts)
        if total_l0 > 0:
            compression = (1 - total_l1 / total_l0) * 100
            st.metric("L0→L1 Compression", f"{compression:.1f}%", "Token reduction")
            st.caption(f"{total_l0} raw traces → {total_l1} structured atoms")

        # Consolidation status
        st.subheader("Consolidation Pipeline")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Atoms → Scenarios", f"{total_l2}/{total_l1}")
        with col_b:
            st.metric("Scenarios → Personas", f"{sum(l3_counts)}/{total_l2}")
        with col_c:
            active_personas = sum(1 for tid, td in twins.items() if td.get("l3_persona"))
            st.metric("Active Personas", active_personas)
    else:
        st.info("No evolution data yet. Run a swarm task to see cross-layer growth.")

# ── Tab 6: VM Cluster ────────────────────────────────────────────────
with tabs[6]:
    st.header("🖥️ VM Cluster Health")
    st.caption("Persistent twin VM status, hibernation cycles, and checkpoint history")

    vm_cluster = state.get("vm_cluster", {})

    if vm_cluster:
        # Top-level metrics
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total VMs", vm_cluster.get("total_twins", 0))
        with c2:
            st.metric("Active", vm_cluster.get("active", 0))
        with c3:
            st.metric("Hibernated", vm_cluster.get("hibernated", 0))
        with c4:
            st.metric("Destroyed", vm_cluster.get("destroyed", 0))
        with c5:
            st.metric("Checkpoints", vm_cluster.get("total_checkpoints", 0))

        # Compute time
        compute_ms = vm_cluster.get("total_compute_time_ms", 0.0)
        st.metric("Total Compute Time", f"{compute_ms:.0f} ms")

        # Per-VM status table
        vm_twins = vm_cluster.get("twins", [])
        if vm_twins:
            st.subheader("Per-VM Status")
            vm_rows = []
            for vm in vm_twins:
                vm_rows.append({
                    "Twin ID": vm.get("twin_id", ""),
                    "Name": vm.get("name", ""),
                    "State": vm.get("state", ""),
                    "Thinks": vm.get("thinks", 0),
                    "Hibernates": vm.get("hibernates", 0),
                    "Checkpoints": vm.get("checkpoints", 0),
                    "Compute (ms)": f"{vm.get('compute_ms', 0):.0f}",
                })
            st.dataframe(vm_rows, use_container_width=True)

            # State distribution pie chart
            from collections import Counter
            state_counts = Counter(vm.get("state", "unknown") for vm in vm_twins)
            fig = px.pie(
                names=list(state_counts.keys()),
                values=list(state_counts.values()),
                title="VM State Distribution",
                hole=0.4,
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No per-VM data available.")
    else:
        st.info("No VM cluster data. Run an AutonomousExecutor with vm_cluster to populate.")

# ── Footer ───────────────────────────────────────────────────────────
st.divider()
st.caption("ACN Autonomous Cognitive Network | Layered Memory Architecture | Research-grounded consensus")

# Auto-refresh trigger
if auto_refresh:
    import time
    time.sleep(0.1)
    st_autorefresh.empty()
    st.rerun()

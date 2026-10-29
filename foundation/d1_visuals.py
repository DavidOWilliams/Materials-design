"""D1 v0.2 — presentation-only charts from independently verified WP3/WP4 records.

No synthesis, scientific modelling, qualification or Pareto recalculation is performed.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
import altair as alt

OBJECTIVES = (
    ("thermal_transmission", "Thermal transmission", "W/m²"),
    ("areal_mass", "Areal mass", "kg/m²"),
    ("tensile_thermal_mismatch", "Tensile thermal mismatch", "Pa"),
)
COLORS = ["#2476b5", "#cc832b", "#369e8a", "#8759ba", "#bb536b"]


from d1_visual_data import _value, _valid, _pareto_ids, _rows, _estimated_design

def campaign_view(data, *, scope: str, key: str):
    """Display only a single campaign's values; never pool WP3 and WP4."""
    phase = "WP4" if "WP4" in scope else "WP3"
    rows = data.get("rows", [])
    st.subheader(scope + " — performance and trade-offs")
    st.caption("Synthetic numerical results. Lower is preferred for every shown objective. "
               "WP3 is intended-state numerical eligibility; WP4 is separate conditional estimated-achieved feasibility.")
    if not rows:
        st.info("No verified candidates to compare.")
        return None
    table = pd.DataFrame(rows)
    st.markdown("**Trade-off plot — choose two objectives**")
    x = st.selectbox("Horizontal objective", [o[0] for o in OBJECTIVES],
                     format_func=lambda k: next(n + " (" + u + ")" for f,n,u in OBJECTIVES if f == k),
                     index=1, key=key+"_x")
    y = st.selectbox("Vertical objective", [o[0] for o in OBJECTIVES if o[0] != x],
                     format_func=lambda k: next(n + " (" + u + ")" for f,n,u in OBJECTIVES if f == k),
                     key=key+"_y")
    candidates = []
    pareto = _pareto_ids(data.get("pareto"))
    for row in rows:
        a, b = _value(row, x, phase), _value(row, y, phase)
        if a is None or b is None:
            continue
        eligible = _valid(row, phase)
        category = ("Pareto eligible" if eligible and str(row["candidate"]) in pareto
                    else "Eligible, dominated" if eligible else "Excluded or unresolved")
        candidates.append(dict(candidate=str(row["candidate"]), x=a, y=b,
                               classification=category))
    if candidates:
        plot = pd.DataFrame(candidates)
        chart = alt.Chart(plot).mark_circle(size=135, opacity=0.9).encode(
            x=alt.X("x:Q", scale=alt.Scale(zero=False), title=next(n+" ("+u+")" for f,n,u in OBJECTIVES if f==x)),
            y=alt.Y("y:Q", scale=alt.Scale(zero=False), title=next(n+" ("+u+")" for f,n,u in OBJECTIVES if f==y)),
            color=alt.Color("classification:N", scale=alt.Scale(domain=[
                "Pareto eligible","Eligible, dominated","Excluded or unresolved"],
                range=["#16816c","#397bb4","#9a9a9a"])),
            shape=alt.Shape("classification:N"),
            tooltip=["candidate:N","classification:N",alt.Tooltip("x:Q",format=".9g"),alt.Tooltip("y:Q",format=".9g")],
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
        st.caption("Axes deliberately do not assume zero. Only existing finite objective values are plotted; "
                   "status labels and the exact table govern eligibility, not marker position.")
    else:
        st.info("Insufficient resolved objective pairs for a scientific scatter plot.")
    with st.expander("Compare each objective separately"):
        for field, label, unit in OBJECTIVES:
            values = [{"candidate":str(r["candidate"]), "value":_value(r, field, phase)}
                      for r in rows if _value(r, field, phase) is not None]
            st.markdown("**"+label+"** — "+unit+" (minimise)")
            if values:
                st.bar_chart(pd.DataFrame(values).set_index("candidate"), use_container_width=True)
            else:
                st.caption("No resolved values.")
    st.markdown("**Exact source values, exclusions and numerical qualification**")
    st.dataframe(table, use_container_width=True, hide_index=True)
    chosen = st.selectbox("Inspect candidate ID", [r["candidate"] for r in rows], key=key)
    return int(chosen)


def architecture_view(design, *, key="architecture"):
    """A1 spatial-strip plus actual architecture profile; A2 detail from original knots/layers."""
    if not isinstance(design, dict) or "architecture" not in design:
        st.info("No supported intended-design architecture available.")
        return
    kind, rows, entries = _rows(design)
    st.subheader("Material architecture — "+kind.title())
    if not rows:
        st.info("No source-supported composition samples; raw design remains available.")
        return
    frame = pd.DataFrame(rows)
    thickness = design.get("thickness", {})
    length = thickness.get("value")
    unit = thickness.get("unit", "m")
    st.caption("Planar coordinate 0–1 across thickness"
               + (f" (total {length:g} {unit})" if type(length) in (int,float) else "")
               + "; fractions on a "+str(frame.iloc[0]["basis"])+" basis.")
    st.markdown("**A1 — material structure and composition**")
    # The strip is a discrete architecture encoding, not an image of microstructure.
    segments = []
    if kind == "layered":
        for i, layer in enumerate(design["architecture"]["layers"]):
            segments.append(dict(start=float(layer["start"]), end=float(layer["end"]),
                                 segment="Layer "+str(i+1)))
    else:
        # For continuous gradients, show declared knot intervals, not fabricated samples.
        positions = sorted(set(float(p) for p in frame["position"]))
        for i, (a,b) in enumerate(zip(positions, positions[1:])):
            segments.append(dict(start=a,end=b,segment=("Gradient interval " if kind=="gradient" else "Uniform ")+str(i+1)))
    if segments:
        strip = alt.Chart(pd.DataFrame(segments)).mark_rect(stroke="#ffffff").encode(
            x=alt.X("start:Q", title="Normalized thickness position",scale=alt.Scale(domain=[0,1])),
            x2="end:Q", color=alt.Color("segment:N", legend=None),
            tooltip=["segment:N","start:Q","end:Q"]).properties(height=55)
        st.altair_chart(strip, use_container_width=True)
        st.caption("Structural regions are identified by actual interfaces/knots; colours do not represent measured microstructure.")
    line_mode = "linear"
    # Layer boundaries are plotted as separate start/end points; never connect across interfaces.
    if kind == "layered":
        samples=[]
        for i,layer in enumerate(design["architecture"]["layers"]):
            for f in layer["composition"]["fractions"]:
                for pos in (layer["start"],layer["end"]):
                    samples.append({"position":float(pos),"constituent":f["material_id"],"fraction":float(f["fraction"]),"basis":layer["composition"]["basis"],"layer_id":str(i+1)})
        profile_frame=pd.DataFrame(samples)
    else:
        profile_frame=frame.copy()
        profile_frame["layer_id"]="continuous"
    plot = alt.Chart(profile_frame).mark_line(point=(kind=="gradient"), interpolate=line_mode).encode(
        x=alt.X("position:Q", scale=alt.Scale(domain=[0,1]), title="Normalized thickness position"),
        y=alt.Y("fraction:Q", scale=alt.Scale(domain=[0,1]), title="Constituent fraction"),
        color=alt.Color("constituent:N", scale=alt.Scale(range=COLORS)),
        detail="layer_id:N",
        tooltip=["position:Q","constituent:N",alt.Tooltip("fraction:Q",format=".9g"),"basis:N"])
    st.altair_chart(plot, use_container_width=True)
    with st.expander("A2 — exact composition samples and architecture assumptions"):
        st.dataframe(frame[["position","constituent","fraction","basis"]], hide_index=True,
                     use_container_width=True)
        st.caption("For layered architectures, repeated boundary coordinates have distinct left/right values. "
                   "Each row originates from a layer or knot. A gradient is piecewise-linear by contract.")
        st.json({"design_id":design.get("id"),"parent_hashes":design.get("parent_hashes"),
                 "proposal_method":design.get("proposal_method"),
                 "assumptions":design.get("assumptions")})


def feedback_view(record):
    st.subheader("Manufacturing feedback and design lineage")
    st.caption("Intended → synthetic process mapping → estimated achieved state → conditional evaluation → feedback")
    intended = record.get("intended_design")
    if isinstance(intended,dict):
        architecture_view(intended,key="wp4_intended")
    estimated = _estimated_design(record)
    if estimated:
        st.markdown("**C1 — intended and estimated profiles**")
        st.caption("Synthetic process prediction only. Distinct marker/line styles distinguish the states; constituent colours identify material IDs.")
        a_kind, a_rows, _ = _rows(intended)
        b_kind, b_rows, _ = _rows(estimated)
        if (a_kind == b_kind and a_rows and b_rows
                and {r["constituent"] for r in a_rows} == {r["constituent"] for r in b_rows}
                and {r["basis"] for r in a_rows} == {r["basis"] for r in b_rows}):
            both = pd.DataFrame([dict(r, state="Intended") for r in a_rows]+
                                [dict(r, state="Synthetic estimated") for r in b_rows])
            st.altair_chart(alt.Chart(both).mark_line(point=True, interpolate=("step-after" if a_kind=="layered" else "linear")).encode(
                x=alt.X("position:Q",scale=alt.Scale(domain=[0,1])),
                y=alt.Y("fraction:Q",scale=alt.Scale(domain=[0,1])),
                color="constituent:N",strokeDash="state:N",
                tooltip=["state:N","position:Q","constituent:N","fraction:Q"]),
                use_container_width=True)
            # Differences are only defined at positions where both actual records exist.
            left = pd.DataFrame(a_rows); right=pd.DataFrame(b_rows)
            common = left.merge(right,on=["position","constituent","basis"],suffixes=("_intended","_estimated"))
            # Never cross-join duplicated layer interface positions or mix coordinate systems.
            if a_kind == "layered":
                common = common.iloc[0:0]
            if not common.empty:
                common["difference_percentage_points"] = 100*(common["fraction_estimated"]-common["fraction_intended"])
                with st.expander("C3 — differences at matched recorded positions"):
                    st.bar_chart(common.pivot(index="position",columns="constituent",
                                              values="difference_percentage_points"))
                    st.dataframe(common,hide_index=True,use_container_width=True)
                    st.caption("Difference values apply only to matched recorded positions; not interpolated or measured.")
        else:
            st.info("The two profile representations cannot be compared directly without unsupported assumptions.")
    else:
        st.info("The accepted WP4 record does not expose a compatible achieved-design composition profile here. "
                "No hypothetical achieved curve has been drawn; inspect the actual estimated_state and manufacturing commands below.")
    feedback=record.get("feedback")
    if feedback is None:
        st.info("No supported feedback trigger for this candidate. This does not imply an improvement or manufacturing validation.")
    else:
        st.markdown("**Recorded manufacturing constraint feedback**")
        st.dataframe(pd.DataFrame([feedback]),hide_index=True,use_container_width=True)
    with st.expander("Exact estimated inputs, evaluation, mass balances and provenance"):
        st.json({k:record.get(k) for k in ("estimated_inputs","evaluation","balances",
                                          "intended_hash","estimated_hash","evaluation_hash")})

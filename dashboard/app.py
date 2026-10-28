"""Streamlit dashboard for local, sanitized honeypot analytics."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.data_processor import summarize_events
from src.log_parser import ParseDiagnostics, iter_events


st.set_page_config(page_title="HackTheHacker", layout="wide")
st.title("HackTheHacker")
st.caption("Defensive SSH honeypot telemetry. Values shown are observations from the selected file.")

log_path = st.sidebar.text_input("JSONL event file", value="tests/sample_events.jsonl")
path = Path(log_path)

if not path.is_file():
    st.info("Select a local JSONL file to begin. No event data is loaded automatically.")
else:
    diagnostics = ParseDiagnostics()
    events = list(iter_events(path, diagnostics))
    summary = summarize_events(events)
    columns = st.columns(4)
    columns[0].metric("Total events", summary["total_events"])
    columns[1].metric("Unique source IPs", summary["unique_source_ips"])
    columns[2].metric("Authentication attempts", summary["authentication_attempts"])
    columns[3].metric("Malformed lines", diagnostics.malformed_lines)

    left, right = st.columns(2)
    with left:
        st.subheader("Event types")
        st.bar_chart(summary["event_types"])
        st.subheader("Attempted usernames")
        st.table(summary["usernames"])
    with right:
        st.subheader("Source IPs")
        st.table(summary["source_ips"])
        st.subheader("Observed commands")
        st.table(summary["commands"])

    if diagnostics.errors:
        with st.expander("Parser diagnostics"):
            st.write(diagnostics.errors)

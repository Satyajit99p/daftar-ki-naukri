import html
import re
from datetime import datetime

import streamlit as st

from common.data_service import fetch_job_openings


st.set_page_config(page_title="Job Openings", layout="wide")

st.markdown(
    """
    <style>
        .tab-card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
            background: #ffffff;
            color: #111827;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            margin-bottom: 16px;
            min-height: 190px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
        }
        .tab-title {
            font-size: 1.05rem;
            font-weight: 600;
            margin: 0 0 6px 0;
            white-space: normal;
            word-break: break-word;
            overflow-wrap: anywhere;
        }
        .tab-meta {
            font-size: 0.9rem;
            color: #4b5563;
            margin: 0 0 10px 0;
        }
        .tab-link {
            font-weight: 600;
            color: #1d4ed8;
            text-decoration: none;
        }
        .tab-link:hover {
            text-decoration: underline;
        }
        @media (prefers-color-scheme: dark) {
            .tab-card {
                background: #0f172a;
                color: #f8fafc;
                border-color: #1f2937;
                box-shadow: 0 1px 2px rgba(0,0,0,0.4);
            }
            .tab-meta {
                color: #cbd5f5;
            }
            .tab-link {
                color: #93c5fd;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("Government Job Openings")

records = fetch_job_openings()

if not records:
    st.info("No job openings found.")
    st.stop()


def _normalize_tag(tag_value):
    if not tag_value:
        return None

    if isinstance(tag_value, str):
        normalized = re.sub(r"\s+", " ", tag_value).strip()
        return normalized or None

    return str(tag_value).strip() or None


def _format_date(value):
    if not value:
        return "N/A"

    if isinstance(value, datetime):
        return value.strftime("%d %b %Y")

    if isinstance(value, str):
        clean_value = value.replace("T", "+00:00")
        try:
            return datetime.fromisoformat(clean_value).strftime("%d %b %Y")
        except ValueError:
            return value

    return str(value)


def _render_cards(records_to_render):
    for idx in range(0, len(records_to_render), 3):
        columns = st.columns(3)
        row_records = records_to_render[idx : idx + 3]
        for column, record in zip(columns, row_records):
            with column:
                title = html.escape(record["title"])
                posted_date = html.escape(record["posted_date"])
                deadline = html.escape(record["deadline"])
                url = record["url"] or "#"
                st.markdown(
                    f"""
                    <div class="tab-card">
                        <div class="tab-title">{title}</div>
                        <div class="tab-meta">Posted: {posted_date} | Deadline: {deadline}</div>
                        <a class="tab-link" href="{url}" target="_blank" rel="noopener noreferrer">Open job posting</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


cards_by_government = {}
for record in records:
    government_body = record.get("government_body") or "Unknown"
    job_tag = _normalize_tag(record.get("job_tag"))
    cards_by_government.setdefault(government_body, []).append(
        {
            "job_tag": job_tag,
            "title": record.get("title") or "Untitled",
            "posted_date": _format_date(record.get("posted_date")),
            "deadline": _format_date(record.get("deadline")),
            "url": record.get("url"),
        }
    )

sorted_bodies = sorted(cards_by_government.keys(), key=str.casefold)

body_tabs = st.tabs(sorted_bodies)

for body_name, body_tab in zip(sorted_bodies, body_tabs):
    with body_tab:
        body_records = cards_by_government.get(body_name, [])
        tags = sorted(
            {record["job_tag"] for record in body_records if record["job_tag"]},
            key=str.casefold,
        )

        if tags:
            subtab_labels = ["All"] + tags
            subtabs = st.tabs(subtab_labels)

            for label, subtab in zip(subtab_labels, subtabs):
                with subtab:
                    if label == "All":
                        visible_records = body_records
                    else:
                        visible_records = [
                            record
                            for record in body_records
                            if record["job_tag"] == label
                        ]

                    _render_cards(visible_records)
        else:
            _render_cards(body_records)

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
        .recent-card {
            border-color: #f59e0b;
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.25);
            background: linear-gradient(135deg, #fff7ed 0%, #ffffff 55%);
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
            .recent-card {
                border-color: #fbbf24;
                box-shadow: 0 0 0 2px rgba(251, 191, 36, 0.28);
                background: linear-gradient(135deg, #1f2937 0%, #0f172a 60%);
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


st.title("Sarkari Naukri")

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
        return value.strftime("%B %d, %Y")

    if isinstance(value, str):
        try:
            clean_value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(clean_value).strftime("%B %d, %Y")
        except ValueError:
            return value

    return str(value)


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            clean_value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(clean_value)
        except ValueError:
            return None

    return None


def _is_recent(record):
    created_at = _parse_date(record.get("created_date"))
    if not created_at:
        return False

    created_at = created_at.replace(tzinfo=None)
    return (datetime.now() - created_at).total_seconds() <= 24 * 60 * 60


def _parse_date_for_sort(value):
    return _parse_date(value)


def _get_priority_sort_date(record):
    for key in ("posted_date", "deadline", "created_date"):
        parsed = _parse_date_for_sort(record.get(key))
        if parsed:
            return parsed
    return datetime.min


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
                highlight_class = "tab-card recent-card" if record.get("is_recent") else "tab-card"
                st.markdown(
                    f"""
                    <div class="{highlight_class}">
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
            "_sort_date": _get_priority_sort_date(record),
            "is_recent": _is_recent(record),
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

                    visible_records.sort(
                        key=lambda entry: entry.get("_sort_date", datetime.min),
                        reverse=True,
                    )
                    _render_cards(visible_records)
        else:
            body_records.sort(
                key=lambda entry: entry.get("_sort_date", datetime.min),
                reverse=True,
            )
            _render_cards(body_records)

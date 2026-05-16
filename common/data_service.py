import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


def _get_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")

    return create_client(url, key)


def is_url_saved(url):
    client = _get_client()

    response = (
        client.table("job_openings")
        .select("id")
        .eq("url", url)
        .limit(1)
        .execute()
    )

    return bool(response.data)


def save_job_opening(government_body, job_tag,job_title, posted_date, deadline, url):
    
    try:
            client = _get_client()

            payload = {
                "government_body": government_body,
                "job_tag": job_tag,
                "title": job_title,
                "posted_date": posted_date if posted_date else None,
                "deadline": deadline if deadline else None,
                "url": url,
                "created_date": datetime.now(timezone.utc).isoformat(),
            }

            response = client.table("job_openings").insert(payload).execute()

            return response.data
    except Exception as ex:
        print(f"Error saving job opening: {ex}")
        raise


def fetch_job_openings():
    client = _get_client()

    try:
        response = (
            client.table("job_openings")
            .select("government_body, job_tag, title, posted_date, deadline, url")
            .order("posted_date", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as ex:
        print(f"Error fetching job openings: {ex}")
        raise
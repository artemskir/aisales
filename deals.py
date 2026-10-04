import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("AMOCRM_BASE_URL")
TOKEN = os.getenv("AMOCRM_ACCESS_TOKEN")

headers = {"Authorization": f"Bearer {TOKEN}"}


def get_problem_leads():
    now = int(time.time())
    page = 1

    while True:
        response = requests.get(
            f"{BASE_URL}/api/v4/leads",
            headers=headers,
            params={"limit": 250, "page": page},
            timeout=10,
        )

        if response.status_code == 204:
            break

        response.raise_for_status()
        leads = response.json().get("_embedded", {}).get("leads", [])

        for lead in leads:
            task_at = lead.get("closest_task_at")

            if task_at is None or task_at < now:
                yield {
                    "id": lead["id"],
                    "name": lead["name"],
                    "responsible_user_id": lead["responsible_user_id"],
                    "reason": "no_task" if task_at is None else "overdue_task",
                }

        if len(leads) < 250:
            break

        page += 1


print(list(get_problem_leads()))
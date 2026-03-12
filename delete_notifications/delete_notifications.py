#!/usr/bin/env python3
"""
Delete bogus/extraneous/orphaned notifications from ModelOp Center

Key points:
-----------
* We assume you already ran preflight.py, and your directory contains a preflight_orphanednotifications.csv 
  that contains all notifications you would like to delete.


WARNING:
--------
This script performs DELETE operations in your environment. Test in a non-production clone first.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests

# ==========================================
# 1. CONFIGURATION & AUTHENTICATION
# ==========================================

# Retrieve configuration from environment or prompt user
MOC_BASE_URL = "your-base-url".strip()
MOC_ACCESS_TOKEN = "your-access-token".strip()


# --------------------------------
# CSV LOCATIONS
# --------------------------------

# Deleted Notifications
DELETED_NOTIFICATIONS_CSV = "deleted_notifications.csv"
# Orphaned Notifications
ORPHANED_NOTIFICATIONS_CSV = "preflight_orphanednotifications.csv"

# --------------------------------
# HTTP / REQUESTS CONFIG
# --------------------------------

VERIFY_SSL = True      # TODO: set False ONLY if you must bypass TLS verification (not recommended)
HTTP_TIMEOUT = 30      # seconds per request
PAGE_SIZE = 200        # page size for list/search endpoints


# --------------------------------
# LOGGING CONFIGURATION
# --------------------------------

logging.basicConfig(
    level=logging.INFO,   # Use logging.DEBUG for verbose output
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("delete_notifications")


# ==========================================
# 1.5 AUTHENTICATION & ENV FILE MANAGEMENT
# ==========================================

def normalize_access_token(raw_token: str) -> str:
    """
    Normalize an access token that may be provided either as:
      - a plain bearer token string, or
      - a JSON string containing {"access_token": "<token>"}.

    This mirrors environments where tooling may return the full OAuth2
    token payload JSON instead of just the access_token string.

    Parameters
    ----------
    raw_token : str
        Raw token string, possibly containing JSON.

    Returns
    -------
    str
        The actual bearer token value.

    Raises
    ------
    ValueError
        If the token is empty or JSON cannot be parsed as expected.
    """
    raw_token = (raw_token or "").strip()
    if not raw_token:
        raise ValueError("Access token is empty. Please configure MOC_ACCESS_TOKEN.")

    if raw_token.startswith("{") and "access_token" in raw_token:
        try:
            parsed = json.loads(raw_token)
            token = parsed.get("access_token")
            if not token:
                raise ValueError("JSON token string does not contain 'access_token' key.")
            return token
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse MOC_ACCESS_TOKEN as JSON: {exc}") from exc

    return raw_token


def create_authenticated_session(base_url: str, access_token: str) -> requests.Session:
    """
    Create a `requests.Session` pre-configured with Authorization headers
    for the given ModelOp Center instance.

    Parameters
    ----------
    base_url : str
        Base URL for the MOC instance (no trailing slash).
    access_token : str
        OAuth2 token (plain string or JSON containing 'access_token').

    Returns
    -------
    requests.Session
        Configured HTTP session.
    """
    token = normalize_access_token(access_token)
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )
    session.verify = VERIFY_SSL
    logger.info("Authenticated HTTP session created for base URL: %s", base_url)
    return session

# ==========================================
# 1. DELETE NOTIFICATION RECORDS
# ==========================================

def delete_notification(
    base_url: str,
    session: requests.Session,
    notification_id: str,
) -> None:
    """
    Delete a notification from ModelOp Center

    Parameters
    ----------
    base_url : str
        ModelOp Center base URL.
    session : requests.Session
        Authenticated session.
    notification_id : str
        Notification UUID.
    
    Returns
    -------
    Dict
        JSON body of the deleted notification record.
    """
    url = f"{base_url}/model-manage/api/notifications/{notification_id}"

    logger.debug(
        "Deleting notification %s...",
        notification_id,
    )
    resp = session.delete(url, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()

    return


def delete_notifications(
    base_url: str,
    session: requests.Session,
    source_csv_path: str,
    target_csv_path: str,
) -> pd.DataFrame:
    """
    For each notification row in `source_csv_path`, delete the notification

    Steps:
      1. Read preflight_orphanednotifications.csv.
      2. For each row:
           a) DELETE the notification
      3. Write the id of each deleted notification to deleted_notifications.csv

    Parameters
    ----------
    base_url : str
        ModelOp Center base URL.
    session : requests.Session
        Authenticated session.
    source_csv_path : str
        Input CSV file path.
    target_csv_path : str
        Output CSV file path.

    Returns
    -------
    pd.DataFrame
        DataFrame of deleted notifications results.
    """
    logger.info("=== Step 1 — Deleting Notification Records ===")

    try:
        df_source = pd.read_csv(source_csv_path)
    except FileNotFoundError as exc:
        logger.error(
            "Source CSV %s not found.",
            source_csv_path,
        )
        raise exc

    if df_source.empty:
        logger.warning("Source CSV %s is empty. No notifications will be deleted.", source_csv_path)
        return df_source

    rows_out = []

    for _, row in df_source.iterrows():
        notification_id = str(row["id"])

        logger.info(
            "Deleting notification_id=%s",
            notification_id,
        )

        # Delete notification
        delete_notification(
            base_url=base_url,
            session=session,
            notification_id=notification_id,
        )

        rows_out.append(notification_id)

    df_out = pd.DataFrame(rows_out)
    df_out.to_csv(target_csv_path, index=False)
    logger.info(
        "Notification Delete complete. %d records processed. Results CSV: %s",
        len(df_out),
        target_csv_path,
    )
    return df_out


# ==========================================
# 6. MAIN ORCHESTRATION
# ==========================================

def main() -> None:
    """
    Orchestrate the full notification deletion process in a single 3.4 environment.

    Summary of steps:
    -----------------
    1) Authenticate to current 3.4 environment (MOC_BASE_URL + MOC_ACCESS_TOKEN).

    2) Read in preflight_orphanednotifications.csv file

    3) Delete orphaned notifications
       Write: deleted_notifications.csv

    After completion:
    -----------------
    * All orphaned notifications will be deleted
    """
    # Step 0: Handle authentication
    global MOC_ACCESS_TOKEN  # Allow modification of the global variable
    
    # Step 1: Authenticate to MOC
    logger.info("Authenticating to ModelOp Center 3.4 environment: %s", MOC_BASE_URL)
    session = create_authenticated_session(MOC_BASE_URL, MOC_ACCESS_TOKEN)

    # Step 2: Delete notification records
    delete_notifications(
        base_url=MOC_BASE_URL,
        session=session,
        source_csv_path=ORPHANED_NOTIFICATIONS_CSV,
        target_csv_path=DELETED_NOTIFICATIONS_CSV,
    )

    logger.info("AuditRecord backfill script completed successfully.")


if __name__ == "__main__":
    main()
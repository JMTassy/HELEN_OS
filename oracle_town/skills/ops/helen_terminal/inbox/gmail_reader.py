"""
HELEN Terminal — Gmail read-only connector.
Reads inbox and drafts replies. NEVER sends without operator confirm.
Requires: google-auth-oauthlib google-api-python-client
OAuth credentials: ~/.helen_gmail_credentials.json (client secret)
Token cache: ~/.helen_gmail_token.json
"""
from __future__ import annotations

import base64
import json
import os
from email.mime.text import MIMEText
from pathlib import Path

from ..receipts.action_receipts import build_receipt

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
CREDENTIALS_PATH = Path.home() / ".helen_gmail_credentials.json"
TOKEN_PATH = Path.home() / ".helen_gmail_token.json"


def _get_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "Gmail connector requires: pip install google-auth-oauthlib google-api-python-client"
        )

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"Gmail credentials not found at {CREDENTIALS_PATH}. "
                    "Download OAuth client secret from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _decode_body(payload: dict) -> str:
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data", "")
                return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    data = payload.get("body", {}).get("data", "")
    if data:
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    return ""


def read_inbox(max_results: int = 10, query: str = "is:unread") -> dict:
    svc = _get_service()
    result = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = result.get("messages", [])

    summaries = []
    for msg in messages:
        m = svc.users().messages().get(userId="me", id=msg["id"], format="metadata",
                                        metadataHeaders=["Subject", "From", "Date"]).execute()
        headers = {h["name"]: h["value"] for h in m["payload"].get("headers", [])}
        summaries.append({
            "id": msg["id"],
            "thread_id": m.get("threadId"),
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": m.get("snippet", "")[:150],
        })

    artifact = {
        "type": "INBOX_READ",
        "query": query,
        "count": len(summaries),
        "messages": summaries,
        "content_preview": f"{len(summaries)} messages matched '{query}'",
    }
    receipt = build_receipt("READ_INBOX", {"query": query, "max_results": max_results}, artifact)
    return {"artifact": artifact, "receipt_id": receipt["receipt_id"]}


def read_thread(thread_id: str) -> dict:
    svc = _get_service()
    thread = svc.users().threads().get(userId="me", id=thread_id, format="full").execute()

    messages = []
    for msg in thread.get("messages", []):
        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        body = _decode_body(msg["payload"])
        messages.append({
            "id": msg["id"],
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "date": headers.get("Date", ""),
            "subject": headers.get("Subject", ""),
            "body": body[:2000],
        })

    artifact = {
        "type": "THREAD_READ",
        "thread_id": thread_id,
        "message_count": len(messages),
        "messages": messages,
        "content_preview": f"Thread {thread_id}: {len(messages)} messages",
    }
    receipt = build_receipt("READ_THREAD", {"thread_id": thread_id}, artifact)
    return {"artifact": artifact, "receipt_id": receipt["receipt_id"]}


def draft_reply(thread_id: str, to: str, subject: str, body: str) -> dict:
    """Creates a Gmail draft. NEVER sends. Operator must review and send manually."""
    svc = _get_service()

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = svc.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw, "threadId": thread_id}}
    ).execute()

    artifact = {
        "type": "EMAIL_DRAFT_CREATED",
        "draft_id": draft["id"],
        "thread_id": thread_id,
        "to": to,
        "subject": subject,
        "body_preview": body[:200],
        "content_preview": f"Draft created for {to}: {subject}",
        "send_status": "DRAFT_ONLY_NOT_SENT",
    }
    receipt = build_receipt(
        "CREATE_EMAIL_DRAFT",
        {"thread_id": thread_id, "to": to, "subject": subject},
        artifact,
    )
    return {
        "draft_id": draft["id"],
        "status": "DRAFT_ONLY_NOT_SENT",
        "receipt_id": receipt["receipt_id"],
        "note": "Draft saved to Gmail. Open Gmail to review and send manually.",
    }

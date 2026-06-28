from __future__ import annotations

import argparse
from pathlib import Path

from keiba_ai_agent.mail.gmail_sender import GmailSender


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send a Markdown report by email")
    parser.add_argument("report", help="Path to the Markdown report")
    parser.add_argument("recipient", help="Recipient email address")
    parser.add_argument("--subject", default="競馬予想レポート")
    parser.add_argument("--env", default=".env")
    args = parser.parse_args(argv)

    sender = GmailSender(env_path=args.env)
    sender.send_report(report_path=args.report, recipient=args.recipient, subject=args.subject)
    print(f"Sent report {args.report} to {args.recipient}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

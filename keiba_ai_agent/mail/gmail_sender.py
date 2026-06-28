from __future__ import annotations

import os
from email.message import EmailMessage
from pathlib import Path
from smtplib import SMTP
from typing import Any


class GmailSender:
    def __init__(self, env_path: str | Path | None = None):
        self.env_path = Path(env_path or ".env")
        self.smtp_host = self._read_env("SMTP_HOST")
        self.smtp_port = int(self._read_env("SMTP_PORT", default="587"))
        self.smtp_user = self._read_env("SMTP_USER")
        self.smtp_password = self._read_env("SMTP_PASSWORD")

    def _read_env(self, key: str, default: str | None = None) -> str:
        if self.env_path.exists():
            for line in self.env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
        return os.getenv(key, default or "")

    def _create_smtp_client(self) -> SMTP:
        return SMTP(self.smtp_host, self.smtp_port)

    def _markdown_to_html(self, markdown_text: str) -> str:
        lines = markdown_text.splitlines()
        html_lines: list[str] = ["<html><body>"]
        for line in lines:
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("- "):
                html_lines.append(f"<li>{line[2:]}</li>")
            else:
                html_lines.append(f"<p>{line}</p>")
        html_lines.append("</body></html>")
        return "\n".join(html_lines)

    def send_report(self, report_path: str | Path, recipient: str, subject: str = "競馬予想レポート") -> None:
        report_path = Path(report_path)
        markdown_text = report_path.read_text(encoding="utf-8")
        html_body = self._markdown_to_html(markdown_text)

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.smtp_user
        message["To"] = recipient
        message.set_content(markdown_text)
        message.add_alternative(html_body, subtype="html")

        smtp_client = self._create_smtp_client()
        try:
            smtp_client.starttls()
            smtp_client.login(self.smtp_user, self.smtp_password)
            smtp_client.sendmail(self.smtp_user, [recipient], message.as_string())
        finally:
            smtp_client.quit()

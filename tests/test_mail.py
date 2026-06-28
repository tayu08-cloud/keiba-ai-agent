from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from keiba_ai_agent.mail.gmail_sender import GmailSender
from keiba_ai_agent.mail.send_report import main as send_report_main


def test_gmail_sender_reads_env_and_sends_via_smtp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "SMTP_HOST=smtp.example.com\n"
        "SMTP_PORT=587\n"
        "SMTP_USER=test@example.com\n"
        "SMTP_PASSWORD=secret\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    smtp_client = MagicMock()
    smtp_client.__enter__.return_value = smtp_client
    smtp_client.__exit__.return_value = False
    smtp_client.send_message.return_value = None

    sender = GmailSender(env_path=env_path)
    monkeypatch.setattr("keiba_ai_agent.mail.gmail_sender.SMTP", Mock(return_value=smtp_client))

    report_path = tmp_path / "report.md"
    report_path.write_text("# テストレポート\n\n内容", encoding="utf-8")

    sender.send_report(report_path=report_path, recipient="to@example.com", subject="件名")

    smtp_client.send_message.assert_called_once()
    assert smtp_client.login.call_count == 1
    assert smtp_client.ehlo.call_count == 2


def test_send_report_cli_uses_report_path_and_recipient(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    report_path = tmp_path / "report.md"
    report_path.write_text("# テストレポート", encoding="utf-8")
    env_path = tmp_path / ".env"
    env_path.write_text(
        "SMTP_HOST=smtp.example.com\n"
        "SMTP_PORT=587\n"
        "SMTP_USER=test@example.com\n"
        "SMTP_PASSWORD=secret\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    sender = Mock()
    monkeypatch.setattr("keiba_ai_agent.mail.send_report.GmailSender", lambda env_path=None: sender)

    exit_code = send_report_main([str(report_path), "to@example.com", "--subject", "件名"])

    assert exit_code == 0
    sender.send_report.assert_called_once()

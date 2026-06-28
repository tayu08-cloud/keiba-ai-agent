# Keiba AI Agent

競馬予想AIエージェント

開発者: Takumi Yamazaki

## Python環境の使い分け

このプロジェクトでは、用途ごとに2つの Python 環境を使います。

- `.venv32`
  - JV-Link / JRA-VAN 取得専用
  - 32bit Python
  - `win32com` などの収集系依存を使う

- `.venv`
  - AI / dataset / pandas / pyarrow / OpenAI / Gmail 用
  - 64bit Python
  - データセット生成や学習・推論・外部 API 連携に使う

## 代表的な実行コマンド

- JV-Link 収集
  - `./.venv32/Scripts/python.exe -m keiba_ai_agent.collector.jvlink_read_test RACE 20240101000000 1 save 5`

- Dataset 生成
  - `c:/keiba-ai-agent/.venv/Scripts/python.exe scripts/build_dataset.py keiba.db dataset`

## pytest

- JV-Link / 収集系
  - `./.venv32/Scripts/python.exe -m pytest -q`

- AI / dataset 系
  - `c:/keiba-ai-agent/.venv/Scripts/python.exe -m pytest -q`

詳細は [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) を参照してください。

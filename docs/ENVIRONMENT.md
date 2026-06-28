# Environment Guide

このプロジェクトでは、Python 環境を用途ごとに分けて管理します。

## 1. .venv32

用途:
- JV-Link / JRA-VAN 取得処理
- 32bit Python
- Windows での COM 連携向け

特徴:
- `win32com` などの JV-Link 系依存を使う
- pandas / pyarrow / ML 系は使わない
- 収集系スクリプトの実行に使用する

## 2. .venv

用途:
- AI / dataset / pandas / pyarrow / OpenAI / Gmail
- 64bit Python

特徴:
- データセット生成
- 解析・学習・推論や外部 API 連携向け
- `pandas`, `pyarrow`, `openai` などを利用する

## 3. 使い分け

- JV-Link 系: `.venv32`
- Dataset / AI 系: `.venv`

## 4. pytest コマンド

- JV-Link / 収集系: `.venv32\Scripts\python.exe -m pytest -q`
- AI / dataset 系: `c:/keiba-ai-agent/.venv/Scripts/python.exe -m pytest -q`

## 5. 依存関係

- JV-Link 用: `requirements-jvlink.txt`
- AI / dataset 用: `requirements-ai.txt`

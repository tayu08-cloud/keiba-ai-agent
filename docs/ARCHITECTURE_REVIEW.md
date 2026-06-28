# Architecture Review

## 1. Executive Summary

このプロジェクトは「JV-Linkから競馬データを取得し、SQLiteに保存し、予測・配信へつなぐ」方向性が明確で、初期の実装基盤としては良好です。特に、以下の点は良い土台です。

- 収集・解析・保存・CLIの責務が比較的分かれている
- パーサーとリポジトリ層の分離が始まっている
- `pytest` による自動テストが導入されている
- 将来のモデル追加・Web API化に向けた拡張余地がある

一方で、販売品質を意識した本番向けシステムとしては、まだ以下の課題があります。

- 設計の一貫性が弱く、責務境界が曖昧な箇所がある
- 依存関係の管理・設定管理・運用観点が不足している
- データ整合性・監査性・再実行性・障害時の回復性が弱い
- モデル学習・推論・API・バッチ処理が同じレイヤーに混ざりやすい構造

結論として、現状は「プロトタイプ／実験基盤」としては十分に進んでいますが、販売品質の競馬AIシステムとしては、設計の基盤強化と運用面の整備が必要です。

---

## 2. Review by Area

### 2.1 Directory Structure

#### Current State

- `keiba_ai_agent/` 配下に主要責務が分割されている
  - `collector/`: データ収集
  - `parser/`: 解析
  - `database/`: SQLite周り
  - `predictor/`: 予測ロジック
  - `mail/`: 配信
  - `models/`: モデル関連
  - `utils/`: 汎用ユーティリティ

#### Assessment

構成の方向性は良いです。機能の責務分離は比較的明確で、今後の拡張に対応しやすいです。

#### Issues

- `collector/` や `parser/` の実装がまだ最小構成に寄っており、サービス層が不足している
- `predictor/`、`models/`、`mail/` がまだ抽象化不足で、将来の責務が散りやすい
- `scripts/` と `tests/` が独立しているが、実行可能なエントリーポイントの規約がまだ弱い

#### Recommendation

- `service/` 層を追加し、CLI・API・バッチから共通利用するビジネスロジックを集約する
- `pipelines/` や `jobs/` を追加し、収集・学習・推論・レポート生成を明確に分離する

---

### 2.2 Naming Conventions

#### Current State

- `JVLinkClient`, `RaceRepository`, `HorseRepository`, `RawRecordRepository` など、概念としては明快
- `parse_jg_record`, `run_read_loop`, `save_to_db` のように機能名は比較的読みやすい

#### Assessment

命名は基本的にわかりやすく、Pythonらしい表記も概ね守られています。

#### Issues

- `jvlink_read_test.py` のように「テスト」ではあるが実行用スクリプトとしても機能しており、役割が曖昧
- `save_to_db` のような boolean 引数は、将来 `save_mode` や `persist_strategy` のような明示的な構造に置き換えた方が保守しやすい
- `raw_records` などのテーブル名・CLI名・Python変数名の粒度が一貫していない箇所がある

#### Recommendation

- スクリプト名と実際の役割を分離する
  - 例: `jvlink_read_test.py` → `jvlink_reader.py` または `collect_raw_data.py`
- CLI引数や設定値は `argparse` で統一する
- boolean 引数は避け、Enum や設定オブジェクトに置き換える

---

### 2.3 Python Design

#### Current State

- dataclass を使用した `Horse` モデルが導入されており、良い方向です
- `KeibaDatabase` が接続を管理する構造になっており、シンプルです
- モジュール分割が比較的自然です

#### Assessment

Pythonとしては読みやすく、初心者にも理解しやすい構造です。dataclass の導入も適切です。

#### Issues

- `collector` 側で `win32com` に強く依存しており、Linux/macOS での実行性が低い
- 例外処理が `main` 側に寄っており、再利用性が低い
- 依存注入や設定オブジェクトの導入がまだ弱い
- 型注釈はあるものの、ドメインモデルや設定モデルの整理がまだ浅い

#### Recommendation

- `Collector`, `Parser`, `Repository`, `Service` 層を明確に切る
- `win32com` を抽象化するため、`JVLinkAdapter` や `DataSource` インターフェースを導入する
- `settings.py` や `config.py` を追加し、DBパス・JV-Link設定・保存戦略などを一元管理する

---

### 2.4 Repository Design

#### Current State

- `RaceRepository`, `HorseRepository`, `EntryRepository`, `RawRecordRepository` があり、責務は概ね整理されています
- `BaseRepository` に共通クエリ処理を寄せており、理解しやすいです

#### Assessment

リポジトリの導入は良い判断です。将来のデータアクセス変更に備えやすいです。

#### Issues

- リポジトリが `dict` ベースでデータを受け渡ししているため、型の安全性が弱い
- `HorseRepository.upsert_horse_from_model()` が `Horse` に依存しており、ドメイン層と永続化層の結びつきがやや強い
- `save()` と `upsert_horse_from_model()` が同一責務に見えて、インターフェースが分散している
- SQLがリポジトリ内部に埋め込まれており、クエリの管理・最適化・テストがやや難しい

#### Recommendation

- ドメインモデルをそのまま引数に取るのではなく、`HorseCreate` や `HorseRecord` のような永続化用 DTO を導入する
- `Repository` の公開メソッドを統一し、`save()` / `upsert()` / `find_by_*()` の粒度を揃える
- 将来的に SQLAlchemy や Django ORM への移行を見据え、SQL依存を少しずつ薄くする

---

### 2.5 Parser Design

#### Current State

- `parse_jg_record()` が `Horse` dataclass を返す構造になり、良い方向です
- `extra` フィールドを通じて将来の拡張余地が作られています

#### Assessment

パーサーの責務が比較的明確で、拡張性もあります。今後のフィールド追加に対応しやすいです。

#### Issues

- 現在は最低限の文字列抽出に留まり、実際の JV-Link 固定長仕様との対応がまだ弱い
- 解析ルールが「候補文字列抽出」に偏っており、構造化データとしてはまだ弱い
- `record_type` や `raw` の保持は良いですが、パース失敗時・不十分なパース時の扱いが弱い

#### Recommendation

- 解析ルールを明示的なフィールド定義に分ける
  - 例: `FieldSpec`, `ParserRule`, `ParserContext`
- 不足したフィールドの扱いを `None` / `Unknown` / `Invalid` で明示する
- `parse_jg_record()` の戻り値を `ParseResult` に包み、成功・失敗・警告を管理する

---

### 2.6 SQLite Design

#### Current State

- `raw_records`, `horses`, `races`, `entries` の基本テーブルが整備されている
- `schema.sql` により初期化ができる構造になっている

#### Assessment

初期構造としては妥当です。SQLiteでの起動・開発がしやすいです。

#### Issues

- `horse_id` が `NULL` を許容しており、データ整合性上の課題がある
- `horse_name` の一意制約がなく、重複登録の防止がアプリ側に依存している
- 外部キー制約が有効化されていない可能性があり、整合性保証の強さが弱い
- `created_at` の管理方法が統一されていない
- 今後のテーブル増加に伴い、マイグレーション戦略が必要

#### Recommendation

- `horses.horse_name` にユニーク制約を追加する
- `raw_records` への保存ルールを明文化し、`source`, `parsed_at`, `status` のようなメタデータを追加する
- マイグレーション手順を設ける（例: `alembic` ではなく、SQL diff 管理）
- 本番運用では `PRAGMA foreign_keys = ON` を前提にする

---

### 2.7 Test Structure

#### Current State

- `pytest` が導入されており、主要な層に対するテストが存在する
- リポジトリ・CLI・パーサーに対するテストがある

#### Assessment

テストの基盤は良好です。これは今後の開発効率に大きく寄与します。

#### Issues

- テストの粒度が一部で混ざっている
  - 例: CLIスクリプト実行テストと DB リポジトリテストが同じファイルに混在
- モックが多用されると、実データ経路の検証が弱くなる
- パーサーの境界条件・異常系テストがまだ少ない
- E2E的なテストが不足している

#### Recommendation

- `tests/unit/` と `tests/integration/` に分離する
- CLIテストは `subprocess` ベースで維持しつつ、DB系は temporary DB を使う
- 重要な入力ケース（空文字、異常形式、長さ不足、重複）を網羅する

---

### 2.8 Readiness for LightGBM / XGBoost

#### Assessment

現状の構造は、モデル追加の前段階として十分に整いつつあります。特に、以下の点は良いです。

- データを SQLite で保存できるため、特徴量生成の入力元として扱いやすい
- `predictor/` と `models/` の分離が進んでいる

#### Issues

- モデル学習・推論・評価のための共通インターフェースがまだない
- 特徴量データの整形ルールが抽象化されていない
- 学習用データセットと推論用データセットの境界が曖昧
- 予測モデルの保存形式・バージョン管理手順が未定

#### Recommendation

- `features/` と `training/` を追加し、特徴量生成と学習パイプラインを分離する
- `BaseModel` / `Predictor` インターフェースを導入し、LightGBM/XGBoost を同じ契約で差し込めるようにする
- モデルのメタデータ（学習日、特徴量一覧、評価指標）を明示的に保存する

---

### 2.9 Readiness for Web API Deployment

#### Assessment

現状の構造は、API化のための基礎はありますが、まだ完全な API 先行設計ではありません。

#### Issues

- CLI中心の実装で、HTTP層が存在しない
- データアクセスとビジネスロジックが結びつきやすい
- 設定管理・認証・ログ・監視・運用タスクの枠組みが不足
- 予測・データ取得・レポート生成の実行単位が曖昧

#### Recommendation

- `service/` 層を導入し、CLI・API・バッチから共通利用する
- API では `FastAPI` を使う前提で、`schemas/` と `routers/` を用意する
- `settings.py` による環境変数管理、`logging` 設定、`health check` エンドポイントを用意する

---

## 3. Priority Recommendations

### P0: Highest Priority

1. Introduce a service layer
   - CLI、API、バッチから共通で呼び出せるサービス層を追加する
   - 現在の `collector` / `parser` / `repository` 連携を整理する

2. Standardize configuration management
   - DBパス、JV-Link設定、保存オプション、モデル設定を一元管理する
   - `.env` や設定クラスで統一する

3. Strengthen data model integrity
   - `horses.horse_name` の一意制約、外部キー制約、`created_at` の標準化を行う
   - データの不整合を防ぐ

### P1: High Priority

4. Separate batch/CLI entry points from library logic
   - `scripts/` は実行用に寄せ、実処理は `keiba_ai_agent/` 配下のモジュールに集約する

5. Introduce explicit domain DTOs
   - `dict` ベースの受け渡しを減らし、型の安全性を上げる

6. Add migration and schema evolution strategy
   - SQLite のテーブル追加・変更を管理できる仕組みを作る

### P2: Medium Priority

7. Add a model interface abstraction
   - LightGBM/XGBoost 追加時に同一インターフェースで差し込める構造にする

8. Add API-oriented architecture skeleton
   - `FastAPI` 追加前に `routers/`, `schemas/`, `dependencies/` を少しずつ整える

9. Improve observability
   - ログ、メトリクス、処理件数、失敗率、再試行回数を記録する仕組みを追加する

---

## 4. Overall Assessment

### Current State

- 良い基礎ができている
- 実験・検証フェーズとしては十分に進んでいる
- 競馬AIシステムとしての骨格は見えている

### Gap to Sales-Quality Product

- 運用・監視・設定管理・データ整合性・API拡張性・モデル管理が不足している
- 実装の品質はかなり良いが、製品品質としては「初期プロトタイプ」に近い

### Suggested Direction

今後は「機能追加」よりも「構造の安定化」を優先するのが重要です。特に以下の3点が、販売品質に直結します。

- 安定したデータ基盤
- 明確なサービス層と設定管理
- テスト・監視・再実行可能性

---

## 5. Bottom Line

現状の実装は、競馬AIプロジェクトの第一段階として十分に良いです。特にデータ収集・パース・保存・CLI確認の流れが通っており、今後の拡張に向けた土台があります。

ただし、販売品質を目指すなら、次の順で改善するのが妥当です。

1. サービス層の導入
2. 設定・データ整合性の強化
3. モデル・API化への抽象化
4. 運用・監視・テストの拡充

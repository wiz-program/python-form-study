# python-form-study

## 概要

[react-form-study](https://github.com/wiz-program/react-form-study) のバックエンド API です。

React Hook Form + Zod で実装したフロントエンドフォームから送信された応募データを受け取り、Neon（PostgreSQL）に保存します。

| 項目 | URL |
|---|---|
| フロントエンド（React） | https://github.com/wiz-program/react-form-study |
| バックエンド（このリポジトリ） | https://github.com/wiz-program/python-form-study |
| デプロイ先（Render） | https://python-form-study.onrender.com |
| フロントエンド（GitHub Pages） | https://wiz-program.github.io/react-form-study/ |

フロントエンドのフォーム UI・クライアントバリデーション・確認画面・応募完了画面の実装は [react-form-study](https://github.com/wiz-program/react-form-study) を参照してください。  
このリポジトリは Render にデプロイされ、GitHub Pages 上のフロントエンドから API リクエストを受け付けます。

実務でよくある「入力 → 確認 → API 送信 → 応募完了」フローのうち、**API 受付〜データベース保存**を担う部分の学習コードです。

フロントエンドの Zod スキーマと対応するバリデーションを Pydantic で実装し、同じ入力ルールをサーバー側でも担保しています。

---

## 構成ファイル

```
python-form/
├── main.py          # FastAPI アプリ・API エンドポイント・DB 保存処理
├── pyproject.toml   # 依存関係定義
├── uv.lock          # ロックファイル
└── .env             # 環境変数（ローカル開発用・Git 管理外）
```

### main.py の役割

- FastAPI アプリの定義と CORS 設定
- Pydantic によるリクエストバリデーション（`RegisterQuestionnaireRequest`）
- `POST /api/v1/register-questionnaire` エンドポイントの実装
- asyncpg による Neon（PostgreSQL）へのデータ保存
- 成功時に `status` と `message` を返却（フロントの応募完了画面で表示）

---

## API 連携

フロントエンドの `ConfirmForm.tsx` から、以下のエンドポイントへ `POST` リクエストが送信されます。

```
https://python-form-study.onrender.com/api/v1/register-questionnaire
```

ローカル開発時は、フロントエンド側のリクエスト先を以下に変更してください。

```
http://localhost:8000/api/v1/register-questionnaire
```

### フロントエンド（別リポジトリ）

| レイヤー | リポジトリ | 役割 |
|---|---|---|
| フロントエンド | [react-form-study](https://github.com/wiz-program/react-form-study) | フォーム UI・クライアントバリデーション・確認画面・API 送信・応募完了画面 |
| バックエンド | このリポジトリ | API 受付・サーバーバリデーション・DB 保存 |

フロントエンドの画面構成・設計方針などの詳細は [react-form-study の README](https://github.com/wiz-program/react-form-study) を参照してください。

### バックエンド（このリポジトリ）

#### `POST /api/v1/register-questionnaire`

応募フォームのデータを受け取り、`questionnaires` テーブルに保存します。

**リクエストボディ**

```json
{
  "name": "山田太郎",
  "email": "taro@example.com",
  "password": "password123",
  "gender": "男性",
  "prize": "A"
}
```

| フィールド | 型 | バリデーション |
|---|---|---|
| `name` | string | 3 文字以上 |
| `email` | string | メール形式（`EmailStr`） |
| `password` | string | 8 文字以上 |
| `gender` | string | 1 文字以上 |
| `prize` | `"A"` \| `"B"` \| `"C"` | リテラル型 |

> フロントエンドの Zod スキーマ（`UseFormContext.tsx`）と同じルールです。

**レスポンス（成功時）**

```json
{
  "status": "success",
  "message": "山田太郎さんの応募を受付、データベースに保存しました。"
}
```

フロントエンドの応募完了画面（`CompleteForm.tsx`）では、この `message` を表示します。

**Swagger UI**

ローカル起動後、以下で API ドキュメントを確認できます。

- http://localhost:8000/docs

---

## データベース

Neon 上に以下のテーブルを作成してください。

```sql
CREATE TABLE questionnaires (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL,
    password   VARCHAR(255) NOT NULL,
    gender     VARCHAR(50)  NOT NULL,
    prize      CHAR(1)      NOT NULL CHECK (prize IN ('A', 'B', 'C')),
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
```

---

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/wiz-program/python-form-study.git
cd python-form-study
```

### 2. 依存関係のインストール

```bash
uv sync
```

### 3. 環境変数の設定

プロジェクトルートに `.env` を作成します。

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>?sslmode=require
```

> Neon のダッシュボードから接続文字列をコピーして設定してください。

### 4. 開発サーバーの起動

```bash
uv run fastapi dev main.py
```

起動後:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

---

## Render へのデプロイ

### 事前準備

- GitHub にこのリポジトリをプッシュ済みであること
- Neon の `DATABASE_URL` を取得済みであること

### Web Service の設定

| 項目 | 値 |
|---|---|
| **Environment** | Python 3 |
| **Build Command** | `pip install uv && uv sync` |
| **Start Command** | `uv run fastapi run main.py --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/docs`（任意） |

### 環境変数

Render のダッシュボードで以下を設定します。

| Key | Value |
|---|---|
| `DATABASE_URL` | Neon の接続文字列 |

### デプロイ後

- API ベース URL: https://python-form-study.onrender.com
- エンドポイント: https://python-form-study.onrender.com/api/v1/register-questionnaire

CORS は開発用に `allow_origins=["*"]` を設定しています。本番ではフロントエンドのドメイン（`https://wiz-program.github.io`）に絞ることを推奨します。

---

## 設計方針

- バリデーションは Pydantic モデルに集約し、フロントエンドの Zod スキーマと同じルールを適用する
- SQL インジェクション対策として asyncpg のプレースホルダー（`$1`, `$2`...）を使用する
- DB 接続は `try` / `finally` で必ずクローズする
- 成功レスポンスの `message` をフロントの応募完了画面でそのまま表示できる形式にする
- 学習段階のため、リクエストモデルとルートハンドラは `main.py` に集約したシンプルな構成とする

---

## 使用技術

- Python 3.12+
- FastAPI
- Pydantic（`EmailStr` によるメール形式チェック）
- asyncpg（PostgreSQL 非同期ドライバ）
- uv（パッケージ管理）
- Neon（PostgreSQL）
- Render（デプロイ）

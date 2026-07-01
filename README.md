# python-form

[react-form-study](https://github.com/wiz-program/react-form-study) のバックエンド API です。

React Hook Form + Zod で実装したフロントエンドフォームから送信された応募データを受け取り、Neon（PostgreSQL）に保存します。

---

## 概要

実務でよくある「入力 → 確認 → API 送信」フローのうち、**API 送信〜データベース保存**を担う部分の学習コードです。

フロントエンドの Zod スキーマと対応するバリデーションを Pydantic で実装し、同じ入力ルールをサーバー側でも担保しています。

| レイヤー | リポジトリ | 役割 |
|---|---|---|
| フロントエンド | [react-form-study](https://github.com/wiz-program/react-form-study) | フォーム UI・クライアントバリデーション・確認画面 |
| バックエンド | このリポジトリ | API 受付・サーバーバリデーション・DB 保存 |

---

## 技術スタック

- Python 3.12+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)（`EmailStr` によるメール形式チェック）
- [asyncpg](https://magicstack.github.io/asyncpg/)（PostgreSQL 非同期ドライバ）
- [uv](https://docs.astral.sh/uv/)（パッケージ管理）
- Neon（PostgreSQL）

---

## プロジェクト構成

```
python-form/
├── main.py          # FastAPI アプリ・API エンドポイント・DB 保存処理
├── pyproject.toml   # 依存関係定義
├── uv.lock          # ロックファイル
└── .env             # 環境変数（ローカル開発用・Git 管理外）
```

---

## API 仕様

### `POST /api/v1/register-questionnaire`

応募フォームのデータを受け取り、`questionnaires` テーブルに保存します。

#### リクエストボディ

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

#### レスポンス（成功時）

```json
{
  "status": "success",
  "message": "山田太郎さんの応募を受付、データベースに保存しました。"
}
```

#### Swagger UI

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
git clone <このリポジトリの URL>
cd python-form
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

## フロントエンドとの接続

ローカル開発時は、フロントエンドの axios リクエスト先を以下に変更します。

```
http://localhost:8000/api/v1/register-questionnaire
```

CORS は開発用に `allow_origins=["*"]` を設定しています。本番デプロイ時はフロントエンドのドメインに絞ることを推奨します。

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

- API ベース URL: `https://<your-service>.onrender.com`
- エンドポイント: `https://<your-service>.onrender.com/api/v1/register-questionnaire`

フロントエンド側の API URL をデプロイ先に合わせて更新してください。

---

## 設計方針

- **バリデーションの二重化**: フロント（Zod）とバックエンド（Pydantic）で同じルールを適用
- **SQL インジェクション対策**: asyncpg のプレースホルダー（`$1`, `$2`...）を使用
- **接続管理**: `try` / `finally` で DB 接続を必ずクローズ
- **責務の分離**: リクエストモデル（`RegisterQuestionnaireRequest`）とルートハンドラを `main.py` に集約（学習段階のためシンプルな構成）

---

## 関連リポジトリ

- フロントエンド: [wiz-program/react-form-study](https://github.com/wiz-program/react-form-study)

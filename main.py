import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
import asyncpg  #  生のSQLを高速に実行するライブラリ
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="フルスタック応募フォーム API (DB連携版)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterQuestionnaireRequest(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)
    gender: str = Field(..., min_length=1)
    prize: Literal["A", "B", "C"]

@app.post("/api/v1/register-questionnaire")
async def register_questionnaire(payload: RegisterQuestionnaireRequest):
    # 1. Neon(PostgreSQL)への接続
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # 2. SQLを実行してデータをインサートする
        # 3. idとcreated_atはSERIALとDEFAULTがあるので、SQLに書かなくてOK
        # 4. $1, $2... はインジェクション攻撃を防ぐためのプレースホルダー
        await conn.execute('''
            INSERT INTO questionnaires (name, email, password, gender, prize)
            VALUES ($1, $2, $3, $4, $5)
        ''', payload.name, payload.email, payload.password, payload.gender, payload.prize)
        
        print(f"データベースに {payload.name} さんのデータを追加完了")
        
        return {
            "status": "success",
            "message": f"{payload.name}さんの応募を受付、データベースに保存しました。"
        }
        
    except Exception as e:
        print(f"データベースの保存に失敗しました: {e}")
        raise HTTPException(status_code=500, detail="データベースの保存に失敗しました")
        
    finally:
        # 5. 使い終わった接続を必ず閉じる
        await conn.close()
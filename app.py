from bson import ObjectId  # pymongo가 설치될 때 함께 설치됨. (install X)
from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request
from flask.json.provider import JSONProvider
from datetime import datetime

import json
import sys
import os

ENV = os.getenv("FLASK_ENV", "development")

if ENV == "development":
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
else:
    MONGODB_URI = os.getenv("MONGODB_URI")
    if not MONGODB_URI:
        print("CRITICAL ERROR: MONGODB_URI is not set in environment variables!")
        sys.exit(1)  # 프로세스를 에러와 함께 종료

app = Flask(__name__)

client = MongoClient(MONGODB_URI)
db = client.dbjungle


#####################################################################################
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


app.json = CustomJSONProvider(app)
# #####################################################################################


@app.route("/")
def home():
    return render_template("index.html")


# ✅ 목록 조회: 좋아요 내림차순 정렬 (원하면 createdAt 기준으로 바꿀 수 있음)
@app.route("/api/list", methods=["GET"])
def show_memos():
    # ✅ projection: 필요한 필드만 내려서 가볍게 + 안전하게
    memos = list(
        db.memos.find({}, {"title": 1, "content": 1, "likes": 1}).sort("likes", -1)
    )
    # ObjectId -> str 은 CustomJSONProvider가 처리해주지만,
    # 명시적으로 처리해도 OK. (여기서는 provider가 하므로 생략 가능)
    return jsonify({"result": "success", "memo_list": memos})


# ✅ 생성
@app.route("/api/create", methods=["POST"])
def create_memo():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    # ✅ 서버에서 반드시 입력검증 (프론트 검증은 우회 가능)
    if not title or not content:
        return jsonify({"result": "failure", "msg": "title/content required"}), 400

    # ✅ 길이 제한(너무 긴 입력 방지) - 필요시 조정
    if len(title) > 100 or len(content) > 2000:
        return jsonify({"result": "failure", "msg": "title/content too long"}), 400

    doc = {
        "title": title,
        "content": content,
        "likes": 0,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    r = db.memos.insert_one(doc)
    return jsonify({"result": "success", "id": str(r.inserted_id)})


# ✅ 삭제: title 기준 ❌ -> _id 기준 ✅
@app.route("/api/delete", methods=["POST"])
def delete_memo():
    memo_id = request.form.get("id", "").strip()

    # ✅ ObjectId 변환 예외 처리
    try:
        oid = ObjectId(memo_id)
    except Exception:
        return jsonify({"result": "failure", "msg": "invalid id"}), 400

    result = db.memos.delete_one({"_id": oid})
    if result.deleted_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure", "msg": "not found"}), 404


# ✅ 수정: title 기준 ❌ -> _id 기준 ✅
@app.route("/api/update", methods=["POST"])
def update_memo():
    memo_id = request.form.get("id", "").strip()
    new_title = request.form.get("new_title", "").strip()
    new_content = request.form.get("new_content", "").strip()

    if not memo_id:
        return jsonify({"result": "failure", "msg": "id required"}), 400
    if not new_title or not new_content:
        return jsonify({"result": "failure", "msg": "title/content required"}), 400
    if len(new_title) > 100 or len(new_content) > 2000:
        return jsonify({"result": "failure", "msg": "title/content too long"}), 400

    try:
        oid = ObjectId(memo_id)
    except Exception:
        return jsonify({"result": "failure", "msg": "invalid id"}), 400

    # ✅ modified_count는 "같은 값으로 저장하면 0"이 될 수 있음
    #   - 그래서 matched_count(문서가 존재했는지)를 성공 기준에 포함하는 게 안전
    result = db.memos.update_one(
        {"_id": oid},
        {
            "$set": {
                "title": new_title,
                "content": new_content,
                "updatedAt": datetime.utcnow(),
            }
        },
    )

    if result.matched_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure", "msg": "not found"}), 404


# ✅ 좋아요: find→+1→update ❌ -> $inc ✅ (원자적 증가)
@app.route("/api/like", methods=["POST"])
def like_memo():
    memo_id = request.form.get("id", "").strip()

    try:
        oid = ObjectId(memo_id)
    except Exception:
        return jsonify({"result": "failure", "msg": "invalid id"}), 400

    result = db.memos.update_one({"_id": oid}, {"$inc": {"likes": 1}})
    if result.matched_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "failure", "msg": "not found"}), 404


if __name__ == "__main__":
    print(sys.executable)
    # ✅ 운영 배포 시 debug=False 권장
    app.run("0.0.0.0", port=5000, debug=False)

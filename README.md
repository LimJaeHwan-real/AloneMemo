# 🚀 Flask & MongoDB 프로젝트 실행 가이드

### 1. 가상환경 설정 (최초 1회)
프로젝트를 처음 다운로드 받았다면 터미널에서 가상환경을 생성합니다.
```bash
python -m venv venv
```

### 2. 가상환경 활성화 (매번 실행 시)
작업을 시작할 때마다 본인의 운영체제에 맞게 가상환경을 켭니다. 성공하면 터미널 앞에 `(venv)`가 표시됩니다.
* **Windows (Git Bash)**: `source venv/Scripts/activate`
* **Windows (CMD)**: `venv\Scripts\activate`
* **Mac / Linux**: `source venv/bin/activate`

### 3. 필수 라이브러리 설치
가상환경이 켜진 상태에서 `requirements.txt`에 적힌 패키지들을 한 번에 설치합니다.
```bash
pip install -r requirements.txt
```

### 4. MongoDB 실행 확인
서버를 켜기 전, 내 컴퓨터에 **MongoDB**가 실행 중인지 확인합니다. (기본 포트: `localhost:27017`)

### 5. 애플리케이션 실행
모든 준비가 끝났습니다. 아래 명령어로 서버를 실행하고, 브라우저에서 `http://localhost:5000`에 접속하세요.
```bash
python app.py
```

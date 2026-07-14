# townly-be

# LocalHub Backend

지역 정보 공유 커뮤니티(LocalHub) 백엔드 프로젝트입니다.

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite
- Uvicorn

---

# 프로젝트 실행

## 1. Repository Clone

```bash
git clone <BACKEND_REPOSITORY_URL>
```

```bash
cd <repository_name>
```

---

## 2. 가상환경 생성

```bash
python -m venv venv
```

---

## 3. 가상환경 실행

### Windows (Git Bash)

```bash
source venv/Scripts/activate
```

### Windows (PowerShell)

```powershell
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 4. 패키지 설치

```bash
pip install -r requirements.txt
```

---

## 5. 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 생성합니다.

```bash
cp .env.example .env
```

Windows에서 `cp`가 안 되면 `.env.example`을 복사해서 `.env`로 이름만 변경하면 됩니다.

`.env`

```env
DATABASE_URL=sqlite:///./localhub.db
OPENAI_API_KEY=
FRONTEND_URL=http://localhost:5173
```

---

## 6. 서버 실행

```bash
uvicorn app.main:app --reload
```

---

## 7. Swagger

브라우저 접속

```
http://localhost:8000/docs
```

Health Check

```
http://localhost:8000/api/health
```

---

# 프로젝트 구조

```
app/
├── api
├── core
├── db
├── models
├── schemas
├── services
├── utils
└── main.py
```

---

# Git 규칙

`.env`

`venv`

`*.db`

는 Git에 포함하지 않습니다.

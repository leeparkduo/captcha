# CAPTCHA (가칭)

Project Layout
```
captcha/
├─ app/
│   ├─ main.py
│   ├─ database.py
│   ├─ models.py
│   ├─ schemas.py
│   ├─ utils.py
│   └─ data_loader.py
│
├─ images/
├─ labels/
├─ static/
│   ├─ index.html
│   ├─ style.css
│   └─ script.js
└─ requirements.txt
```

## 설치
### 파이썬 환경 설정
```sh
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```
### 데이터 다운로드
```sh
$ python download.py
```

### 서버 실행 및 접속
```sh
$ uvicorn app.main:app --reload
```
실행 이후 웹 브라우저에서 `http://localhost:8000`에 접속합니다.
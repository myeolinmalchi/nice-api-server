# 나이스 본인인증 API 연동 서버

## 실행 방법

### 직접 실행

1. 레포지토리 클론

```console
$ git clone https://github.com/myeolinmalchi/nice-api-server
$ cd nice-api-server
```

2. 가상환경 설정 및 라이브러리 설치

```console
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python3 -m pip install -r requirements.txt
```

3. `config.json` 생성 및 값 입력

```console
$ cp ./config.example.json ./config.json
$ vim ./config.json
```

4. (Optional) 액세스 토큰 발급

```
$ python3 init_token.py
```

5. 서버 실행

```
$ uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 도커

1. 레포지토리 클론

```console
$ git clone https://github.com/myeolinmalchi/nice-api-server
$ cd nice-api-server
```

2. 도커 컨테이너 빌드

```console
$ docker build -t nice-api-server .
```

3. `config.json` 생성 및 값 입력

```console
$ cp ./config.example.json ./config.json
$ vim ./config.json
```

4. 도커 컨테이너 실행

```console
$ docker run -p 8000:8000 nice-api-server
```

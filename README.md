# 교육 신청 시스템

교육 소개, 신청 접수, 신청 관리를 한 흐름으로 다루는 Django 서비스입니다.

## 개요

방문자는 공개된 교육 목록에서 모집 상태와 교육 기간을 보고, 교육 상세에서 소개와 커리큘럼을 확인합니다. 모집중인 교육은 그 페이지에서 이름, 이메일, 주소, 연락 가능 날짜를 남겨 신청합니다. 신청은 Ajax로 접수 API에 전달되고, 접수되면 확인 메일이 갑니다.

운영자는 Django admin에서 신청을 조회·수정·삭제하고, 상태를 접수, 확인중, 완료로 바꿉니다. 고른 신청은 CSV로 받을 수 있습니다. 연락 가능 날짜가 된 신청에는 안내 메일을 보낼 수 있습니다.

## 실행 방법

Python 3.12, [uv](https://docs.astral.sh/uv/), Docker가 필요합니다. 데이터베이스는 Docker Compose의 Postgres입니다.

```bash
make setup
make superuser
make run
```

`make setup`은 의존성 설치, git hook, `.env` 생성, Postgres 기동, 마이그레이션, 샘플 데이터까지 한 번에 실행합니다. `.env`가 이미 있으면 덮어쓰지 않습니다. 샘플에는 모집중인 `파이썬 입문`과 모집 예정인 `웹 서비스 기초`가 들어 있습니다.

개발 서버는 http://127.0.0.1:8000/ 입니다.

| 주소 | 설명 |
| --- | --- |
| `/` | 공개된 교육 목록 |
| `/courses/<slug>/` | 교육 상세와 수강 신청 |
| `/admin/` | 교육·신청 관리 |
| `POST /api/applications/` | 공개된 교육에 신청. 로그인 없이 접수되고 확인 메일을 보냅니다 |
| `GET /api/applications/` | 신청 목록. 관리자만 조회합니다. `status`, `q`로 거르고 한 페이지에 20건입니다 |
| `GET /api/applications/<id>/` | 신청 한 건. 관리자만 조회합니다 |

신청 수정과 삭제는 API에 없고 admin에서 합니다. 모집 예정이거나 모집이 마감된 교육의 상세 페이지에는 신청 폼이 나오지 않습니다.

연락 안내 메일은 스케줄러 없이 명령으로 보냅니다. 연락 가능 날짜가 오늘이거나 그 전이고, 아직 안내를 보내지 않은 신청만 대상입니다.

```bash
uv run python manage.py send_contact_notices
```

개발 중 메일은 `.env`의 `EMAIL_BACKEND`를 따릅니다. 예제 설정은 콘솔에 출력합니다.

자주 쓰는 명령은 아래와 같습니다.

```bash
make seed       # 샘플 교육, 커리큘럼, 신청을 다시 넣습니다. 이미 있는 데이터는 중복되지 않습니다
make test       # pytest. Postgres가 꺼져 있으면 켭니다
make lint       # ruff format, ruff check, ty
make down       # Postgres 중지
```

## 사용 기술

- Python 3.12, Django 5.2, Django REST framework
- PostgreSQL 16, psycopg
- uv, pytest, factory-boy, ruff, ty
- 이미지 업로드는 Pillow, 정적 파일은 WhiteNoise
- 화면 문구와 시간대는 한국어, `Asia/Seoul`입니다

설정은 `configs/`, 앱 코드는 `apps/`에 있습니다. `apps/catalog`가 교육과 커리큘럼, `apps/applications`가 신청·메일·API, `apps/common`이 생성·수정 시각 믹스인입니다.

운영 이미지는 `Dockerfile`에서 gunicorn으로 띄우고, 시작 시 마이그레이션을 실행합니다. Compose 파일은 로컬 Postgres만 올립니다.

## 설계 의도

교육 소개와 신청을 앱으로 나눴습니다. 목록과 상세는 공개된 교육만 보여줍니다. 신청 접수와 확인 메일은 DRF로 만든 `POST /api/applications/`에 이미 있으므로, 상세 페이지가 폼을 직접 저장하지 않습니다. 신청 버튼은 Ajax로 그 API를 호출하고, 응답의 접수 결과와 입력 오류만 화면 일부에 반영합니다.

신청 상태는 접수, 확인중, 완료입니다. 목록 조회는 상태와 이름·이메일 검색을 쿼리셋에서 처리합니다. 연락 안내 메일은 날짜가 된 신청 중 아직 보내지 않은 것만 골라, 같은 명령을 다시 실행해도 중복으로 보내지 않습니다.

관리자 화면은 Django admin을 그대로 씁니다. 상태 변경과 CSV 내보내기는 선택한 신청에만 적용됩니다.

## 첨부 문서

- [AI 코딩 보조 도구 사용 내역과 활용 이유](docs/ai-usage.md)

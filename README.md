# ✈️ Air-Safe README

> https://air-safe.co.kr

Air-Safe는 기내반입/위탁수하물 제한 품목을 검색할 수 있는 웹 애플리케이션입니다. 

### Prerequisites

* Python >= 3.8
* PostgreSQL

### Create a Virtual Enviroment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Database Configuration

#### file tree

```
/your-project-directory
│
├── config.yml
├── app
│   ├── main.py
│   ├── ...
│
└── requirements.txt
```
#### config.yml

```yaml
db:
  host: {your_database_host}
  port: {your_database_port}
  user: {your_database_user_name}
  password: {your_database_password}
  database: [your_schema_name]
```

### run server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Documentation

**EP** : http://localhost:8000/docs
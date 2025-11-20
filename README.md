# Python Serverless News Bot (Keyword Hunter)

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Notification-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automation-2088FF?style=flat-square&logo=github-actions&logoColor=white)

![Telegram Preview](assets/telegram_preview.png)

> "서버비 걱정 없는 평생 무료 자동화 솔루션"

원하는 키워드의 최신 뉴스를 실시간으로 감지하여 텔레그램 봇으로 즉시 알림을 보내고,  
전송 이력을 Supabase (PostgreSQL)에 저장해 중복 기사를 완벽하게 차단하는 서버리스 뉴스 알리미 봇입니다.  
GitHub Actions만으로 24시간 365일 무료 구동!

## ✨ Key Features

- 서버리스 아키텍처 → 서버 비용 0원
- Supabase 연동으로 완벽한 중복 방지
- 텔레그램 실시간 알림
- 감시 키워드 무제한 추가 가능
- 네이버 뉴스 UI 변경 자동 대응 + 차단 방지 로직 내장

## 🛠 Tech Stack

- Python 3.10+
- Supabase (Serverless PostgreSQL)
- GitHub Actions (Cron)
- requests, beautifulsoup4, supabase-py, python-dotenv

## 🚀 How to Run

### 1. 로컬에서 테스트

프로젝트 루트에 `.env` 파일 생성 후 아래 내용 입력

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
SEARCH_KEYWORD=속보,비트코인,AI,삼성전자

그 후 터미널에서

pip install -r requirements.txt
python main.py

### 2. GitHub Actions로 자동 실행 (추천)

1. 이 레포지토리 Fork
2. Settings → Secrets and variables → Actions
3. 위의 5개 환경변수를 동일하게 등록

→ 15분마다 자동 실행 시작!

## 📊 Supabase 테이블 구조 (news_logs)

| Column      | Type         | 설명                    |
|-------------|--------------|-------------------------|
| id          | int8         | Primary Key             |
| title       | text         | 뉴스 제목               |
| link        | text         | 뉴스 링크 (Unique)      |
| created_at  | timestamptz  | 생성 시간 (기본값 now())|

Developed with ❤️ by hwanyc
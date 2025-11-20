import os
import time
import logging
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class NewsMonitor:
    def __init__(self):
        self.sb_url = os.getenv("SUPABASE_URL")
        self.sb_key = os.getenv("SUPABASE_KEY")
        self.tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        raw_keywords = os.getenv("SEARCH_KEYWORD", "속보")
        self.keywords = [k.strip() for k in raw_keywords.split(',')]

        if not self.sb_url:
            logging.error("❌ 치명적 오류: SUPABASE_URL 환경변수가 없습니다.")
        if not self.sb_key:
            logging.error("❌ 치명적 오류: SUPABASE_KEY 환경변수가 없습니다.")
        if not self.tg_token:
            logging.error("❌ 치명적 오류: TELEGRAM_BOT_TOKEN 환경변수가 없습니다.")

        try:
            self.supabase: Client = create_client(self.sb_url, self.sb_key)
            logging.info(f"✅ 봇 가동 시작! 감시 키워드: {self.keywords}")
        except Exception as e:
            logging.error(f"Supabase 연결 실패: {e}")

    def send_telegram(self, message):
        url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
        payload = {"chat_id": self.tg_chat_id, "text": message}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            logging.error(f"텔레그램 전송 실패: {e}")

    def check_duplicate(self, link):
        try:
            response = self.supabase.table("news_logs").select("*").eq("link", link).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"DB 조회 실패: {e}")
            return False

    def save_log(self, title, link):
        try:
            data = {"title": title, "link": link}
            self.supabase.table("news_logs").insert(data).execute()
        except Exception as e:
            logging.error(f"DB 저장 실패: {e}")

    def fetch_news(self):
        """다중 키워드 크롤링 로직"""

        # [업그레이드 포인트 2] 키워드 리스트를 하나씩 돌면서 검색
        for keyword in self.keywords:
            self._search_one_keyword(keyword)
            # 네이버 차단 방지를 위해 키워드 사이에 잠깐 쉼 (사람인 척)
            time.sleep(2)

    def _search_one_keyword(self, keyword):
        """단일 키워드 검색 헬퍼 함수"""
        encoded_keyword = quote(keyword)
        base_url = f"https://search.naver.com/search.naver?where=news&query={encoded_keyword}&sm=tab_opt&sort=1"

        logging.info(f"🔍 '[{keyword}]' 검색 중...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://search.naver.com/"
            }

            res = requests.get(base_url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')

            # SDS 최신 구조 대응
            title_spans = soup.select("span.sds-comps-text-type-headline1")
            if not title_spans:
                title_spans = soup.select("a.news_tit")

            if not title_spans:
                logging.warning(f"⚠️ '{keyword}' 검색 결과 없음 (구조 변경 또는 뉴스 없음)")
                return

            count = 0
            for span in title_spans:
                title = span.get_text().strip()
                parent_a = span.find_parent("a")

                if span.name == 'a':
                    link = span['href']
                elif parent_a:
                    link = parent_a['href']
                else:
                    continue

                if not self.check_duplicate(link):
                    # 메시지에 어떤 키워드로 찾았는지 명시
                    msg = f"[{keyword} 알림] 🔔\n{title}\n{link}"
                    self.send_telegram(msg)
                    self.save_log(title, link)
                    logging.info(f"🚀 [{keyword}] 전송: {title}")
                    count += 1
                    time.sleep(0.5)
                else:
                    pass

            if count > 0:
                logging.info(f"✨ [{keyword}] {count}개 업데이트 완료")

        except Exception as e:
            logging.error(f"❌ '{keyword}' 크롤링 중 에러: {e}")

    def run(self):
        logging.info("🚀 GitHub Actions에 의해 실행됨")
        self.fetch_news()
        logging.info("👋 작업 완료. 종료합니다.")

if __name__ == "__main__":
    bot = NewsMonitor()
    bot.run()
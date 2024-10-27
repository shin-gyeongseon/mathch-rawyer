from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import threading

lock = threading.Lock()
lawyers_data = []
error_data = []


class LawyerCrawler:
    def __init__(self, last_page=1830, max_threads=10):
        self.last_page = last_page
        self.max_threads = max_threads
    
    def crawl_page(self, page):
        base_url = "https://www.koreanbar.or.kr/pages/search/search1.asp"
        url = f"{base_url}?sido1=%EC%84%9C%EC%9A%B8&gun1=&dong1=&special1_1=&special1=&searchtype=mname&searchstr=&page={page}"
        response = requests.get(url)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"페이지 {page} 접근 실패. 상태 코드: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table_style4'})
        
        if not table:
            print(f"페이지 {page}에 테이블이 없습니다.")
            return
        
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            try:
                cols = row.find_all('td')
                name = cols[2].get_text(strip=True)
                office_name = cols[5].get_text(strip=True)
                birth_year = cols[4].get_text(strip=True) if len(cols) > 4 else ''
                address = cols[6].get_text(strip=True)
                
                with lock:
                    lawyers_data.append({
                        '성명': name,
                        '사무소명': office_name,
                        '출생년도': birth_year,
                        '주소': address
                    })
            except Exception as e:
                with lock:
                    error_data.append(str(row))
                    print(f"페이지 {page}에서 오류 발생: {e}")

    def run_crawler(self):
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.crawl_page, page) for page in range(1, self.last_page + 1)]
            for future in as_completed(futures):
                future.result()
        df = pd.DataFrame(lawyers_data)
        df.to_csv('seoul_lawyers.csv', index=False, encoding='utf-8-sig')
        print("정상 데이터 CSV 파일로 저장 완료.")
        
        if error_data:
            with open('error_rows.txt', 'w', encoding='utf-8') as f:
                for row in error_data:
                    f.write(row + '\n')
            print("오류 데이터 파일로 저장 완료.")
            
    def is_exist_file(self, path: str) -> bool:
        exist: bool = os.path.isfile(path)
        return exist
    
if __name__ == '__main__':
    crawler = LawyerCrawler()
    
    if crawler.is_exist_file('./seoul_lawyers.csv'):
        print('존재합니다.')
    else:
        print('없습니다.')
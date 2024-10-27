from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from soupsieve import select

from cleaner import LawyerCleaner
from crawler import LawyerCrawler
from matcher import LawyerMatcher

import pandas as pd

def main():
    max_threads = 10  # 스레드 개수
    last_page = 1830  # 마지막 페이지
    
    print("크롤링 시작...")
    crawler = LawyerCrawler(last_page=1830, max_threads=10)
    if not crawler.is_exist_file('seoul_lawyers.csv'):
        crawler.run_crawler()
    else: 
        print('이미 파일이 존재하여 넘어갑니다. 새롭게 크롤링을 진행하고 싶다면 기존에 있는 파일을 제거해주세요')
    
    print("\n이름 정리 시작...")

    selected_rawyer_list_path = 'seleted_rawyer_list_tag.html'
    selected_rawyer_list_output_path = 'selected_rawyer_list.csv'
    cleaner = LawyerCleaner()
    cleaner.export_names_by_html(selected_rawyer_list_path,
                                 selected_rawyer_list_output_path)

    seoul_lawyers_input_file = 'seoul_lawyers.csv'
    seoul_lawyers_output_file = 'seoul_lawyers_cleaned.csv'
    out_filename = cleaner.clean_names_in_csv_and_out_filename(seoul_lawyers_input_file, seoul_lawyers_output_file)

    print("\n매칭 시작...")
    # matcher = LawyerMatcher()
    # matcher.load_and_prepare_data()
    # results = matcher.find_matches()
    try:
        matcher = LawyerMatcher()
        matcher.initialize_data(select_rawyer_list_path=selected_rawyer_list_output_path,
                                seoul_lawyers_cleaned_path=seoul_lawyers_output_file)
        matcher.find_matches(similarity_threshold=0.7)
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
    
    # results_df = pd.DataFrame(results)
    # results_df.to_csv('matched_rawyers.csv', index=False, encoding='utf-8')
    # print("\n전체 작업이 완료되었습니다. 매칭 결과가 'search_results/matched_lawyers.csv'에 저장되었습니다.")

if __name__ == "__main__":
    main()

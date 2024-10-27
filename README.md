# 변호사 데이터 처리 프로젝트
웹 페이지와 HTML 파일에서 변호사 데이터를 수집, 정리, 매칭하는 Python 프로젝트입니다.

# 목차
- 프로젝트 개요
- 디렉토리 구조
- 설치 방법
- 사용법
- 모듈 설명
- 라이센스

## 프로젝트 개요
이 프로젝트는 웹 크롤링 및 데이터 처리를 통해 변호사 데이터를 자동으로 수집, 정리, 매칭하는 기능을 제공합니다. 주요 단계는 다음과 같습니다:

1. 데이터 크롤링: 웹 페이지에서 변호사 정보를 수집합니다. 
2. 데이터 정리: 수집된 데이터를 정리하고 표준화합니다. 
3. 데이터 매칭: 데이터 레코드를 비교 및 매칭하여 일관성을 분석합니다.

## 디렉토리 구조
프로젝트의 디렉토리 구조는 다음과 같이 구성됩니다:
```angular2html
lawyer-data-processing/
├── cleaner.py           # HTML 및 CSV 파일을 정리하는 모듈
├── crawler.py           # 변호사 정보를 수집하는 웹 크롤러
├── matcher.py           # 데이터 매칭 및 처리 모듈
├── main.py              # 전체 프로세스를 실행하는 메인 스크립트
├── __init__.py          # 패키지 초기화 파일
└── README.md            # 프로젝트 설명서
```

## 설치 방법
1. 저장소 클론:

```bash
코드 복사
git clone https://github.com/yourusername/lawyer-data-processing.git
cd lawyer-data-processing
필요한 패키지 설치: 이 프로젝트는 Python 3.7 이상이 필요합니다. 아래 명령어로 필요한 패키지를 설치합니다:
```
```bash
코드 복사
pip install -r requirements.txt
BeautifulSoup, pandas, requests와 같은 라이브러리가 requirements.txt에 포함되어 있어야 합니다.
```

## 사용법
전체 워크플로우를 실행하려면 main.py 파일을 실행합니다:

1. 데이터 크롤링:
   - 지정된 웹사이트에서 변호사 데이터를 수집합니다. 
   - 수집된 데이터는 seoul_lawyers.csv에 저장됩니다.
2. 데이터 정리:
   - HTML 또는 CSV 파일에서 변호사 이름과 주소를 정리합니다. 
   - 정리된 데이터는 seoul_lawyers_cleaned.csv에 저장됩니다.
3. 데이터 매칭:
   - 이름과 주소 유사도를 기준으로 정리된 데이터의 레코드를 매칭합니다.
   - 매칭 결과는 search_results/all_matches.csv에 저장됩니다.

## 모듈 설명
1. cleaner.py
   - 주요 함수:
     - clean_names_in_csv_and_out_filename(): CSV 파일에서 변호사 이름을 정리합니다. 
     - export_names_by_html(): HTML 파일에서 이름과 주소를 추출하여 CSV로 저장합니다.
2. crawler.py
   - 주요 함수:
     - crawl_page(): 지정된 웹사이트에서 한 페이지의 데이터를 크롤링합니다. 
     - run_crawler(): 여러 페이지에 걸쳐 크롤러를 실행합니다. 
     - is_exist_file(): 지정된 경로에 파일이 존재하는지 확인합니다.
3. matcher.py 
   - 주요 함수:
     - initialize_data(): CSV 파일에서 데이터를 불러와 매칭 준비를 합니다. 
     - find_matches(): 이름과 주소 유사도를 기준으로 매칭을 수행합니다. 
     - extract_name_parts(): 매칭 정확성을 높이기 위해 이름의 구성 요소를 추출합니다.
           
## 라이센스
이 프로젝트는 MIT 라이센스 하에 배포됩니다.
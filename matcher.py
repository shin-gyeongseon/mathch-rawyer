import pandas as pd
import os
from difflib import SequenceMatcher
import re

class LawyerMatcher:
    def __init__(self):
        self.lawyers_df = None
        self.addresses_df = None

    def initialize_data(self, seoul_lawyers_cleaned_path:str, select_rawyer_list_path:str):
        """데이터 파일들을 로드하고 전처리합니다."""
        try:
            # 기본 변호사 정보 로드
            self.lawyers_df = pd.read_csv(seoul_lawyers_cleaned_path)
            
            # 변호사 주소 정보 로드
            self.addresses_df = pd.read_csv(select_rawyer_list_path)
            
            # 주소 전처리
            self._preprocess_addresses()
            
            print("데이터 로드 완료")
            print(f"검색할 변호사 수: {len(self.addresses_df)}명")
        except Exception as e:
            print(f"데이터 로드 중 오류 발생: {e}")
            raise

    def _preprocess_addresses(self):
        """주소 데이터를 전처리합니다."""
        # 구 정보 추출
        self.lawyers_df['구'] = self.lawyers_df['주소'].str.extract(r'서울\s+(\w+구)')
        self.addresses_df['구'] = self.addresses_df['주소'].str.extract(r'서울\s+(\w+구)')
        
        # 주소 정규화
        self.lawyers_df['정규화_주소'] = self._normalize_address(self.lawyers_df['주소'])
        self.addresses_df['정규화_주소'] = self._normalize_address(self.addresses_df['주소'])

    def _normalize_address(self, address_series):
        """주소를 정규화합니다."""
        return address_series.str.replace(r'\s+', '', regex=True) \
                           .str.replace(r'\(.*?\)', '', regex=True) \
                           .str.replace(r'[0-9-]+', '', regex=True) \
                           .str.replace(r'층|호|번지', '', regex=True) \
                           .str.lower()

    def _calculate_address_similarity(self, addr1, addr2):
        """두 주소 간의 유사도를 계산합니다."""
        return SequenceMatcher(None, addr1, addr2).ratio()

    def extract_name_parts(self, name):
        """이름에서 첫 글자와 마지막 글자를 추출합니다."""
        if pd.isna(name) or len(name) < 2:
            return None, None
        return name[0], name[-1]

    def find_matches(self, similarity_threshold=0.7):
        """lawyers_addresses.csv의 모든 데이터에 대해 매칭되는 변호사를 검색합니다."""
        all_results = []
        total_matches = {'구_매칭': 0, '주소_매칭': 0}
        
        # 결과 저장용 디렉토리 생성
        os.makedirs('search_results', exist_ok=True)
        
        print("\n매칭 검색을 시작합니다...")
        
        for idx, row in self.addresses_df.iterrows():
            first_letter, last_letter = self.extract_name_parts(row['이름'])
            district = row['구']
            normalized_address = row['정규화_주소']
            
            if first_letter and last_letter:
                # 구 기반 매칭
                district_matches = self._search_by_district(first_letter, last_letter, district)
                
                # 전체 주소 기반 매칭
                address_matches = self._search_by_full_address(
                    first_letter, last_letter, normalized_address, similarity_threshold
                )
                
                if not district_matches.empty or not address_matches.empty:
                    result = {
                        'search_name': row['이름'],
                        'search_address': row['주소'],
                        'district_matches': district_matches,
                        'address_matches': address_matches
                    }
                    all_results.append(result)
                    total_matches['구_매칭'] += len(district_matches)
                    total_matches['주소_매칭'] += len(address_matches)
                    
            # 진행 상황 표시
            if (idx + 1) % 100 == 0:
                print(f"진행 중... {idx + 1}명 처리 완료")
        
        self._save_and_print_results(all_results, total_matches)

    def _search_by_district(self, first_letter, last_letter, district):
        """구 정보를 기반으로 검색합니다."""
        if pd.isna(district):
            return pd.DataFrame()
        
        return self.lawyers_df[
            (self.lawyers_df['성명'].str[0] == first_letter) &
            (self.lawyers_df['성명'].str[-1] == last_letter) &
            (self.lawyers_df['구'] == district)
        ]

    def _search_by_full_address(self, first_letter, last_letter, normalized_address, threshold):
        """전체 주소 정보를 기반으로 검색합니다."""
        name_matches = self.lawyers_df[
            (self.lawyers_df['성명'].str[0] == first_letter) &
            (self.lawyers_df['성명'].str[-1] == last_letter)
        ]
        
        if name_matches.empty:
            return pd.DataFrame()
        
        # 주소 유사도 계산
        # address_matches = name_matches[
        #     name_matches['정규화_주소'].apply(
        #         lambda x: self._calculate_address_similarity(x, normalized_address) >= threshold
        #     )
        # ]

        # 제공된 주소를 포함하는 변호사 주소만 필터링
        pattern = re.escape(normalized_address)  # 정규식으로 패턴 생성
        address_matches = name_matches[
            name_matches['정규화_주소'].str.contains(pattern)
        ]
        
        return address_matches

    def _save_and_print_results(self, all_results, total_matches):
        """검색 결과를 저장하고 출력합니다."""
        print("\n=== 검색 결과 요약 ===")
        print(f"총 검색된 변호사: {len(self.addresses_df)}명")
        print(f"매칭된 결과가 있는 변호사: {len(all_results)}명")
        print(f"구 기반 매칭 건수: {total_matches['구_매칭']}건")
        print(f"주소 기반 매칭 건수: {total_matches['주소_매칭']}건")
        
        if all_results:
            all_matches_list = []
            
            print("\n=== 상세 매칭 결과 ===")
            for idx, result in enumerate(all_results, 1):
                print(f"\n검색 대상 {idx}")
                print(f"이름: {result['search_name']}")
                print(f"주소: {result['search_address']}")
                
                # 구 기반 매칭 결과 출력
                # if not result['district_matches'].empty:
                #     print("\n[구 기반 매칭 결과]")
                #     self._print_matches(result['district_matches'], result, all_matches_list, '구_매칭')
                
                # 주소 기반 매칭 결과 출력
                if not result['address_matches'].empty:
                    print("\n[주소 기반 매칭 결과]")
                    self._print_matches(result['address_matches'], result, all_matches_list, '주소_매칭')
                
                print("-" * 50)
            
            # 결과를 DataFrame으로 변환하여 CSV로 저장
            matches_df = pd.DataFrame(all_matches_list)
            matches_df.to_csv('search_results/all_matches.csv', 
                            index=False, 
                            encoding='utf-8-sig')
            
            print(f"\n전체 매칭 결과가 'search_results/all_matches.csv'에 저장되었습니다.")
        else:
            print("\n매칭되는 결과가 없습니다.")

    def _print_matches(self, matches, result, all_matches_list, match_type):
        """매칭 결과를 출력하고 리스트에 추가합니다."""
        for _, match in matches.iterrows():
            print(f"\n- 성명: {match['성명']}")
            if pd.notna(match['사무소명']):
                print(f"  사무소명: {match['사무소명']}")
            if pd.notna(match['출생년도']):
                print(f"  출생년도: {match['출생년도']}")
            print(f"  주소: {match['주소']}")
            
            match_dict = {
                '검색_이름': result['search_name'],
                '검색_주소': result['search_address'],
                '매칭_유형': match_type,
                '매칭_성명': match['성명'],
                '매칭_사무소명': match['사무소명'],
                '매칭_출생년도': match['출생년도'],
                '매칭_주소': match['주소']
            }
            all_matches_list.append(match_dict)

def main():
    try:
        matcher = LawyerMatcher()
        matcher.find_matches(similarity_threshold=0.7)
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
import csv
import os
import pandas as pd
from bs4 import BeautifulSoup

class LawyerCleaner:
    def clean_names_in_csv_and_out_filename(self, input_file:str, output_file:str):
        df = pd.read_csv(input_file)
        if '성명' in df.columns:
            df['성명'] = df['성명'].str.replace('개업\[상세보기\]', '', regex=True).str.strip()
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"이름 수정 완료, 결과가 {output_file}에 저장되었습니다.")
        else:
            raise Exception("'성명' 열을 찾을 수 없습니다.")

    def export_names_by_html(self, input_file:str, output_file: str):
        with open(input_file, mode='r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        lawyers_data = []
        
        for option in soup.select('select#AJS_SELECT option'):
            text = option.text.strip()
            if text == '법무사/변호사선택':
                continue
            
            # name, address = text.split(' - ')
            # lawyers_data.append((name, address))
            name, address = [x.strip() for x in text.split(' - ')]
            print(f'name: {name}, address: {address}')
            lawyers_data.append({name, address})
            
        with open(output_file, mode='w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['이름', '주소'])
            writer.writerows(lawyers_data)

# if __name__ == '__main__':
#     cl= LawyerCleaner()
#     cl.clean_seleted_rawer_list_for_html_tag('seleted_rawyer_list_tag.html')
#----------------------------------------------------------
#install chromedriver_binary
#自分のgooglr chromeのversionと一致したdriverをinstallする
#参照->https://yuki.world/python-chrome-driver-version-error/
#----------------------------------------------------------
#必要なモジュールの読み込み
#----------------------------------------------------------
import numpy as np
import pandas as pd

import time
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from googletrans import Translator

import getpass
import sys
#----------------------------------------------------------
#pathの指定
#----------------------------------------------------------
data_path = '../data/'
result_path = '../result/'

#----------------------------------------------------------
#メイン関数の定義
#----------------------------------------------------------
def pubmed_scraping(keyword, page_num):
    #setting
    options = Options()
    options.add_argument('--headless') #ヘッドレスモード
    driver = webdriver.Chrome() 

    #list作成
    title_list = []
    author_list = []
    citation_list = []
    pmid_list = []
    abstract_list = []
    doi_list = []
    japansese_title_list = []
    japansese_abstract_list = []

    #title, authors, pmidの取得
    for i in range(page_num):
        driver.get(f'https://pubmed.ncbi.nlm.nih.gov/?term={keyword}&page={i+1}')
        titles = driver.find_elements_by_class_name('docsum-title')
        authors = driver.find_elements_by_class_name('docsum-authors.full-authors')
        citatons = driver.find_elements_by_class_name('docsum-journal-citation.full-journal-citation')
        pmids = driver.find_elements_by_class_name('docsum-pmid')

        for title in titles:
            title_list.append(title.text) 
        for pmid in pmids:
            pmid = pmid.text
            pmid = int(pmid)
            pmid_list.append(pmid) 
        for author in authors:
            author_list.append(author.text) 
        for citaion in citatons:
            citation_list.append(citaion.text) 
        time.sleep(1)

    #abstract, pmidの取得
    driver = webdriver.Chrome()

    for pmid in pmid_list:
        driver.get('https://pubmed.ncbi.nlm.nih.gov/') 
        driver.find_element_by_id('id_term').send_keys(pmid)
        driver.find_element_by_class_name('search-btn').click() 
        
        ##abstract
        try:
            abstract = driver.find_element_by_xpath('//*[@id="enc-abstract"]/p').text
            abstract_list.append(abstract)
        except :
            abstract_list.append('NaN')
        
        #doi
        try:
            doi = driver.find_element_by_xpath('//*[@id="full-view-heading"]/div[1]/span[1]').text
            doi_list.append(doi)
        except :
            doi_list.append('NaN')
            
        time.sleep(1)
    driver.close()

    #title, abstractの翻訳
    tr = Translator()
    tr.raise_Exception = True
    japansese_title_list = []
    japansese_abstract_list = []

    for title in title_list:
        japanese_title = tr.translate(text=title, src="en", dest="ja").text
        japansese_title_list.append(japanese_title)

    for abstract in abstract_list:
        japanese_abstract = tr.translate(text=abstract, src="en", dest="ja").text
        japansese_abstract_list.append(japanese_abstract)


    #df作成
    df = pd.DataFrame(zip(
        title_list,
        author_list,
        citation_list,
        pmid_list, 
        abstract_list, 
        doi_list, 
        japansese_title_list,
        japansese_abstract_list
    ), 
    columns =[
        'Title',
        'Authors',
        'Citation',
        'pmid',
        'Abstract',
        'Doi',
        'Japanese_Title',
        'Japanese_Abstract'
    ])
    df.index = np.arange(1, len(df)+1) #indexを1から振り直す
    df = df.dropna(subset=['Abstract'])
    #export(csv, excel)
    df.to_excel(result_path + f'{keyword}_papers_information.xlsx', index=False)
#----------------------------------------------------------
#keyword, pagenumの入力
#----------------------------------------------------------
print('Keyword?')
keyword = input('Keyword: ')
print('Page_num ? (The number of papers is pagenum * 10)')
page_num = input('Page_num: ')
page_num= int(page_num)
#----------------------------------------------------------
#処理の決定
#----------------------------------------------------------
answer = input('Are you sure? (y/n): ')
if (answer != 'y' and answer != 'Y'):
    sys.exit(1)
print('処理を継続します')
pubmed_scraping(keyword, page_num)
#----------------------------------------------------------
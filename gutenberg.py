import requests
from bs4 import BeautifulSoup
import os
import re

# 中文書URL
url = 'https://www.gutenberg.org/browse/languages/zh'

# HTTP GET
response = requests.get(url)

# 請求是否成功
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # 書籍鏈接
    book_links = []
    for li in soup.select('li a'):
        link = li.get('href')
        # 只保留以 '/ebooks/' 開頭，並且後面跟隨數字的鏈接
        if link and re.match(r'^/ebooks/\d+$', link):
            book_links.append('https://www.gutenberg.org' + link)

    # 200本
    book_links = book_links[:200]

    # 創建文件夾
    if not os.path.exists('Gutenberg_Chinese_Books'):
        os.makedirs('Gutenberg_Chinese_Books')

    # 書籍內容
    for i, book_link in enumerate(book_links, 1):
        print(f"正在爬取第{i}本書: {book_link}")
        book_response = requests.get(book_link)
        if book_response.status_code == 200:
            book_soup = BeautifulSoup(book_response.content, 'html.parser')
            #  "Read online (web)" 
            read_online_tag = book_soup.find('a', string='Read online (web)')
            if read_online_tag:
                content_link = 'https://www.gutenberg.org' + read_online_tag['href']
                content_response = requests.get(content_link)
                if content_response.status_code == 200:
                    content_soup = BeautifulSoup(content_response.content, 'html.parser')
                    paragraphs = content_soup.find_all('p')
                    
                    # 書名作為文件名
                    title_tag = book_soup.find('h1')
                    title = title_tag.get_text().strip() if title_tag else f'book_{i}'
                    # 非法字符
                    title = title.replace('/', '-').replace('\\', '-')

                    # 保存到文件
                    file_path = os.path.join('Gutenberg_Chinese_Books', f'{title}.txt')
                    with open(file_path, 'w', encoding='utf-8') as file:
                        for paragraph in paragraphs:
                            text = paragraph.get_text()
                            file.write(text + '\n\n')
                    
                    print(f"已保存: {title}")
                else:
                    print(f"無法獲取書籍內容: {content_link}")
            else:
                print(f"未找到 'Read online (web)' 鏈接: {book_link}")
        else:
            print(f"無法訪問書籍頁面: {book_link}")
else:
    print(f"無法訪問中文書籍列表頁面，HTTP狀態碼: {response.status_code}")

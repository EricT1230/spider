import requests
from bs4 import BeautifulSoup
import os

# URL
url = 'https://www.gutenberg.org/browse/languages/zh'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# 200本中文書
book_links = soup.select('li.pgdbetext > a')[:200]

# 目錄
if not os.path.exists('Gutenberg_Books'):
    os.makedirs('Gutenberg_Books')

# 爬書
for link in book_links:
    book_url = 'https://www.gutenberg.org' + link['href']
    book_response = requests.get(book_url)
    book_soup = BeautifulSoup(book_response.content, 'html.parser')

    # 書名、作者、時間、內容
    title = book_soup.find('h1').get_text(strip=True).replace('/', '_')
    author = book_soup.find('h2').get_text(strip=True) if book_soup.find('h2') else '未知作者'
    release_date = book_soup.find(text='Release Date:').find_next().get_text(strip=True) if book_soup.find(text='Release Date:') else '未知日期'
    text_content = book_soup.find('body').get_text(separator='\n', strip=True)

    # FileNmae
    file_name = f"{title}.txt"
    file_path = os.path.join('Gutenberg_Books', file_name)

    # 保存書籍內容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"書名: {title}\n")
        file.write(f"作者: {author}\n")
        file.write(f"出版時間: {release_date}\n\n")
        file.write("內文:\n")
        file.write(text_content)

    print(f"已保存: {title}")

print("Finish")

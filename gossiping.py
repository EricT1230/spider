import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime, timedelta

# Gossiping URL
PTT_URL = 'https://www.ptt.cc'
GOSSIPING_URL = f'{PTT_URL}/bbs/Gossiping/index.html'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'cookie': 'over18=1'
}
session = requests.Session()
session.cookies.set('over18', '1', domain='.ptt.cc')  # 18+

# 7 day
today = datetime.now()
date_limit = today - timedelta(days=7)

def clean_filename(title):
    # 去除非法字符
    return re.sub(r'[\\/*?:"<>|]', "-", title)

def get_article_content_and_comments(article_url):
    response = session.get(article_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        author = soup.select_one('.article-meta-value').text if soup.select_one('.article-meta-value') else None
        title = clean_filename(soup.select('span.article-meta-value')[2].text) if len(soup.select('span.article-meta-value')) > 2 else None
        post_time_str = soup.select('span.article-meta-value')[3].text if len(soup.select('span.article-meta-value')) > 3 else None
        
        # 如果發文時間無法提取，直接返回 None
        post_time = datetime.strptime(post_time_str, '%a %b %d %H:%M:%S %Y') if post_time_str else None
        if post_time and post_time < date_limit:
            return None, None, None, None, None  # 跳過過期的文章

        main_content = soup.find(id='main-content')
        article_content = main_content.text.split('--')[0].strip() if main_content else None

        comments = []
        for comment in soup.find_all('div', class_='push'):
            comment_author = comment.find('span', class_='f3 hl push-userid').text if comment.find('span', class_='f3 hl push-userid') else None
            comment_content = comment.find('span', class_='f3 push-content').text.strip(' :') if comment.find('span', class_='f3 push-content') else None
            comment_time = comment.find('span', class_='push-ipdatetime').text.strip() if comment.find('span', class_='push-ipdatetime') else None

            comments.append({
                'author': comment_author,
                'content': comment_content,
                'time': comment_time
            })

        return title, author, post_time_str, article_content, comments
    
    except Exception as e:
        print(f"Error parsing article: {e}")
        return None, None, None, None, None

def get_posts_from_page(url):
    response = session.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for div in soup.find_all('div', class_='r-ent'):
        if div.find('a'):  # 有超連結的才是正常文章
            title = div.find('a').text
            link = PTT_URL + div.find('a')['href']
            author = div.find('div', class_='author').text
            date = div.find('div', class_='date').text
            
            # 檢查是否是公告或已刪除的文章
            if "[公告]" in title or "已刪除" in title:
                continue
            
            articles.append({
                'title': title,
                'link': link,
                'author': author,
                'date': date
            })
    return articles, soup

def get_previous_page(soup):
    """取得前一頁的 URL"""
    prev_link = soup.select('a.btn.wide')[1]  # 選取第二個包含 'wide' 的按鈕
    if prev_link:
        return PTT_URL + prev_link['href']
    return None

def scrape_gossiping_board():
    current_url = GOSSIPING_URL
    while current_url:
        articles, soup = get_posts_from_page(current_url)
        for article in articles:
            print(f"正在爬取: {article['title']}")
            title, author, post_time_str, content, comments = get_article_content_and_comments(article['link'])

            if title:  # 確保有有效的文章
                # 儲存文章與留言
                filename = f"ptt_gossiping/{title}.txt"
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(f"標題: {title}\n")
                    file.write(f"作者: {author}\n")
                    file.write(f"日期: {post_time_str}\n")
                    file.write(f"內容:\n{content}\n")
                    file.write("\n留言:\n")
                    for comment in comments:
                        file.write(f"{comment['time']} {comment['author']}: {comment['content']}\n")
        
        # 取得前一頁的 URL
        current_url = get_previous_page(soup)

        # 檢查是否爬取到過期文章
        if not articles:
            break

    print("Finish")

# 創資料夾來儲存資料
if not os.path.exists('ptt_gossiping'):
    os.makedirs('ptt_gossiping')

# 開始爬取
scrape_gossiping_board()

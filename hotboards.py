from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# spider
def fetch_ptt_boards():
    url = "https://www.ptt.cc/bbs/hotboards.html"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    hot_boards = soup.find_all('div', class_='b-ent')
    
    boards = []
    for board in hot_boards:
        board_name = board.find('div', class_='board-name').text.strip()
        board_url = "https://www.ptt.cc" + board.find('a')['href']
        boards.append((board_name, board_url))
    
    return boards

@app.route('/')
def home():
    boards = fetch_ptt_boards()
    
    # HTML
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PTT 熱門看板</title>
        <script>
            // 每30秒刷新页面
            setTimeout(function(){
                window.location.reload(1);
            }, 10000);
        </script>
    </head>
    <body>
        <h1>PTT 熱門看板</h1>
        <ul>
            {% for name, url in boards %}
            <li><a href="{{ url }}" target="_blank">{{ name }}</a></li>
            {% endfor %}
        </ul>
    </body>
    </html>
    '''
    
    return render_template_string(html_template, boards=boards)

if __name__ == '__main__':
    app.run(debug=True)

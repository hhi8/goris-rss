from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
import datetime
import pytz

def run():
    # 痞客邦部落格網址
    target_url = "https://goris.pixnet.net/blog"
    
    with sync_playwright() as p:
        # 啟動 Chrome (無頭模式)，並偽裝成一般真實使用者的瀏覽器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"正在前往: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        
        # 尋找文章標題與連結 (痞客邦常見的標籤結構是 .title a 或 h2 a)
        # 這裡我們抓取包含文章連結的 a 標籤
        articles = page.query_selector_all('.title a, h2 a')
        
        print(f"找到 {len(articles)} 篇文章，準備生成 RSS...")
        
        # 初始化 RSS 生成器
        fg = FeedGenerator()
        fg.title("Goris' Sky 痞客邦 RSS (自製版)")
        fg.link(href=target_url, rel='alternate')
        fg.description("使用 Playwright 與 GitHub Actions 每日自動抓取")
        fg.language("zh-TW")
        
        taipei_tz = pytz.timezone('Asia/Taipei')
        
        count = 0
        for article in articles:
            if count >= 10: # 只取最新 10 篇
                break
                
            title = article.inner_text().strip()
            link = article.get_attribute('href')
            
            if title and link and "blog/post" in link:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=link)
                fe.guid(link) # 將網址作為唯一識別碼
                # 設定抓取當下的時間為文章時間 (為了符合 RSS 格式)
                fe.pubDate(datetime.datetime.now(taipei_tz))
                count += 1
                print(f"已加入: {title}")

        # 將結果存成 xml 檔案
        fg.rss_file('rss.xml')
        print("✅ rss.xml 生成成功！")
        
        browser.close()

if __name__ == "__main__":
    run()

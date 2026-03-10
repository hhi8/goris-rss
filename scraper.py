from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
import datetime
import pytz

def run():
    target_url = "https://goris.pixnet.net/blog"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        print(f"正在前往: {target_url}")
        
        try:
            # 【關鍵修改 1】
            # 改成 domcontentloaded：只要網頁基本架構出來就繼續，不等廣告。
            # 並且把超時時間拉長到 60 秒 (60000ms)，以防 GitHub 美國伺服器連台灣太慢。
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            
            # 【關鍵修改 2】
            # 強制等待 5 秒鐘，讓痞客邦的 JavaScript 把文章列表渲染出來
            print("網頁基本載入完成，等待 5 秒讓文章顯示...")
            page.wait_for_timeout(5000)
            
        except Exception as e:
            print(f"載入過程發生超時或錯誤，但嘗試繼續擷取: {e}")
        
        # 尋找文章標題與連結
        articles = page.query_selector_all('.title a, h2 a')
        
        print(f"找到 {len(articles)} 篇文章，準備生成 RSS...")
        
        if len(articles) == 0:
            print("⚠️ 警告：沒有找到任何文章！可能是被防爬蟲機制阻擋，或網頁結構改變。")
            print("當前網頁標題:", page.title())
        
        fg = FeedGenerator()
        fg.title("Goris' Sky 痞客邦 RSS (自製版)")
        fg.link(href=target_url, rel='alternate')
        fg.description("使用 Playwright 與 GitHub Actions 每日自動抓取")
        fg.language("zh-TW")
        
        taipei_tz = pytz.timezone('Asia/Taipei')
        
        count = 0
        for article in articles:
            if count >= 10:
                break
                
            title = article.inner_text().strip()
            link = article.get_attribute('href')
            
            if title and link and "blog/post" in link:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=link)
                fe.guid(link)
                fe.pubDate(datetime.datetime.now(taipei_tz))
                count += 1
                print(f"已加入: {title}")

        fg.rss_file('rss.xml')
        print("✅ rss.xml 生成成功！")
        
        browser.close()

if __name__ == "__main__":
    run()

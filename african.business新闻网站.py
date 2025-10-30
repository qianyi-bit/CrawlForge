import requests
import json
import re
import csv
import time
import random
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 线程锁用于保护共享数据
data_lock = threading.Lock()


# 读取代理文件
def load_proxies_from_file(file_path):
    """从文件中加载SOCKS5代理"""
    proxies = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('socks5://'):
                    proxies.append(line)
        return proxies
    except FileNotFoundError:
        print(f"代理文件 {file_path} 未找到")
        return []
    except Exception as e:
        print(f"读取代理文件出错: {e}")
        return []

# 随机选择代理
def get_random_proxy(proxies):
    """随机选择一个代理"""
    if not proxies:
        return None
    proxy_url = random.choice(proxies)
    # 解析代理URL
    if proxy_url.startswith('socks5://'):
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    return None


# 页面爬取函数
def crawl_page(page, proxies_list, user_agents, base_url, category, page_size, headers, cookies):
    """爬取单个页面的数据"""
    offset = page * page_size
    print(f"正在爬取第 {page + 1} 页，offset: {offset}")

    # 创建本地副本避免线程间干扰
    local_headers = headers.copy()

    # 随机更换User-Agent
    local_headers["user-agent"] = random.choice(user_agents)

    # 随机延迟，模拟人类行为
    delay = random.uniform(0.5, 1.5)
    print(f"第 {page + 1} 页等待 {delay:.2f} 秒...")
    time.sleep(delay)

    data = {
        "category": category,
        "offset": offset,
        "type": "categoryPost"
    }

    data_json = json.dumps(data, separators=(',', ':'))

    try:
        # 随机选择代理
        proxy = get_random_proxy(proxies_list) if proxies_list else None

        if proxy:
            print(f"第 {page + 1} 页使用代理: {proxy['http']}")
            response = requests.post(
                base_url,
                headers=local_headers,
                cookies=cookies,
                data=data_json,
                timeout=15,
                proxies=proxy
            )
        else:
            response = requests.post(
                base_url,
                headers=local_headers,
                cookies=cookies,
                data=data_json,
                timeout=10
            )

        response.raise_for_status()
        result = response.json()

        # 检查是否有更多数据
        if 'html' not in result or not result['html']:
            print(f"第 {page + 1} 页没有更多数据")
            return page, [], True

        content = result['html']

        # 提取数据
        url_list = re.findall('<a href="(.*?)"', content)
        time_list = re.findall('<p class="ppt-date">(.*?)</p>', content)
        title_list = re.findall('<h2>(.*?)</h2>', content)
        content_list = re.findall('<p class="feature-post-content">(.*?)</p>', content)
        image_list = re.findall("'([^']*?)'\); min-height", content)

        # 处理当前页数据
        page_data = []
        max_items = min(len(url_list), len(time_list), len(title_list), len(content_list), len(image_list))

        for i in range(max_items):
            item_data = {
                'url': url_list[i] if i < len(url_list) else '',
                'time': time_list[i] if i < len(time_list) else '',
                'title': title_list[i] if i < len(title_list) else '',
                'content': content_list[i] if i < len(content_list) else '',
                'image': image_list[i] if i < len(image_list) else ''
            }
            page_data.append(item_data)

        print(f"第 {page + 1} 页爬取完成，获取到 {len(page_data)} 条数据")

        # 如果当前页数据少于页面大小，说明已经到最后一页
        is_last_page = len(page_data) < page_size

        return page, page_data, is_last_page

    except requests.exceptions.Timeout:
        print(f"第 {page + 1} 页请求超时，跳过...")
        return page, [], False
    except requests.exceptions.RequestException as e:
        print(f"第 {page + 1} 页网络请求出错: {e}")
        return page, [], False
    except Exception as e:
        print(f"爬取第 {page + 1} 页时出错: {e}")
        return page, [], False


# 设置请求头和cookie
headers = {

}

cookies = {

}

base_url = "https://african.business/wp-content/themes/IC_Publications/api/get-posts.php"
category = "60"
page_size = 5
max_pages = 100
max_workers = 5  # 最大线程数

# User-Agent池，用于轮换
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2"

]

# 加载代理列表
proxies_list = load_proxies_from_file('ip.txt')
print(f"已加载 {len(proxies_list)} 个代理")

# 存储所有数据
all_data = []

# 使用线程池进行多线程爬取
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交所有任务
    future_to_page = {
        executor.submit(
            crawl_page,
            page,
            proxies_list,
            user_agents,
            base_url,
            category,
            page_size,
            headers,
            cookies
        ): page for page in range(max_pages)
    }

    completed_pages = 0

    # 处理完成的任务
    for future in as_completed(future_to_page):
        page = future_to_page[future]
        try:
            page_num, page_data, is_last_page = future.result()

            # 将数据添加到全局列表中
            with data_lock:
                all_data.extend(page_data)

            completed_pages += 1
            print(f"已完成 {completed_pages} 页")

            # 如果是最后一页，取消剩余未开始的任务
            if is_last_page:
                print("已到达最后一页，取消剩余任务...")
                for f in future_to_page:
                    f.cancel()
                break

        except Exception as e:
            print(f"处理第 {page + 1} 页结果时出错: {e}")

# 按照原始顺序排序数据（可选）
# all_data.sort(key=lambda x: x.get('time', ''))

# 保存为CSV文件
csv_filename = 'african_business.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['url', 'time', 'title', 'content', 'image']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for data_item in all_data:
        writer.writerow(data_item)

print(f"数据爬取完成，共获取 {len(all_data)} 条数据，已保存到 {csv_filename}")


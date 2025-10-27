# African Business 数据爬取工具

## 项目简介

这个项目是一个用于爬取 [African Business](https://african.business/) 网站数据的爬虫工具。它能够通过多线程抓取文章的 URL、发布时间、标题、内容以及图片链接，并将结果保存为 CSV 文件。爬虫支持代理池和随机 User-Agent，能够模拟人类行为进行爬取，避免被封禁。

### 特性：
- **多线程支持**：使用 `ThreadPoolExecutor` 来加速爬取过程。
- **代理池**：从外部文件加载 SOCKS5 代理，通过代理池随机选择代理来进行请求。
- **随机 User-Agent**：每次请求时，随机选择 User-Agent，模拟不同设备访问。
- **CSV 文件输出**：将爬取的数据保存为 CSV 文件，便于后续分析和处理。

---

## 环境要求

- Python 3.x
- 安装依赖库：

```bash
pip install requests
pip install beautifulsoup4
pip install lxml

使用方法
1. 配置代理
创建一个 ip.txt 文件，文件内每行一个 SOCKS5 代理地址。例如：

perl
复制代码
socks5://username:password@ip:port
socks5://username:password@ip2:port2
2. 配置爬取参数
修改 base_url 为你想要爬取的目标网站接口。

设置 category 为你要爬取的内容类别（具体值可以通过观察接口参数确定）。

设置 page_size 和 max_pages 来控制每页的数据量和最大爬取的页数。

设置 max_workers 来控制最大并发线程数。

3. 运行爬虫
在项目根目录下运行脚本：

bash
复制代码
python crawler.py
4. 输出结果
爬虫将会将爬取到的数据保存到 african_business.csv 文件中，文件包含以下字段：

url：文章链接

time：发布时间

title：文章标题

content：文章内容

image：文章中的图片链接

代码结构
crawler.py：爬虫主脚本，负责数据爬取和保存。

ip.txt：包含 SOCKS5 代理列表的文件。

african_business.csv：爬取的数据将保存到此文件。

运行时日志输出
运行时，爬虫会打印当前页数和代理信息，例如：

perl
复制代码
正在爬取第 1 页，offset: 0
第 1 页等待 1.23 秒...
第 1 页使用代理: socks5://username:password@ip:port
第 1 页爬取完成，获取到 5 条数据
注意事项
代理使用：此爬虫支持 SOCKS5 代理池，如果代理文件为空或格式不正确，爬虫将使用默认的直连方式。

反爬机制：爬虫通过设置随机 User-Agent 和模拟人类行为的延时来绕过部分反爬虫机制，但仍可能遇到封禁，具体可根据需求调整延时、代理等设置。

数据量和频率：请根据目标网站的请求限制和规则来调整爬取频率，避免对服务器造成过大压力。

贡献
欢迎提出建议和贡献代码！如果您有任何问题，请在 Issues 区域提出，我们会尽快回复。

许可证
本项目采用 MIT License 许可证，欢迎自由使用和修改。

yaml
复制代码

---

### 项目结构

```bash
.
├── crawler.py            # 爬虫主脚本
├── ip.txt                # 代理列表文件
├── african_business.csv  # 爬取到的结果数据
└── README.md             # 项目使用说明
提示
你可以根据需要修改 base_url 和 category 来爬取不同类型的内容，或调整 page_size 来优化抓取。

代理文件中的每个代理应遵循 socks5:// 方案，你可以通过提供更多代理来提升爬取效率和稳定性。

如果你觉得这些内容合适，可以将其作为项目的 README 文件，并根据具体需求进一步修改。

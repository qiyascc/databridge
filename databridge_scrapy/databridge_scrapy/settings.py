# Scrapy settings for databridge_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "databridge_scrapy"

SPIDER_MODULES = ["databridge_scrapy.databridge_scrapy.spiders"]
NEWSPIDER_MODULE = "databridge_scrapy.databridge_scrapy.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "databridge_scrapy (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16
DOWNLOAD_TIMEOUT = 30

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False


# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "databridge_scrapy.middlewares.Databridge_scrapySpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'databridge_scrapy.databridge_scrapy.middlewares.CustomUserAgentMiddleware': 543,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'databridge_scrapy.databridge_scrapy.middlewares.ProxyMiddleware': 100,
    'databridge_scrapy.databridge_scrapy.middlewares.CustomRetryMiddleware': 541,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,  # Varsayılan retry middleware'i devre dışı bırak
}

ITEM_PIPELINES = {
    'lcwaikiki.pipelines.DjangoPipeline': 800,

}




    
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "databridge_scrapy.pipelines.Databridge_scrapyPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

PROXIES = [
    "zkcqmduo:wg1ks7uapqib@64.137.57.16:6025",
    "zkcqmduo:wg1ks7uapqib@216.173.103.151:6665",
    "zkcqmduo:wg1ks7uapqib@45.38.122.204:7112",
    "zkcqmduo:wg1ks7uapqib@89.42.8.61:5622",
    "zkcqmduo:wg1ks7uapqib@45.43.70.89:6376",
    "zkcqmduo:wg1ks7uapqib@45.92.77.217:6239",
    "zkcqmduo:wg1ks7uapqib@104.239.90.91:6482",
    "zkcqmduo:wg1ks7uapqib@173.239.219.112:6021",
    "zkcqmduo:wg1ks7uapqib@185.245.26.233:6750",
    "zkcqmduo:wg1ks7uapqib@198.46.246.23:6647",
    "zkcqmduo:wg1ks7uapqib@145.223.56.208:7260",
    "zkcqmduo:wg1ks7uapqib@104.239.10.32:5703",
    "zkcqmduo:wg1ks7uapqib@154.92.124.254:5282",
    "zkcqmduo:wg1ks7uapqib@194.32.82.79:6724",
    "zkcqmduo:wg1ks7uapqib@45.117.55.249:6895",
    "zkcqmduo:wg1ks7uapqib@103.76.117.75:6340",
    "zkcqmduo:wg1ks7uapqib@150.107.224.158:6073",
    "zkcqmduo:wg1ks7uapqib@154.203.39.121:5409",
    "zkcqmduo:wg1ks7uapqib@173.244.41.204:6388",
    "zkcqmduo:wg1ks7uapqib@181.214.13.127:5968",
    "zkcqmduo:wg1ks7uapqib@107.172.221.21:5976",
    "zkcqmduo:wg1ks7uapqib@145.223.50.195:6257",
    "zkcqmduo:wg1ks7uapqib@173.211.30.136:6570",
    "zkcqmduo:wg1ks7uapqib@192.154.250.169:5749",
    "zkcqmduo:wg1ks7uapqib@23.94.7.39:5726",
    "zkcqmduo:wg1ks7uapqib@82.24.245.238:8061",
    "zkcqmduo:wg1ks7uapqib@104.168.8.179:5632",
    "zkcqmduo:wg1ks7uapqib@199.180.8.131:5842",
    "zkcqmduo:wg1ks7uapqib@45.131.102.11:5663",
    "zkcqmduo:wg1ks7uapqib@82.22.215.91:7422",
    "zkcqmduo:wg1ks7uapqib@82.27.246.171:7495",
    "zkcqmduo:wg1ks7uapqib@82.29.226.43:7385",
    "zkcqmduo:wg1ks7uapqib@192.95.91.117:5744",
    "zkcqmduo:wg1ks7uapqib@206.41.169.21:5601",
    "zkcqmduo:wg1ks7uapqib@92.113.242.171:6755",
    "zkcqmduo:wg1ks7uapqib@198.105.101.31:5660",
    "zkcqmduo:wg1ks7uapqib@64.137.79.140:6054",
    "zkcqmduo:wg1ks7uapqib@82.23.213.120:6960",
    "zkcqmduo:wg1ks7uapqib@91.212.74.45:6411",
    "zkcqmduo:wg1ks7uapqib@92.112.165.196:6648",
    "zkcqmduo:wg1ks7uapqib@23.26.61.73:5539",
    "zkcqmduo:wg1ks7uapqib@45.61.96.151:6131",
    "zkcqmduo:wg1ks7uapqib@89.213.141.79:6955",
    "zkcqmduo:wg1ks7uapqib@89.213.188.190:6066",
    "zkcqmduo:wg1ks7uapqib@194.113.112.133:6028",
    "zkcqmduo:wg1ks7uapqib@104.238.38.154:6422",
    "zkcqmduo:wg1ks7uapqib@216.74.80.82:6654",
    "zkcqmduo:wg1ks7uapqib@46.202.67.170:6166",
    "zkcqmduo:wg1ks7uapqib@92.112.148.95:6540",
    "zkcqmduo:wg1ks7uapqib@46.202.67.39:6035",
    "zkcqmduo:wg1ks7uapqib@89.43.34.132:6149",
    "zkcqmduo:wg1ks7uapqib@89.45.125.181:5907",
    "zkcqmduo:wg1ks7uapqib@155.254.48.128:6034",
    "zkcqmduo:wg1ks7uapqib@161.123.131.128:5733",
    "zkcqmduo:wg1ks7uapqib@31.58.30.210:6792",
    "zkcqmduo:wg1ks7uapqib@173.211.8.28:6140",
    "zkcqmduo:wg1ks7uapqib@103.114.59.241:7018",
    "zkcqmduo:wg1ks7uapqib@104.238.38.34:6302",
    "zkcqmduo:wg1ks7uapqib@104.252.149.240:5654",
    "zkcqmduo:wg1ks7uapqib@46.202.78.58:5553",
    "zkcqmduo:wg1ks7uapqib@84.33.47.158:7194",
    "zkcqmduo:wg1ks7uapqib@137.59.5.195:6678",
    "zkcqmduo:wg1ks7uapqib@145.223.63.159:6219",
    "zkcqmduo:wg1ks7uapqib@168.199.132.243:6315",
    "zkcqmduo:wg1ks7uapqib@104.239.105.182:6712",
    "zkcqmduo:wg1ks7uapqib@104.252.193.24:5934",
    "zkcqmduo:wg1ks7uapqib@140.99.201.221:6100",
    "zkcqmduo:wg1ks7uapqib@192.95.91.171:5798",
    "zkcqmduo:wg1ks7uapqib@92.112.165.47:6499",
    "zkcqmduo:wg1ks7uapqib@174.140.254.63:6654",
    "zkcqmduo:wg1ks7uapqib@82.27.246.59:7383",
    "zkcqmduo:wg1ks7uapqib@92.112.172.19:6291",
    "zkcqmduo:wg1ks7uapqib@168.199.141.138:5890",
    "zkcqmduo:wg1ks7uapqib@185.171.255.171:6224",
    "zkcqmduo:wg1ks7uapqib@198.105.122.148:6721",
    "zkcqmduo:wg1ks7uapqib@45.43.70.84:6371",
    "zkcqmduo:wg1ks7uapqib@82.23.243.164:7522",
    "zkcqmduo:wg1ks7uapqib@104.239.80.57:5635",
    "zkcqmduo:wg1ks7uapqib@154.92.125.176:5477",
    "zkcqmduo:wg1ks7uapqib@104.239.38.139:6672",
    "zkcqmduo:wg1ks7uapqib@188.215.5.145:5175",
    "zkcqmduo:wg1ks7uapqib@45.61.122.116:6408",
    "zkcqmduo:wg1ks7uapqib@82.24.221.104:5955",
    "zkcqmduo:wg1ks7uapqib@104.222.167.212:6614",
    "zkcqmduo:wg1ks7uapqib@184.174.28.112:5127",
    "zkcqmduo:wg1ks7uapqib@46.203.45.50:6073",
    "zkcqmduo:wg1ks7uapqib@86.38.234.140:6594",
    "zkcqmduo:wg1ks7uapqib@89.43.34.247:6264",
    "zkcqmduo:wg1ks7uapqib@161.123.115.250:5271",
    "zkcqmduo:wg1ks7uapqib@192.95.91.36:5663",
    "zkcqmduo:wg1ks7uapqib@188.68.1.181:6050",
    "zkcqmduo:wg1ks7uapqib@206.127.212.121:6099",
    "zkcqmduo:wg1ks7uapqib@5.154.253.176:8434",
    "zkcqmduo:wg1ks7uapqib@64.137.90.16:5636",
    "zkcqmduo:wg1ks7uapqib@23.129.252.172:6440",
    "zkcqmduo:wg1ks7uapqib@64.137.73.197:5285",
    "zkcqmduo:wg1ks7uapqib@84.33.47.72:7108",
    "zkcqmduo:wg1ks7uapqib@103.99.33.253:6248",
    "zkcqmduo:wg1ks7uapqib@64.43.89.52:6311",
    "zkcqmduo:wg1ks7uapqib@43.245.117.16:5600",
]

# Diğer ayarlar aynı kalacak, sadece pipeline'ları güncelleyin


# Django ayarlarını ekleyin
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databridge_scrapy.settings')
django.setup()
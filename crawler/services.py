import shutil
import tempfile
from httpcore import TimeoutException
import requests
import re
import time
import logging
from datetime import datetime
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, Comment
from django.utils import timezone
from .redis_models import RedisNewsArticle, RedisCrawlTask
from .utils import convert_to_markdown, extract_images, clean_text
from .image_service import image_cache_service

logger = logging.getLogger(__name__)

class PeopleNetCrawler:
    """人民网爬虫服务类"""
    
    def __init__(self):
        self.base_url = "http://www.people.com.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://www.people.com.cn/',
            'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # 允许重定向，但限制次数
        self.session.max_redirects = 3
    
    def crawl_today_news(self, task_id=None):
        """爬取今日要闻 (新版：直接从目标URL获取)"""
        logger.info("开始执行")
        try:
            # 目标URL
            target_url = "http://www.people.com.cn/GB/59476/index.html"
            
            # 更新任务状态
            if task_id:
                task = RedisCrawlTask.get(task_id)
                if task:
                    task.update(status='running', started_at=timezone.now().isoformat())
            
            logger.info(f"开始爬取今日要闻，目标URL: {target_url}")
            
            # 获取新闻链接
            # 获取今日号数
            now = datetime.now()
            news_links = self._get_tody_news_url(target_url,now.day)
            
            if not news_links:
                # 如果获取失败，直接抛出异常，而不是尝试其他策略
                raise Exception(f"无法从目标URL {target_url} 获取任何新闻链接")
            
            logger.info(f"找到 {len(news_links)} 条新闻链接")
            
            if task_id:
                task.update(total_links=len(news_links))
            
            success_count = 0
            failed_count = 0
            
            # 爬取每篇文章的详细内容 (这部分逻辑保持不变)
            for i, link_info in enumerate(news_links):
                try:
                    logger.info(f"正在爬取第 {i+1}/{len(news_links)} 篇文章: {link_info['title']}")
                    
                    article_data = self._crawl_article_detail(link_info)
                    if article_data:
                        self._save_article(article_data)
                        success_count += 1
                        logger.info(f"成功保存文章: {article_data['title']}")
                    else:
                        failed_count += 1
                        logger.warning(f"文章爬取失败: {link_info['title']}")
                    
                    # 更新任务进度
                    if task_id:
                        task.update(success_count=success_count, failed_count=failed_count)
                    
                    # 避免请求过于频繁
                    time.sleep(1)
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"爬取文章时出错: {link_info.get('title', 'Unknown')} - {str(e)}")
                    continue
            
            # 完成任务
            if task_id:
                task.update(
                    status='completed',
                    completed_at=timezone.now().isoformat(),
                    success_count=success_count,
                    failed_count=failed_count
                )
            
            logger.info(f"爬取完成: 成功 {success_count} 篇，失败 {failed_count} 篇")
            
            return {
                'success': True,
                'total': len(news_links),
                'success_count': success_count,
                'failed_count': failed_count,
                'message': '爬取完成'
            }
            
        except Exception as e:
            error_msg = f"爬取今日要闻时出错: {str(e)}"
            logger.error(error_msg)
            
            if task_id:
                task = RedisCrawlTask.get(task_id)
                if task:
                    task.update(
                        status='failed',
                        error_message=error_msg,
                        completed_at=timezone.now().isoformat()
                    )
            
            return {
                'success': False,
                'message': error_msg
            }
    
    def _get_tody_news_url(self, url, target_date):
        """
        爬取今日要闻所有文章的链接（适配两种页面模式）。
        """
        chrome_options = Options()
        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        original_window = driver.current_window_handle
        
        try:
            # 1. 访问初始 URL
            driver.get(url)

            # --- 新增的验证步骤 ---
            # 验证导航是否成功，我们期望 URL 包含 'people.com.cn'
            # 我们给一个合理的等待时间，比如 15 秒
            WebDriverWait(driver, 15).until(
                EC.url_contains("people.com.cn")
            )
            print(f"成功导航到页面，当前 URL: {driver.current_url}")
            # --- 验证结束 ---
            
            print("页面初次加载...")
            
            # --- 核心逻辑：判断页面模式 ---
            try:
                # 尝试执行“模式 A”：寻找并点击 iframe 中的日历
                # 我们给一个较短的等待时间，比如5秒。如果5秒内 iframe 没出现，就认为它不会出现了。
                print("正在尝试检测 iframe 日历模式...")
                iframe = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                )
                driver.switch_to.frame(iframe)
                print("检测到 iframe，已切换。")
                
                print(f"正在查找并点击日期 '{target_date}' 的链接...")
                date_link_xpath = f"//a[font/text()='{target_date}']"
                date_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, date_link_xpath))
                )
                date_link.click()
                print("成功点击日期链接。")

                # 等待并切换到新打开的新闻列表窗口
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break
                print("已成功切换到新闻列表标签页。")

            except TimeoutException:
                # 如果5秒内没有找到 iframe，捕获 TimeoutException 异常
                # 这意味着我们很可能处于“模式 B”：直接进入了新闻列表
                print("未在规定时间内检测到 iframe，假定已直接进入新闻列表页面。")
                # 不需要做任何额外操作，driver 已经停留在正确的页面上

            # --- 通用逻辑：此时无论哪种模式，都应该在新闻列表页了 ---
            print(f"当前所在页面 URL: {driver.current_url}")
            print("等待新闻列表加载...")
            
            # 等待新闻列表的关键元素加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "p6"))
            )
            print("新闻列表页面加载完成！")

            # 2. 获取并解析 HTML 内容
            page_source = driver.page_source
            return self._parse_news_data(page_source) 

        except Exception as e:
            print(f"在爬取过程中发生未知错误: {e}")
            # 保存截图对于调试非常有帮助
            driver.save_screenshot('error_screenshot.png')
            print("已保存错误截图 'error_screenshot.png'")
            return None # 或者重新抛出异常
        finally:
            if 'driver' in locals() and driver:
                driver.quit()
            if 'user_data_dir' in locals() and user_data_dir:
                try:
                    shutil.rmtree(user_data_dir)
                except OSError as e:
                    print(f"清理临时目录失败: {e.strerror}")
    
    def _parse_news_data(self,html_content):
        """
        专门解析人民网历史回顾页面的HTML，提取“新闻排行榜”和“今日要闻”的标题和数据。

        参数:
            html_content (str): 包含新闻列表的完整HTML页面源码。

        返回:
            dict: 一个字典，包含两个键 "news_ranking" 和 "todays_news"，
                它们的值都是一个列表，列表中的每个元素是包含 'title' 和 'url' 的字典。
        """
        if not html_content:
            print("错误：传入的 HTML 内容为空。")
            return {"news_ranking": [], "todays_news": []}

        soup = BeautifulSoup(html_content, 'html.parser')

        # --- 提取“今日要闻” ---
        todays_news_list = []
        # “今日要闻”的数据在 class="p6" 的 <td> 元素中
        news_container = soup.find('td', class_='p6')
        if news_container:
            # 直接在容器内查找所有的 <a> 标签，这样最简单直接
            # 因为一个 <li> 可能包含多个 <br> 分隔的 <a>
            all_links_in_container = news_container.find_all('a')
            for link in all_links_in_container:
                title = link.text.strip()
                url = link.get('href', '').strip()
                if title and url: # 确保标题和链接都有效
                    todays_news_list.append({
                        "title": title,
                        "url": url
                    })

        return todays_news_list
    
    
    def _crawl_article_detail(self, link_info):
        """爬取文章详细内容"""
        try:
            url = link_info['url']
            soup = None
            logger.info(f"开始从这里获取文章：{url}")
            # 尝试从网站获取内容
            try:
                # 创建一个 Options 对象
                chrome_options = Options()
                # 为 driver 实例创建一个唯一的临时目录
                # user_data_dir = tempfile.mkdtemp()
                # chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
                # 添加无头模式参数
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-extensions") # 禁用所有扩展
                chrome_options.add_argument("--disable-infobars") # 禁用信息栏
                chrome_options.add_argument("--disable-popup-blocking") # 禁用弹出窗口拦截
                chrome_options.add_argument("--disable-notifications") # 禁用通知
                chrome_options.add_argument("--disable-logging") # 禁用日志记录
                chrome_options.add_argument("--log-level=3") # 设置日志级别为最高（最少日志）
                chrome_options.add_argument("--silent") # 静默模式
                chrome_options.add_argument("--ignore-certificate-errors") # 忽略证书错误
                chrome_options.add_argument("--disk-cache-size=0") # 禁用磁盘缓存
                chrome_options.add_argument("--media-cache-size=0") # 禁用媒体缓存
                # 初始化webdriver
                driver = webdriver.Chrome(options=chrome_options)
                article_content = None
                # 初始化变量以存储提取的内容
                try:
                    # 1. 发送HTTP请求
                    driver.get(url)
                    # 2. 获取HTML内容
                    page_source = driver.page_source
                    # 3.提取文章结构部分
                    article_content = self._extract_article_content(page_source)
                    
                    if not article_content:
                        raise ValueError("错误：未能通过任何一种方法定位到文章内容。")
                    soup = BeautifulSoup(article_content, 'html.parser')
                
                except Exception as e:
                    print(f"发生错误: {e}")
                finally:
                    driver.quit()
                    
            except Exception as e:
                logger.error(f"无法获取文章网页内容: {link_info['title']} - {str(e)}")
            
            # 如果无法从网站获取内容，跳过这篇文章
            if soup is None:
                logger.warning(f"无法获取文章内容，跳过: {link_info['title']}")
                return None
            
            # 提取文章信息
            # 提取内容和图片映射
            content, image_mapping = self._extract_content(soup)
            
            article_data = {
                'url': url,
                'title': self._extract_title(soup, link_info['title']),
                'source': self._extract_source(soup),
                'publish_date': self._extract_publish_date(soup),
                'content': content,
                'image_mapping': image_mapping,
                'category': self._extract_category(soup, url),
            }
            
            # 转换为Markdown格式
            if article_data['content']:
                article_data['markdown_content'] = convert_to_markdown(
                    article_data['content'], 
                    article_data['title']
                )
                article_data['word_count'] = len(clean_text(article_data['content']))
                article_data['image_count'] = len(extract_images(article_data['content']))
            else:
                return None
            
            return article_data
            
        except Exception as e:
            logger.error(f"爬取文章详情时出错 {link_info['url']}: {str(e)}")
            return None
    
    def _extract_article_content(self,page_source):
        """
        从HTML源码中智能提取主要文章内容的函数。
        它会按顺序尝试多种策略，一旦成功即返回结果。

        参数:
            page_source (str): 网页的HTML源代码。

        返回:
            str: 格式化后的文章内容HTML，如果所有策略都失败则返回None。
        """
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 策略 1: 精确查找 '<!--内容-->' 注释标记。
        # 这种模式下，内容通常在注释标记下方的第一个div的第一个子div中。
        comment_start = soup.find(string=lambda text: isinstance(text, Comment) and text.strip() == '内容')
        if comment_start:
            content_wrapper_div = comment_start.find_next_sibling('div')
            if content_wrapper_div:
                # 提取其第一个子div作为文章主体
                article_div = content_wrapper_div.find('div', recursive=False)
                if article_div:
                    print("信息：通过 '<!--内容-->' (策略1) 成功提取。")
                    return article_div.prettify()

        # 策略 2: 精确查找 '<!--结束正文-->' 注释标记。
        # 这种模式下，文章内容就是注释标记紧邻的前一个div。
        comment_end = soup.find(string=lambda text: isinstance(text, Comment) and text.strip() == '结束正文')
        if comment_end:
            # 提取紧邻的前一个兄弟div作为文章主体
            article_div = comment_end.find_previous_sibling('div')
            if article_div:
                print("信息：通过 '<!--结束正文-->' (策略2) 成功提取。")
                return article_div.prettify()

        # 如果两种策略都失败，返回None
        print("警告：所有提取策略均失败，未能定位到文章内容。")
        return None
    
    def _extract_title(self, soup, fallback_title):
        """提取文章标题"""
        # 尝试多种选择器
        selectors = [
            'h1',
            '.rm_txt_con h1',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and not title.endswith('--人民网'):
                    return title.replace('--人民网', '').replace('--文旅·体育--人民网', '').replace('--经济·科技--人民网', '').strip()
        
        return fallback_title
    
    def _extract_source(self, soup):
        """提取文章来源"""
        # 查找来源信息
        source_patterns = [
            r'来源：(.+?)(?:\s|$)',
            r'来源:<a[^>]*>([^<]+)</a>',
        ]
        
        # 先尝试从特定元素中提取
        source_elements = soup.select('.channel .col-1-1, .source')
        for element in source_elements:
            text = element.get_text()
            for pattern in source_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()
        
        # 默认来源
        return "人民网"
    
    def _extract_publish_date(self, soup):
        """提取发布时间"""
        try:
            # 查找时间信息
            date_patterns = [
                r'(\d{4}年\d{1,2}月\d{1,2}日\d{1,2}:\d{1,2})',
                r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2})',
                r'(\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2})',
            ]
            
            # 从页面文本中查找
            page_text = soup.get_text()
            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    date_str = match.group(1)
                    # 解析日期
                    return self._parse_date_string(date_str)
            
            # 如果找不到，使用当前时间
            return timezone.now()
            
        except Exception as e:
            logger.warning(f"提取发布时间失败: {str(e)}")
            return timezone.now()
    
    def _parse_date_string(self, date_str):
        """解析日期字符串"""
        try:
            # 处理中文日期格式
            if '年' in date_str and '月' in date_str and '日' in date_str:
                # 2025年09月01日06:56
                date_str = re.sub(r'年|月', '-', date_str).replace('日', ' ')
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            
            # 处理其他格式
            formats = [
                '%Y-%m-%d %H:%M',
                '%Y/%m/%d %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return timezone.now()
            
        except Exception:
            return timezone.now()
    
    def _extract_content(self, soup):
        """提取文章正文内容"""
        try:
            # 查找正文容器
            content_selectors = [
                '.main',
                '.rm_txt_con',
                '.content',
                '.article-content',
                '#content',
                '.article-body',
                '.post-content',
                '.entry-content'
            ]
            
            content_element = None
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content_element = element
                    break
            
            if not content_element:
                # 如果没找到内容，尝试更通用的方法
                # 查找包含大量文本的元素
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    if len(text) > 500:  # 至少500个字符
                        # 检查是否包含文章内容的关键词
                        if any(keyword in text for keyword in ['习近平', '中国', '发展', '经济', '政治', '社会', '建设', '改革']):
                            content_element = div
                            break
                
                if not content_element:
                    return "", {}
            
            # 移除不需要的元素
            for unwanted in content_element.select('.edit, .paper_num, .share, .ad, script, style'):
                unwanted.decompose()
            
            # 使用更简单的方法：将HTML转换为文本，同时保留图片标记
            content_parts = []
            
            # 先将所有img标签替换为特殊标记
            img_placeholders = {}
            image_mapping = {}
            img_counter = 0
            
            for img in content_element.find_all('img'):
                src = img.get('src')
                alt = img.get('alt', '')
                if src:
                    if not src.startswith('http'):
                        src = urljoin(self.base_url, src)
                    if not alt:
                        alt = "图片"
                    
                    placeholder = f"__IMAGE_PLACEHOLDER_{img_counter}__"
                    
                    # 下载并缓存图片
                    # 如果是本地文件的相对路径，尝试转换为可用的URL
                    if src.startswith('./') and '_files/' in src:
                        filename = src.split('/')[-1]  # 获取文件名
                        constructed_url = None
                        
                        # 尝试多种URL构造模式
                        if filename.startswith('MAIN'):
                            # 模式1: MAIN开头的文件，通常是NMediaFile路径
                            constructed_url = f"http://www.people.com.cn/NMediaFile/2022/0801/{filename}"
                        elif filename.isdigit() or len(filename.split('.')[0]) > 10:
                            # 模式2: 纯数字或长文件名，通常是mediafile/pic路径
                            constructed_url = f"http://www.people.com.cn/mediafile/pic/BIG/20250901/{filename}"
                        else:
                            # 模式3: 其他文件，尝试paper.people.com.cn路径
                            constructed_url = f"http://paper.people.com.cn/rmrb/pc/pic/202509/01/{filename}"
                        
                        logger.debug(f"本地相对路径转换: {src} -> {constructed_url}")
                        try:
                            image_id, content_type = image_cache_service.download_and_cache_image(constructed_url, self.base_url)
                        except Exception as e:
                            logger.warning(f"图片下载失败: {constructed_url} - {str(e)}")
                            image_id, content_type = None, None
                        
                        # 如果第一次尝试失败，尝试其他模式
                        if not image_id and filename.startswith('MAIN'):
                            # 尝试直接使用原始路径构造
                            alt_url = f"http://www.people.com.cn/mediafile/pic/{filename}"
                            logger.debug(f"尝试备选路径: {alt_url}")
                            try:
                                image_id, content_type = image_cache_service.download_and_cache_image(alt_url, self.base_url)
                            except Exception as e:
                                logger.warning(f"备选图片下载失败: {alt_url} - {str(e)}")
                                image_id, content_type = None, None
                            
                    else:
                        try:
                            image_id, content_type = image_cache_service.download_and_cache_image(src, self.base_url)
                        except Exception as e:
                            logger.warning(f"图片下载失败: {src} - {str(e)}")
                            image_id, content_type = None, None
                    
                    if image_id:
                        # 使用缓存的图片ID
                        img_placeholders[placeholder] = f"![{alt}](/api/crawler/image/{image_id}/)"
                        image_mapping[src] = {
                            'image_id': image_id,
                            'alt': alt,
                            'content_type': content_type
                        }
                        logger.debug(f"图片缓存成功: {alt} -> {image_id}")
                    else:
                        # 如果缓存失败，使用原链接
                        img_placeholders[placeholder] = f"![{alt}]({src})"
                        logger.warning(f"图片缓存失败，使用原链接: {src}")
                    
                    # 用占位符替换img标签
                    img.replace_with(placeholder)
                    img_counter += 1
            
            # 获取所有文本内容，包括占位符
            full_text = content_element.get_text()
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            content_parts = [line for line in lines if len(line) > 5]
            
            # 将所有内容连接，然后替换图片占位符
            full_content = '\n\n'.join(content_parts)
            
            # 替换图片占位符
            for placeholder, img_markdown in img_placeholders.items():
                full_content = full_content.replace(placeholder, f'\n\n{img_markdown}\n\n')
            
            return full_content.strip(), image_mapping
            
        except Exception as e:
            logger.error(f"提取文章内容时出错: {str(e)}")
            return "", {}
    
    def _extract_category(self, soup, url):
        """提取文章分类"""
        try:
            # 从URL路径推断分类
            if '/finance/' in url:
                return "经济·科技"
            elif '/ent/' in url:
                return "文旅·体育"
            elif '/society/' in url:
                return "社会·法治"
            elif '/world/' in url:
                return "国际"
            elif '/politics/' in url:
                return "时政"
            elif '/military/' in url:
                return "军事"
            elif '/health/' in url:
                return "健康·生活"
            elif '/edu/' in url:
                return "教育"
            
            # 从页面导航中提取
            nav_elements = soup.select('.route a, .breadcrumb a')
            for nav in nav_elements:
                nav_text = nav.get_text(strip=True)
                if nav_text in ["经济·科技", "文旅·体育", "社会·法治", "国际", "时政", "军事", "健康·生活", "教育"]:
                    return nav_text
            
            return "综合"
            
        except Exception:
            return "综合"
    
    def _save_article(self, article_data):
        """保存文章到Redis"""
        try:
            # 创建Redis文章实例
            article = RedisNewsArticle(
                title=article_data['title'],
                url=article_data['url'],
                source=article_data['source'],
                publish_date=article_data['publish_date'],
                content=article_data['content'],
                markdown_content=article_data['markdown_content'],
                category=article_data['category'],
                word_count=article_data['word_count'],
                image_count=article_data['image_count'],
                image_mapping=article_data.get('image_mapping', {}),
                crawl_status='success'
            )
            
            if article.save():
                logger.info(f"保存新文章: {article.title}")
            else:
                logger.error(f"保存文章失败: {article.title}")
                raise Exception(f"保存文章失败: {article.title}")
            
        except Exception as e:
            logger.error(f"保存文章时出错: {str(e)}")
            raise

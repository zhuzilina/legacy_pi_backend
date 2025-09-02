import re
import html
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def clean_text(text):
    """清理文本内容"""
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 解码HTML实体
    text = html.unescape(text)
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除特殊字符
    text = re.sub(r'[\r\n\t]+', ' ', text)
    
    return text.strip()

def convert_to_markdown(content, title=""):
    """将内容转换为Markdown格式"""
    if not content:
        return ""
    
    markdown_lines = []
    
    # 添加标题
    if title:
        markdown_lines.append(f"# {title}\n")
    
    # 按段落分割内容
    paragraphs = content.split('\n\n')
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # 检查是否是图片
        if paragraph.startswith('![') and paragraph.endswith(')'):
            markdown_lines.append(paragraph)
            markdown_lines.append("")  # 图片后加空行
        else:
            # 普通段落
            # 清理段落内容
            clean_paragraph = clean_text(paragraph)
            if clean_paragraph:
                # 处理段落缩进
                if clean_paragraph.startswith('　　'):
                    clean_paragraph = clean_paragraph[2:]  # 移除中文缩进
                
                markdown_lines.append(clean_paragraph)
                markdown_lines.append("")  # 段落后加空行
    
    return '\n'.join(markdown_lines).strip()

def extract_images(content):
    """提取内容中的图片链接"""
    if not content:
        return []
    
    images = []
    
    # 提取Markdown格式的图片
    markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
    for alt, src in markdown_images:
        images.append({
            'src': src,
            'alt': alt
        })
    
    # 提取HTML格式的图片
    soup = BeautifulSoup(content, 'html.parser')
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src')
        alt = img.get('alt', '')
        if src:
            images.append({
                'src': src,
                'alt': alt
            })
    
    return images

def format_date_chinese(date_str):
    """格式化中文日期"""
    try:
        # 处理各种中文日期格式
        patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2}):(\d{1,2})', r'\1-\2-\3 \4:\5'),
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', r'\1-\2-\3'),
        ]
        
        for pattern, replacement in patterns:
            if re.match(pattern, date_str):
                return re.sub(pattern, replacement, date_str)
        
        return date_str
    except Exception:
        return date_str

def extract_text_from_html(html_content):
    """从HTML中提取纯文本"""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除脚本和样式
    for script in soup(["script", "style"]):
        script.decompose()
    
    # 获取文本
    text = soup.get_text()
    
    # 清理文本
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def is_valid_news_url(url):
    """检查是否是有效的新闻URL"""
    if not url:
        return False
    
    # 检查是否是人民网链接
    if 'people.com.cn' not in url:
        return False
    
    # 检查是否是新闻文章链接
    if '/n1/' not in url:
        return False
    
    # 排除某些不需要的链接
    exclude_patterns = [
        r'/img/',
        r'/css/',
        r'/js/',
        r'\.jpg$',
        r'\.png$',
        r'\.gif$',
        r'\.pdf$',
        r'/search/',
        r'/index\.html$',
    ]
    
    for pattern in exclude_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    
    return True

def normalize_url(url, base_url="http://www.people.com.cn"):
    """规范化URL"""
    if not url:
        return ""
    
    # 如果是完整URL，直接返回
    if url.startswith('http'):
        return url
    
    # 处理相对URL
    if url.startswith('//'):
        return 'http:' + url
    elif url.startswith('/'):
        return base_url + url
    else:
        return urljoin(base_url, url)

def extract_summary(content, max_length=200):
    """提取文章摘要"""
    if not content:
        return ""
    
    # 清理内容
    clean_content = clean_text(content)
    
    # 按句号分割
    sentences = re.split(r'[。！？]', clean_content)
    
    summary = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if len(summary + sentence) <= max_length:
            summary += sentence + "。"
        else:
            break
    
    return summary.strip()

def validate_article_data(article_data):
    """验证文章数据的完整性"""
    required_fields = ['title', 'url', 'content', 'source', 'publish_date']
    
    for field in required_fields:
        if not article_data.get(field):
            return False, f"缺少必要字段: {field}"
    
    # 检查标题长度
    if len(article_data['title']) < 5:
        return False, "标题过短"
    
    # 检查内容长度
    if len(article_data['content']) < 50:
        return False, "内容过短"
    
    # 检查URL格式
    if not is_valid_news_url(article_data['url']):
        return False, "无效的新闻URL"
    
    return True, "验证通过"

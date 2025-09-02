# 人民网爬虫API文档

## 概述

本API提供人民网"今日要闻"内容的自动爬取和获取服务。系统采用被动触发机制，仅在每日首次请求时启动爬取任务，并将结果缓存在Redis中。

**基础URL**: `http://127.0.0.1:8000/api/crawler/`

### 跨域访问支持

API已配置CORS（跨域资源共享）支持，允许前端应用从不同域名访问：

- ✅ 支持常见前端开发服务器端口（3000, 8080, 5173等）
- ✅ 允许所有HTTP方法（GET, POST, PUT, DELETE等）
- ✅ 支持自定义请求头
- ✅ 允许携带认证信息

**注意**: 生产环境下建议配置具体的允许域名列表，而不是允许所有来源。

### 内容格式优化

- ✅ **段落格式保留**: 自动识别并保留原文的段落结构，每个段落用双换行分隔
- ✅ **图片位置准确**: 图片按原文位置正确插入，不会集中在文末
- ✅ **Markdown格式**: 输出标准Markdown格式，支持图片、标题、列表等
- ✅ **智能分割**: 基于全角空格和句号智能识别段落边界

---

## API端点

### 1. 获取每日文章列表

**端点**: `GET /api/crawler/daily/`

**描述**: 获取当日所有爬取的文章ID列表。如果是当日首次请求，将自动触发爬取任务。

#### 请求示例
```bash
curl -X GET "http://127.0.0.1:8000/api/crawler/daily/"
```

#### 响应格式

##### 成功响应（已缓存）
```json
{
  "msg": "success",
  "crawl_date": "2025-09-01",
  "total_articles": 13,
  "article_ids": [
    "article_1756695929848",
    "article_1756695931028",
    "article_1756695928626",
    "article_1756695936008",
    "article_1756695941088",
    "article_1756695938522",
    "article_1756695940005",
    "article_1756695933577",
    "article_1756695927480",
    "article_1756695926312",
    "article_1756695937202",
    "article_1756695932295",
    "article_1756695934772"
  ],
  "status": "cached"
}
```

##### 爬取中响应
```json
{
  "msg": "crawling_started",
  "crawl_date": "2025-09-01",
  "task_id": "task_1756696594478",
  "status": "crawling",
  "message": "爬取任务已启动，请稍后再次请求获取结果"
}
```

##### 爬取失败响应
```json
{
  "msg": "error",
  "crawl_date": "2025-09-01",
  "error": "无法获取页面内容: 网站无法访问",
  "status": "failed"
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `msg` | string | 响应状态：`success`、`crawling_started`、`error` |
| `crawl_date` | string | 爬取日期 (YYYY-MM-DD) |
| `total_articles` | integer | 成功爬取的文章总数 |
| `article_ids` | array | 文章ID列表 |
| `status` | string | 任务状态：`cached`、`crawling`、`failed` |
| `task_id` | string | 爬取任务ID（仅在爬取中时返回） |
| `message` | string | 状态消息 |
| `error` | string | 错误信息（仅在失败时返回） |

---

### 2. 获取文章内容

**端点**: `GET /api/crawler/article/{article_id}/`

**描述**: 根据文章ID获取完整的Markdown格式文章内容。

#### 请求参数

| 参数 | 类型 | 位置 | 必需 | 描述 |
|------|------|------|------|------|
| `article_id` | string | URL路径 | 是 | 文章唯一标识符 |

#### 请求示例
```bash
curl -X GET "http://127.0.0.1:8000/api/crawler/article/article_1756695932295/"
```

#### 响应格式

##### 成功响应
```markdown
# 人形机器人,更快更高更强

**来源**: 人民网－人民日报222  
**发布时间**: 2025年09月01日 06:00  
**分类**: 经济·科技  
**字数**: 3521  
**原文链接**: [http://finance.people.com.cn/n1/2025/0901/c1004-40553854.html](http://finance.people.com.cn/n1/2025/0901/c1004-40553854.html)

---

# 人形机器人,更快更高更强

![图片](/api/crawler/image/9931dc94fe617acd058657a6ec771d81/)

图①：轮式人形机器人Cruzr S2与无人物流车赤兔协同作业。 图②：优必选推出的智能教育机器人悟空...

近日，世界人形机器人运动会"百米飞人"决赛鸣枪开跑...

---

*本文由人民网爬虫系统自动采集整理*  
*采集时间: 2025-09-01 03:05:32*
```

##### 错误响应
```
HTTP 404 Not Found
文章不存在或已过期
```

#### 内容格式说明

- **标题**: 使用 `#` 标记的主标题
- **元信息**: 包含来源、发布时间、分类、字数、原文链接
- **正文**: Markdown格式的文章内容
- **图片**: 使用 `![alt](/api/crawler/image/{image_id}/)` 格式
- **底部信息**: 采集时间等系统信息

---

### 3. 获取缓存图片

**端点**: `GET /api/crawler/image/{image_id}/`

**描述**: 获取缓存的图片文件。

#### 请求参数

| 参数 | 类型 | 位置 | 必需 | 描述 |
|------|------|------|------|------|
| `image_id` | string | URL路径 | 是 | 图片唯一标识符 |

#### 请求示例
```bash
curl -X GET "http://127.0.0.1:8000/api/crawler/image/9931dc94fe617acd058657a6ec771d81/"
```

#### 响应格式

##### 成功响应
- **Content-Type**: `image/jpeg`、`image/png`、`image/gif` 或 `image/webp`
- **Cache-Control**: `public, max-age=86400`
- **Content-Disposition**: `inline; filename="{image_id}"`
- **Body**: 二进制图片数据

##### 错误响应
```
HTTP 404 Not Found
图片不存在
```

---

## 状态查询API

### 获取爬取状态

**端点**: `GET /api/crawler/status/`

**描述**: 获取当前爬取任务的详细状态信息。

#### 请求示例
```bash
curl -X GET "http://127.0.0.1:8000/api/crawler/status/"
```

#### 响应示例
```json
{
  "msg": "success",
  "date": "2025-09-01",
  "task_status": "completed",
  "articles_count": 13,
  "task_info": {
    "task_id": "task_1756695926009",
    "status": "completed",
    "total_links": 13,
    "success_count": 8,
    "failed_count": 5,
    "started_at": "2025-09-01T03:00:26.009000+00:00",
    "completed_at": "2025-09-01T03:05:45.123000+00:00"
  },
  "cache_info": {
    "total_images": 12,
    "cache_size_mb": 2.3
  }
}
```

---

## 使用指南

### 前端调用流程

#### 跨域请求配置

```javascript
// 基础配置
const API_BASE_URL = 'http://127.0.0.1:8000/api/crawler';

// 带跨域支持的fetch请求
const fetchWithCORS = async (url, options = {}) => {
  return await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    mode: 'cors', // 启用CORS
    credentials: 'include', // 包含凭证（如需要）
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
};
```

1. **获取文章列表**
   ```javascript
   // 获取今日文章列表（跨域）
   const response = await fetchWithCORS('/daily/');
   const data = await response.json();
   
   if (data.msg === 'success') {
     // 处理文章ID列表
     console.log(`共有 ${data.total_articles} 篇文章`);
     data.article_ids.forEach(id => {
       // 处理每个文章ID
     });
   } else if (data.msg === 'crawling_started') {
     // 显示加载状态，稍后重试
     setTimeout(() => fetchDaily(), 30000); // 30秒后重试
   }
   ```

2. **获取文章内容**
   ```javascript
   // 获取特定文章内容（跨域）
   const articleId = 'article_1756695932295';
   const response = await fetchWithCORS(`/article/${articleId}/`);
   
   if (response.ok) {
     const markdown = await response.text();
     // 渲染Markdown内容
     renderMarkdown(markdown);
   } else {
     console.error('文章不存在');
   }
   ```

3. **处理图片**
   ```javascript
   // 图片URL格式（跨域）
   const imageId = '9931dc94fe617acd058657a6ec771d81';
   const imageUrl = `${API_BASE_URL}/image/${imageId}/`;
   
   // 在HTML中使用
   const imgElement = document.createElement('img');
   imgElement.src = imageUrl;
   imgElement.crossOrigin = 'anonymous'; // 如果需要跨域访问图片
   ```

### 错误处理

```javascript
async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetchWithCORS(url, options);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    } else {
      return await response.text();
    }
  } catch (error) {
    console.error('请求失败:', error);
    // 处理网络错误或服务器错误
    return null;
  }
}
```

### 完整的前端示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>人民网爬虫API测试</title>
</head>
<body>
    <div id="app">
        <button onclick="loadArticles()">加载文章列表</button>
        <div id="articles"></div>
    </div>

    <script>
        const API_BASE_URL = 'http://127.0.0.1:8000/api/crawler';
        
        const fetchWithCORS = async (url, options = {}) => {
          return await fetch(`${API_BASE_URL}${url}`, {
            ...options,
            mode: 'cors',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              ...options.headers,
            },
          });
        };

        async function loadArticles() {
            try {
                const response = await fetchWithCORS('/daily/');
                const data = await response.json();
                
                if (data.msg === 'success') {
                    displayArticles(data.article_ids);
                } else if (data.msg === 'crawling_started') {
                    document.getElementById('articles').innerHTML = 
                        '<p>正在爬取中，请稍后...</p>';
                    setTimeout(loadArticles, 30000);
                }
            } catch (error) {
                console.error('加载失败:', error);
                document.getElementById('articles').innerHTML = 
                    '<p>加载失败，请检查网络连接</p>';
            }
        }

        async function displayArticles(articleIds) {
            const container = document.getElementById('articles');
            container.innerHTML = '<p>加载文章内容中...</p>';
            
            const articlesHtml = [];
            for (const id of articleIds.slice(0, 3)) { // 只显示前3篇
                try {
                    const response = await fetchWithCORS(`/article/${id}/`);
                    if (response.ok) {
                        const markdown = await response.text();
                        articlesHtml.push(`
                            <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
                                <h3>文章ID: ${id}</h3>
                                <pre style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">
                                    ${markdown.substring(0, 500)}...
                                </pre>
                            </div>
                        `);
                    }
                } catch (error) {
                    console.error(`加载文章 ${id} 失败:`, error);
                }
            }
            
            container.innerHTML = articlesHtml.join('');
        }
    </script>
</body>
</html>
```

### 缓存策略

- **文章数据**: 每日缓存，次日自动清理
- **图片数据**: 缓存7天
- **首次请求**: 可能需要等待30-60秒完成爬取
- **后续请求**: 从缓存中快速返回

### 限制说明

1. **请求频率**: 建议间隔至少1秒
2. **并发限制**: 建议同时最多5个请求
3. **数据更新**: 每日仅在首次请求时更新
4. **图片大小**: 单张图片最大5MB
5. **网络依赖**: 需要能访问人民网

---

## 响应码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 技术栈

- **后端**: Django + Redis
- **爬虫**: BeautifulSoup4 + Requests
- **缓存**: Redis容器化部署
- **图片处理**: Pillow + Base64编码
- **数据格式**: JSON + Markdown

---

## 联系信息

如有问题或建议，请联系开发团队。

**版本**: v1.0  
**更新时间**: 2025-09-01

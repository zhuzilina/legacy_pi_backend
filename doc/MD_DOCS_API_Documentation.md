# MD文档管理系统API文档

## 概述

本API提供MD文档的获取服务，支持按照类别（精神、人物、党史）获取文档列表和内容。系统采用数据库存储，支持图片文件管理。

**基础URL**: `http://127.0.0.1:8000/api/md-docs/`

### 跨域访问支持

API已配置CORS（跨域资源共享）支持，允许前端应用从不同域名访问：

- ✅ 支持常见前端开发服务器端口（3000, 8080, 5173等）
- ✅ 允许所有HTTP方法（GET, POST, PUT, DELETE等）
- ✅ 支持自定义请求头
- ✅ 允许携带认证信息

**注意**: 生产环境下建议配置具体的允许域名列表，而不是允许所有来源。

### 内容格式说明

- ✅ **Markdown格式**: 输出标准Markdown格式，支持图片、标题、列表等
- ✅ **图片处理**: 图片自动上传并转换为服务器路径
- ✅ **分类管理**: 支持精神、人物、党史三个类别
- ✅ **元数据完整**: 包含作者、来源、发布时间等完整信息

---

## API端点

### 1. 获取文档ID列表

**端点**: `GET /api/md-docs/category/`

**描述**: 根据类别获取MD文档ID列表，接口格式与crawler应用保持一致。

#### 请求参数

| 参数 | 类型 | 位置 | 必需 | 描述 |
|------|------|------|------|------|
| `category` | string | Query | 否 | 文档类别：`spirit`(精神)、`person`(人物)、`party_history`(党史) |

#### 请求示例
```bash
# 获取所有文档ID
curl -X GET "http://127.0.0.1:8000/api/md-docs/category/"

# 获取精神类别的文档ID
curl -X GET "http://127.0.0.1:8000/api/md-docs/category/?category=spirit"

# 获取人物类别的文档ID
curl -X GET "http://127.0.0.1:8000/api/md-docs/category/?category=person"
```

#### 响应格式

##### 成功响应
```json
{
  "msg": "success",
  "crawl_date": "2025-09-04",
  "total_articles": 6,
  "article_ids": [
    "f5c904a1-fe48-4088-86b7-55d7beced545",
    "bcdc6ea3-6efa-40ad-b07a-9e6b6545f9b3",
    "e9b5a2ee-686a-488d-a32b-8e330eb9ff03"
  ],
  "status": "cached"
}
```

##### 错误响应
```json
{
  "msg": "error",
  "error": "无效的类别: invalid_category。有效类别: spirit, person, party_history"
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `msg` | string | 响应状态：`success`、`error` |
| `crawl_date` | string | 查询日期 (YYYY-MM-DD) |
| `total_articles` | integer | 文档总数 |
| `article_ids` | array | 文档ID列表 |
| `status` | string | 状态：`cached` |

---

### 2. 获取文档内容

**端点**: `GET /api/md-docs/document/{document_id}/`

**描述**: 根据文档ID获取完整的Markdown格式文档内容，直接返回用户上传的原始MD内容，包含用户手动编写的元数据。

#### 请求参数

| 参数 | 类型 | 位置 | 必需 | 描述 |
|------|------|------|------|------|
| `document_id` | string | URL路径 | 是 | 文档唯一标识符 |

#### 请求示例
```bash
curl -X GET "http://127.0.0.1:8000/api/md-docs/document/f5c904a1-fe48-4088-86b7-55d7beced545/"
```

#### 响应格式

##### 成功响应
```markdown
# 走进以抗战先烈名字命名的街道:以英雄之名守护万里山河

**来源**: 人民网－人民日报海外版222  
**发布时间**: 2025年09月04日 07:50  
**分类**: 社会·法治  
**字数**: 3027  
**原文链接**: [http://society.people.com.cn/n1/2025/0904/c1008-40556608.html](http://society.people.com.cn/n1/2025/0904/c1008-40556608.html)

---

# 走进以抗战先烈名字命名的街道:以英雄之名守护万里山河

![图片](/api/md-docs/image/84e27e8e21e078d89c164f05ef586618/)

图①：赵登禹路。 图②：位于张自忠路地铁站的张自忠胸像。 图③：位于佟麟阁路北口的怀表雕塑。 图④：人们在黑龙江省哈尔滨市一曼街上行走。 新华社记者 谢剑飞摄 本文照片除署名外均为本报记者严 冰摄 潘旭涛制图 在北京，张自忠路、佟麟阁路、赵登禹路，以英雄之名见证着城市的脉动；在黑龙江哈尔滨，一曼街回荡着巾帼英魂的不屈呐喊；在四川芦山，乐以琴路承载着"空中赵子龙"的忠勇传奇；在山西，左权县铭记着八路军高级将领的赤胆忠心……一个个闪耀着英雄光辉的名字，被写在祖国的广阔山河，刻进城市的街巷，融入人们的生活。

近日，笔者走进北京的街头巷尾，从庄严肃穆的张自忠将军像，到承载历史记忆的佟麟阁铜质怀表雕塑，循着英雄之名，找寻大街小巷中的历史印记。

"为国家民族死之决心，海不清，石不烂，决不半点改变！"这是张自忠将军留下的铮铮誓言。多年过去，声音穿过岁月，这句话依旧回响在大街小巷，记在人们的心里。

笔者搭乘北京市地铁五号线，一路来到张自忠路站。站台里，矗立着一座张自忠胸像：张自忠将军一身戎装，神情坚毅，下方刻着他的生卒年份：1891年至1940年。张自忠，曾先后参加过徐州会战、武汉会战等战役，在枣宜会战中壮烈牺牲，是第二次世界大战反法西斯阵营中牺牲的军衔最高将领。周恩来曾评价他："其忠义之志，壮烈之气，直可以为中国抗战军人之魂。"

走出地铁口，眼前便是张自忠路。东西走向，全长700余米。这条路过去叫"铁狮子胡同"，曾是张自忠所在的国民革命军第29军的驻地。新中国成立后，这条路三次拓宽改建，如今属于平安大街的一部分，宽阔整洁，车水马龙。

街边的咖啡馆传来轻快的音乐，老人们搬来椅子在树下闲话家常，孩子们穿梭在胡同里嬉戏玩耍，也有游客慕名而来，驻足观看。

"你知道张自忠是谁吗？"一位游客指着路牌上的名字问道。"民族英雄！老师和我们讲过他的故事。"旁边一名学生脱口而出，"他说过：'今天有我无敌，有敌无我，一定要血战到底！'"学生的语气中充满了崇敬。

"这条路承载了太多历史。"附近的居民告诉笔者，"逢年过节，总会有人带着鲜花，敬献到张自忠雕像前。我们走在这条路上，心里都会多一份敬意。这条路，是以英雄名字命名的路，更是让我们牢记抗战精神的路。"

英雄的名字闪耀在大街小巷，历史在街头巷尾沉淀成记忆，在寻常生活里生长出力量。张自忠路，既是一条城市的道路，也是一条连接历史与当下的纽带，传承着先烈的精神，也见证着城市的发展。

[文档内容继续...]
```

##### 错误响应
```
HTTP 404 Not Found
文档不存在
```

#### 内容格式说明

- **原始内容**: 直接返回用户上传的原始MD内容
- **用户元数据**: 包含用户手动编写的来源、发布时间、分类等信息
- **图片路径**: 使用 `![alt](/api/md-docs/image/{image_id}/)` 格式，已在上传时处理
- **完整格式**: 保持用户原始文档的完整格式和结构

---

### 3. 获取文档图片

**端点**: `GET /api/md-docs/image/{image_id}/`

**描述**: 获取文档中的图片文件。

#### 请求参数

| 参数 | 类型 | 位置 | 必需 | 描述 |
|------|------|------|------|------|
| `image_id` | string | URL路径 | 是 | 图片唯一标识符 |

#### 请求示例
```bash
curl -X GET "http://127.0.0.1:8000/api/md-docs/image/db24ee66-86bb-46a6-8388-308ba4f50eaf/"
```

#### 响应格式

##### 成功响应
- **Content-Type**: `image/jpeg`、`image/png`、`image/gif` 或 `image/webp`
- **Cache-Control**: `public, max-age=86400`
- **Content-Disposition**: `inline; filename="{original_filename}"`
- **Body**: 二进制图片数据

##### 错误响应
```
HTTP 404 Not Found
图片不存在
```

---

## 状态查询API

### 获取系统状态

**端点**: `GET /api/md-docs/status/`

**描述**: 获取MD文档系统的详细状态信息。

#### 请求示例
```bash
curl -X GET "http://127.0.0.1:8000/api/md-docs/status/"
```

#### 响应示例
```json
{
  "msg": "success",
  "total_documents": 3,
  "category_stats": {
    "spirit": 1,
    "person": 2,
    "party_history": 1
  },
  "recent_update": "2025-09-04T10:54:09.032523+00:00",
  "system_status": "running"
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `msg` | string | 响应状态：`success` |
| `total_documents` | integer | 文档总数 |
| `category_stats` | object | 各类别文档统计 |
| `category_stats.spirit` | integer | 精神类别文档数量 |
| `category_stats.person` | integer | 人物类别文档数量 |
| `category_stats.party_history` | integer | 党史类别文档数量 |
| `recent_update` | string | 最近更新时间 (ISO格式) |
| `system_status` | string | 系统状态：`running` |

---

## 使用指南

### 前端调用流程

#### 跨域请求配置

```javascript
// 基础配置
const API_BASE_URL = 'http://127.0.0.1:8000/api/md-docs';

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

1. **获取文档ID列表**
   ```javascript
   // 获取精神类别的文档ID列表（跨域）
   const response = await fetchWithCORS('/category/?category=spirit');
   const data = await response.json();
   
   if (data.msg === 'success') {
     // 处理文档ID列表
     console.log(`共有 ${data.total_articles} 个文档`);
     data.article_ids.forEach(docId => {
       console.log(`文档ID: ${docId}`);
     });
   }
   ```

2. **获取文档内容**
   ```javascript
   // 获取特定文档内容（跨域）
   const documentId = '3d1f27fa-69e0-48ee-bbec-631caa084545';
   const response = await fetchWithCORS(`/document/${documentId}/`);
   
   if (response.ok) {
     const markdown = await response.text();
     // 渲染Markdown内容
     renderMarkdown(markdown);
   } else {
     console.error('文档不存在');
   }
   ```

3. **处理图片**
   ```javascript
   // 图片URL格式（跨域）
   const imageId = 'db24ee66-86bb-46a6-8388-308ba4f50eaf';
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
    <title>MD文档API测试</title>
    <style>
        .document-item {
            border: 1px solid #ccc;
            margin: 10px;
            padding: 15px;
            border-radius: 5px;
        }
        .document-content {
            max-height: 400px;
            overflow-y: auto;
            background: #f9f9f9;
            padding: 10px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div id="app">
        <h1>MD文档管理系统</h1>
        <div>
            <button onclick="loadDocuments('spirit')">精神类文档</button>
            <button onclick="loadDocuments('person')">人物类文档</button>
            <button onclick="loadDocuments('party_history')">党史类文档</button>
            <button onclick="loadDocuments('')">所有文档</button>
        </div>
        <div id="documents"></div>
    </div>

    <script>
        const API_BASE_URL = 'http://127.0.0.1:8000/api/md-docs';
        
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

        async function loadDocuments(category) {
            try {
                const url = category ? `/category/?category=${category}` : '/category/';
                const response = await fetchWithCORS(url);
                const data = await response.json();
                
                if (data.msg === 'success') {
                    displayDocuments(data.documents, data.category);
                } else {
                    document.getElementById('documents').innerHTML = 
                        `<p>加载失败: ${data.error}</p>`;
                }
            } catch (error) {
                console.error('加载失败:', error);
                document.getElementById('documents').innerHTML = 
                    '<p>加载失败，请检查网络连接</p>';
            }
        }

        async function displayDocuments(documents, category) {
            const container = document.getElementById('documents');
            const categoryName = getCategoryName(category);
            
            container.innerHTML = `
                <h2>${categoryName} (${documents.length} 个文档)</h2>
                <div id="document-list"></div>
            `;
            
            const listContainer = document.getElementById('document-list');
            const documentsHtml = [];
            
            for (const doc of documents) {
                documentsHtml.push(`
                    <div class="document-item">
                        <h3>${doc.title}</h3>
                        <p><strong>作者:</strong> ${doc.author || '未知'}</p>
                        <p><strong>来源:</strong> ${doc.source || '未知'}</p>
                        <p><strong>字数:</strong> ${doc.word_count}</p>
                        <p><strong>图片:</strong> ${doc.image_count} 张</p>
                        <p><strong>摘要:</strong> ${doc.summary || '无'}</p>
                        <button onclick="loadDocumentContent('${doc.id}')">查看内容</button>
                    </div>
                `);
            }
            
            listContainer.innerHTML = documentsHtml.join('');
        }

        async function loadDocumentContent(documentId) {
            try {
                const response = await fetchWithCORS(`/document/${documentId}/`);
                
                if (response.ok) {
                    const markdown = await response.text();
                    showDocumentContent(markdown);
                } else {
                    alert('文档不存在');
                }
            } catch (error) {
                console.error('加载文档内容失败:', error);
                alert('加载失败');
            }
        }

        function showDocumentContent(markdown) {
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
                display: flex;
                justify-content: center;
                align-items: center;
            `;
            
            const content = document.createElement('div');
            content.style.cssText = `
                background: white;
                padding: 20px;
                border-radius: 5px;
                max-width: 80%;
                max-height: 80%;
                overflow-y: auto;
            `;
            
            content.innerHTML = `
                <h3>文档内容</h3>
                <div class="document-content">
                    <pre style="white-space: pre-wrap; font-family: inherit;">${markdown}</pre>
                </div>
                <button onclick="this.parentElement.parentElement.remove()">关闭</button>
            `;
            
            modal.appendChild(content);
            document.body.appendChild(modal);
        }

        function getCategoryName(category) {
            const names = {
                'spirit': '精神类',
                'person': '人物类',
                'party_history': '党史类',
                'all': '所有文档'
            };
            return names[category] || '所有文档';
        }

        // 页面加载时获取系统状态
        window.onload = async function() {
            try {
                const response = await fetchWithCORS('/status/');
                const data = await response.json();
                
                if (data.msg === 'success') {
                    console.log('系统状态:', data);
                    console.log(`总文档数: ${data.total_documents}`);
                }
            } catch (error) {
                console.error('获取系统状态失败:', error);
            }
        };
    </script>
</body>
</html>
```

### 限制说明

1. **请求频率**: 建议间隔至少1秒
2. **并发限制**: 建议同时最多10个请求
3. **图片大小**: 单张图片最大10MB
4. **文档大小**: 单个文档最大1MB
5. **分页限制**: 每页最多100个文档

---

## 响应码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 技术栈

- **后端**: Django + SQLite
- **图片存储**: Django Media Files
- **数据格式**: JSON + Markdown
- **跨域支持**: Django CORS Headers

---

## 联系信息

如有问题或建议，请联系开发团队。

**版本**: v1.0  
**更新时间**: 2025-09-04

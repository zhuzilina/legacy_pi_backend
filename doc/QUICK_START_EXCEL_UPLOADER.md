# Excel题目上传工具 - 快速开始指南

## 🚀 快速开始

### 1. 安装依赖
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖（如果还没安装）
pip install pandas openpyxl
```

### 2. 创建Excel模板
```bash
python3 excel_question_uploader.py --create-template my_questions.xlsx
```

### 3. 填写题目数据
打开生成的 `my_questions.xlsx` 文件，按照模板填写题目数据。

### 4. 验证格式
```bash
python3 excel_question_uploader.py --server http://your-server.com --validate-only my_questions.xlsx
```

### 5. 上传题目
```bash
python3 excel_question_uploader.py --server http://your-server.com my_questions.xlsx
```

## 📋 Excel格式要求

### 必填列
- **题目内容**: 题目的具体内容
- **题目类型**: 单选题/多选题/填空题
- **分类**: 党史/理论

### 选择题必填
- **选项A/B/C/D**: 选项内容
- **正确答案**: A、B、C、D或组合（如ABCD）

### 填空题必填
- **正确答案**: 填空题的答案

### 可选列
- **难度**: 简单/中等/困难
- **答案解析**: 题目解析
- **标签**: 用逗号分隔的标签

## 📝 示例数据

| 题目内容 | 题目类型 | 分类 | 难度 | 选项A | 选项B | 选项C | 选项D | 正确答案 | 答案解析 |
|---------|---------|------|------|-------|-------|-------|-------|----------|----------|
| 中国共产党成立于哪一年？ | 单选题 | 党史 | 简单 | 1921年 | 1922年 | 1923年 | 1924年 | A | 中国共产党成立于1921年7月1日。 |
| 以下哪些是中国特色社会主义理论体系的重要组成部分？ | 多选题 | 理论 | 中等 | 邓小平理论 | "三个代表"重要思想 | 科学发展观 | 习近平新时代中国特色社会主义思想 | ABCD | 中国特色社会主义理论体系包括邓小平理论、"三个代表"重要思想、科学发展观和习近平新时代中国特色社会主义思想。 |
| 马克思主义的三大组成部分是马克思主义哲学、马克思主义政治经济学和______。 | 填空题 | 理论 | 中等 | | | | | 科学社会主义 | 马克思主义的三大组成部分是马克思主义哲学、马克思主义政治经济学和科学社会主义。 |

## 🔧 命令行参数

```bash
# 基本用法（必须指定服务器）
python3 excel_question_uploader.py --server http://your-server.com questions.xlsx

# 指定批量大小
python3 excel_question_uploader.py --server http://your-server.com --batch-size 20 questions.xlsx

# 仅验证格式
python3 excel_question_uploader.py --server http://your-server.com --validate-only questions.xlsx

# 创建模板（不需要服务器地址）
python3 excel_question_uploader.py --create-template template.xlsx
```

## ✅ 成功输出示例

```
📖 解析Excel文件: questions.xlsx
✅ 解析完成，共找到 10 道题目
📤 开始上传 10 道题目...
📦 上传第 1/1 批 (10 道题目)...
✅ 第 1 批上传完成: 成功 10, 失败 0

📊 上传完成:
   总题目数: 10
   成功: 10
   失败: 0

🎉 所有题目上传成功！
```

## ❌ 常见错误

### 1. 缺少必填字段
```
❌ 缺少必要的列: ['题目内容', '题目类型']
```

### 2. 无效的题目类型
```
❌ 无效的题目类型: ['判断题']
   支持的题目类型: ['单选题', '多选题', '填空题']
```

### 3. 选择题缺少选项
```
❌ 选择题必须提供选项
```

### 4. 填空题缺少答案
```
❌ 填空题必须提供正确答案
```

## 🆘 获取帮助

```bash
python3 excel_question_uploader.py --help
```

## 📚 详细文档

查看完整文档：`doc/Excel题目上传工具使用说明.md`

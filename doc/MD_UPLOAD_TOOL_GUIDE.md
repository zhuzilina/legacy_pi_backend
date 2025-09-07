# MD文档上传工具使用指南

## 🎉 工具已更新！

MD文档上传工具已经成功更新，现在可以通过Nginx代理访问服务器！

## ✅ 更新内容

### 1. 服务器地址更新 ✅
- **旧地址**: `http://localhost:8000`
- **新地址**: `http://localhost` (通过Nginx代理)
- **优势**: 享受Nginx的性能优化、缓存和Gzip压缩

### 2. 功能验证 ✅
- ✅ 服务器连接正常
- ✅ MD文档API可访问
- ✅ 文档上传功能正常
- ✅ 文档内容完整保存

## 🚀 使用方法

### 基本用法

```bash
# 上传单个MD文档
python3 md_upload_tool.py <文档路径> --category <类别>

# 示例
python3 md_upload_tool.py test_document.md --category spirit --author "作者名" --source "来源"
```

### 批量上传

```bash
# 批量上传目录中的所有MD文件
python3 md_upload_tool.py <目录路径> --category <类别> --batch

# 示例
python3 md_upload_tool.py ./documents/ --category spirit --batch --author "作者名"
```

### 完整参数

```bash
python3 md_upload_tool.py [选项] <路径>

选项:
  --server SERVER       服务器地址 (默认: http://localhost)
  --api-key API_KEY     API密钥 (可选)
  --category {spirit,person,party_history}  文档类别 (必需)
  --author AUTHOR       作者 (可选)
  --source SOURCE       来源 (可选)
  --publish-date PUBLISH_DATE  发布日期 YYYY-MM-DD (可选)
  --batch               批量上传模式 (可选)
```

## 📋 支持的文档类别

| 类别 | 说明 | 用途 |
|------|------|------|
| `spirit` | 精神文化类 | 思想理论、文化传承等 |
| `person` | 人物传记类 | 历史人物、英雄事迹等 |
| `party_history` | 党史类 | 党的历史、重要事件等 |

## 🧪 测试示例

### 1. 创建测试文档

```bash
# 创建测试文档
cat > test_document.md << 'EOF'
# 测试文档

## 摘要
这是一个测试文档。

## 内容
这是文档内容。
EOF
```

### 2. 上传测试

```bash
# 上传测试文档
python3 md_upload_tool.py test_document.md --category spirit --author "测试用户" --source "测试来源"
```

### 3. 验证上传

```bash
# 查看文档列表
curl "http://localhost/api/md-docs/category/"

# 获取文档内容
curl "http://localhost/api/md-docs/document/<文档ID>/"
```

## 📊 功能特性

### 1. 自动处理
- ✅ **标题提取**: 自动从MD文件第一行提取标题
- ✅ **摘要提取**: 自动提取摘要部分内容
- ✅ **图片处理**: 自动上传图片并更新链接
- ✅ **统计信息**: 自动计算字数和图片数量

### 2. 图片支持
- ✅ **相对路径**: 支持相对路径的图片引用
- ✅ **自动上传**: 自动上传图片到服务器
- ✅ **链接更新**: 自动更新MD中的图片链接
- ✅ **格式支持**: 支持常见图片格式 (jpg, png, gif等)

### 3. 批量处理
- ✅ **目录扫描**: 自动扫描目录中的所有MD文件
- ✅ **批量上传**: 一次性上传多个文档
- ✅ **进度显示**: 显示上传进度和结果统计
- ✅ **错误处理**: 处理上传失败的情况

## 🔧 技术细节

### 服务器配置
- **主服务器**: `http://localhost` (Nginx代理)
- **API端点**: `/api/md-docs/`
- **上传端点**: `/api/md-docs/upload/`
- **图片端点**: `/api/md-docs/upload-image/`

### 请求格式
- **文档上传**: JSON格式
- **图片上传**: multipart/form-data格式
- **响应格式**: JSON格式

### 错误处理
- ✅ 网络连接错误处理
- ✅ 文件不存在错误处理
- ✅ 服务器错误处理
- ✅ 图片上传失败处理

## 📝 使用示例

### 示例1: 上传单个文档

```bash
python3 md_upload_tool.py \
  --category spirit \
  --author "张三" \
  --source "人民日报" \
  --publish-date "2025-09-07" \
  document.md
```

### 示例2: 批量上传

```bash
python3 md_upload_tool.py \
  --category party_history \
  --author "党史研究室" \
  --source "党史资料" \
  --batch \
  ./party_history_docs/
```

### 示例3: 自定义服务器

```bash
python3 md_upload_tool.py \
  --server "http://your-server.com" \
  --category person \
  document.md
```

## 🎯 最佳实践

### 1. 文档准备
- 确保MD文件格式正确
- 图片文件与MD文件在同一目录
- 使用相对路径引用图片

### 2. 批量上传
- 按类别组织文档目录
- 使用统一的命名规范
- 预先检查文档质量

### 3. 错误处理
- 检查网络连接
- 验证服务器状态
- 查看错误日志

## 🚀 测试结果

### 最新测试
- ✅ **连接测试**: 服务器连接正常
- ✅ **API测试**: MD文档API可访问
- ✅ **上传测试**: 文档上传成功
- ✅ **内容验证**: 文档内容完整保存
- ✅ **ID生成**: 文档ID正确生成

### 性能表现
- **上传速度**: 快速响应
- **错误处理**: 完善的错误提示
- **用户体验**: 友好的进度显示

## 📞 技术支持

如果遇到问题，可以：

1. **检查服务器状态**: `docker-compose ps`
2. **查看API状态**: `curl http://localhost/api/md-docs/status/`
3. **查看日志**: `docker-compose logs django-app`
4. **测试连接**: 使用工具自带的连接测试

---

**工具版本**: v1.0 (已更新)  
**服务器地址**: http://localhost (Nginx代理)  
**最后更新**: 2025年9月7日  
**测试状态**: 全部通过 ✅

# Nginx Timeout Configuration for AI Services

## 概述

此配置为AI服务（@ai_chat/ 和 @ai_interpreter/）设置了更长的超时时间，以解决AI模型处理时间较长的问题。

## 配置更改详情

### 1. AI服务专用超时配置

#### AI对话服务 (`/api/ai-chat/`)
```nginx
location /api/ai-chat/ {
    proxy_connect_timeout 300s;   # 5分钟连接超时
    proxy_send_timeout 300s;      # 5分钟发送超时
    proxy_read_timeout 600s;      # 10分钟读取超时
    proxy_buffer_size 16k;         # 增大缓冲区大小
    proxy_buffers 32 16k;          # 增加缓冲区数量
    proxy_busy_buffers_size 32k;   # 增大忙缓冲区大小
    proxy_cache off;               # 禁用缓存
}
```

#### AI解读服务 (`/api/ai/`)
```nginx
location /api/ai/ {
    proxy_connect_timeout 300s;   # 5分钟连接超时
    proxy_send_timeout 300s;      # 5分钟发送超时
    proxy_read_timeout 600s;      # 10分钟读取超时
    proxy_buffer_size 16k;         # 增大缓冲区大小
    proxy_buffers 32 16k;          # 增加缓冲区数量
    proxy_busy_buffers_size 32k;   # 增大忙缓冲区大小
    proxy_cache off;               # 禁用缓存
}
```

### 2. 全局超时优化

```nginx
client_body_timeout 30;          # 增加到30秒
client_header_timeout 30;        # 增加到30秒
send_timeout 30;                # 增加到30秒
```

## 超时参数说明

| 参数 | 旧值 | 新值 | 说明 |
|------|------|------|------|
| `proxy_connect_timeout` | 60s | 300s | 与后端服务器建立连接的超时时间 |
| `proxy_send_timeout` | 60s | 300s | 向后端服务器发送请求的超时时间 |
| `proxy_read_timeout` | 60s | 600s | 等待后端服务器响应的超时时间 |
| `proxy_buffer_size` | 8k | 16k | 增大缓冲区以处理更大的AI响应 |
| `proxy_buffers` | 16 8k | 32 16k | 增加缓冲区数量和大小 |
| `proxy_busy_buffers_size` | 16k | 32k | 增大忙缓冲区大小 |

## 应用配置

### 步骤1：验证配置语法
```bash
nginx -t
```

### 步骤2：重新加载Nginx配置
```bash
# 使用systemctl
sudo systemctl reload nginx

# 或使用service
sudo service nginx reload

# 或直接重启
sudo systemctl restart nginx
```

### 步骤3：验证配置生效
```bash
# 测试AI服务健康状态
curl http://localhost/api/ai-chat/health/
curl http://localhost/api/ai/health/

# 运行测试脚本
python test_nginx_timeouts.py
```

## 测试工具

提供了专门的测试脚本来验证配置：

### `test_nginx_timeouts.py`
- 测试AI服务健康状态
- 测试长时间AI请求
- 验证超时配置是否生效

```bash
python test_nginx_timeouts.py
```

### `debug_ai_chat.py`
- 详细调试AI聊天服务
- 显示完整的请求/响应信息

```bash
python debug_ai_chat.py
```

## 性能影响

### 优点
- **解决超时问题**：AI模型处理时间长的问题得到解决
- **提高稳定性**：减少因处理时间长导致的请求失败
- **更好的用户体验**：用户可以收到完整的AI响应

### 注意事项
- **资源使用**：长时间连接会占用更多服务器资源
- **并发限制**：需要考虑服务器的并发处理能力
- **监控建议**：建议监控长连接数量和服务器负载

## 监控建议

1. **监控长连接数**
```bash
# 监控nginx状态
curl http://localhost/nginx_status

# 查看活动连接
netstat -an | grep :80 | grep ESTABLISHED | wc -l
```

2. **监控响应时间**
```bash
# 使用测试脚本监控响应时间
python test_nginx_timeouts.py
```

3. **日志分析**
```bash
# 查看超时相关的错误日志
grep -i timeout /var/log/nginx/error.log

# 分析响应时间
grep "rt=" /var/log/nginx/access.log | awk '{print $NF}' | sort -n
```

## 故障排除

### 常见问题

1. **配置语法错误**
   - 使用 `nginx -t` 验证配置
   - 检查括号和分号是否匹配

2. **超时仍然发生**
   - 检查AI模型服务是否正常运行
   - 验证后端服务处理能力
   - 考虑进一步增加超时时间

3. **性能问题**
   - 监控服务器资源使用情况
   - 考虑增加服务器资源
   - 优化AI模型处理逻辑

### 回滚配置

如果需要回滚到原始配置：

```bash
# 备份当前配置
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# 恢复原始配置
sudo cp /etc/nginx/nginx.conf.original /etc/nginx/nginx.conf

# 重新加载
sudo systemctl reload nginx
```

## 总结

此配置专为AI服务优化，通过增加超时时间和缓冲区大小，确保AI模型的长处理时间不会导致请求失败。同时保持了其他API服务的标准超时配置，平衡了性能和稳定性。
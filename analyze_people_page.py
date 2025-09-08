#!/usr/bin/env python3
"""
分析人民网页面结构
"""

import requests
from bs4 import BeautifulSoup


def analyze_page_structure(url):
    """分析页面结构"""
    print(f"🔍 分析页面: {url}")
    print("=" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有可能包含文章内容的元素
            print("查找文章内容元素:")
            
            # 1. 查找所有div元素
            divs = soup.find_all('div')
            print(f"总div数量: {len(divs)}")
            
            # 2. 查找包含大量文本的div
            content_divs = []
            for div in divs:
                text = div.get_text(strip=True)
                if len(text) > 200:  # 至少200个字符
                    class_name = ' '.join(div.get('class', []))
                    content_divs.append({
                        'element': div,
                        'text_length': len(text),
                        'class': class_name,
                        'text_preview': text[:100]
                    })
            
            # 按文本长度排序
            content_divs.sort(key=lambda x: x['text_length'], reverse=True)
            
            print(f"找到 {len(content_divs)} 个包含大量文本的div:")
            for i, div_info in enumerate(content_divs[:5]):
                print(f"  {i+1}. class=\"{div_info['class']}\" (长度: {div_info['text_length']})")
                print(f"     预览: {div_info['text_preview']}...")
                print()
            
            # 3. 查找特定的文章内容选择器
            selectors_to_test = [
                '.rm_txt_con',
                '.main',
                '.content',
                '.article-content',
                '#content',
                '.article-body',
                '.post-content',
                '.entry-content',
                '.text-content',
                '.main-content',
                '.body-content',
                '.article-text',
                '.content-text',
                '.main-text',
                '.body-text',
                '.article',
                '.post',
                '.entry',
                '.text',
                '.body',
                '.main'
            ]
            
            print("测试选择器:")
            working_selectors = []
            for selector in selectors_to_test:
                try:
                    elements = soup.select(selector)
                    if elements:
                        total_text = sum(len(elem.get_text(strip=True)) for elem in elements)
                        if total_text > 100:
                            working_selectors.append({
                                'selector': selector,
                                'count': len(elements),
                                'text_length': total_text
                            })
                            print(f"  ✅ {selector}: {len(elements)} 个元素, {total_text} 字符")
                        else:
                            print(f"  ⚠️ {selector}: {len(elements)} 个元素, 内容太少")
                    else:
                        print(f"  ❌ {selector}: 未找到元素")
                except Exception as e:
                    print(f"  ❌ {selector}: 错误 - {e}")
            
            # 4. 查找包含特定关键词的元素
            print("\n查找包含关键词的元素:")
            keywords = ['习近平', '中国', '发展', '经济', '政治', '社会', '建设', '改革']
            keyword_elements = []
            
            for div in divs:
                text = div.get_text(strip=True)
                if len(text) > 200:
                    for keyword in keywords:
                        if keyword in text:
                            class_name = ' '.join(div.get('class', []))
                            keyword_elements.append({
                                'element': div,
                                'keyword': keyword,
                                'text_length': len(text),
                                'class': class_name,
                                'text_preview': text[:100]
                            })
                            break
            
            if keyword_elements:
                print(f"找到 {len(keyword_elements)} 个包含关键词的元素:")
                for i, elem_info in enumerate(keyword_elements[:3]):
                    print(f"  {i+1}. 关键词: {elem_info['keyword']}")
                    print(f"     class: {elem_info['class']}")
                    print(f"     长度: {elem_info['text_length']}")
                    print(f"     预览: {elem_info['text_preview']}...")
                    print()
            
            return working_selectors, keyword_elements
            
    except Exception as e:
        print(f"分析失败: {e}")
        return [], []


def main():
    """主函数"""
    print("🚀 开始分析人民网页面结构...")
    print("=" * 60)
    
    # 测试几个不同的文章页面
    test_urls = [
        "http://politics.people.com.cn/n1/2025/0908/c1024-40559264.html",
        "http://world.people.com.cn/n1/2025/0908/c1002-40559255.html",
        "http://health.people.com.cn/n1/2025/0908/c14739-40559156.html"
    ]
    
    all_selectors = []
    all_keyword_elements = []
    
    for url in test_urls:
        selectors, keyword_elements = analyze_page_structure(url)
        all_selectors.extend(selectors)
        all_keyword_elements.extend(keyword_elements)
        print()
    
    # 汇总结果
    print("📊 汇总分析结果:")
    print("=" * 50)
    
    # 统计选择器
    selector_stats = {}
    for selector_info in all_selectors:
        selector = selector_info['selector']
        if selector not in selector_stats:
            selector_stats[selector] = {
                'count': 0,
                'total_text': 0,
                'avg_text': 0
            }
        selector_stats[selector]['count'] += 1
        selector_stats[selector]['total_text'] += selector_info['text_length']
    
    # 计算平均文本长度
    for selector in selector_stats:
        stats = selector_stats[selector]
        stats['avg_text'] = stats['total_text'] / stats['count']
    
    # 按平均文本长度排序
    sorted_selectors = sorted(selector_stats.items(), key=lambda x: x[1]['avg_text'], reverse=True)
    
    print("推荐的选择器 (按平均文本长度排序):")
    for selector, stats in sorted_selectors[:10]:
        print(f"  {selector}: 平均 {stats['avg_text']:.0f} 字符, 出现 {stats['count']} 次")
    
    print(f"\n找到 {len(all_keyword_elements)} 个包含关键词的元素")
    
    print("\n✅ 分析完成！")
    print("=" * 60)
    print("💡 建议:")
    print("   1. 使用推荐的选择器更新crawler")
    print("   2. 添加关键词匹配作为备用方案")
    print("   3. 测试新的选择器是否有效")


if __name__ == '__main__':
    main()

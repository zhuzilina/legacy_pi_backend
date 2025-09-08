#!/usr/bin/env python3
"""
修复crawler选择器，适配人民网新的网页结构
"""

import requests
from bs4 import BeautifulSoup


def analyze_people_website():
    """分析人民网网站结构"""
    print("🔍 分析人民网网站结构...")
    print("=" * 50)
    
    # 测试一个具体的文章页面
    test_url = "http://politics.people.com.cn/n1/2025/0908/c1024-40559264.html"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print("分析页面结构...")
            
            # 查找所有div元素及其class
            divs = soup.find_all('div', class_=True)
            print(f"找到 {len(divs)} 个带class的div元素")
            
            # 分析可能的文章内容区域
            content_candidates = []
            
            for div in divs:
                class_name = ' '.join(div.get('class', []))
                text_length = len(div.get_text(strip=True))
                
                # 查找可能包含文章内容的区域
                if (text_length > 500 and 
                    any(keyword in class_name.lower() for keyword in ['content', 'article', 'text', 'main', 'body'])):
                    content_candidates.append({
                        'class': class_name,
                        'text_length': text_length,
                        'element': div
                    })
            
            print(f"找到 {len(content_candidates)} 个可能的内容区域:")
            for i, candidate in enumerate(content_candidates[:5]):
                print(f"  {i+1}. class=\"{candidate['class']}\" (长度: {candidate['text_length']})")
                
                # 显示前100个字符
                text_preview = candidate['element'].get_text(strip=True)[:100]
                print(f"     预览: {text_preview}...")
                print()
            
            # 查找所有可能的文章内容选择器
            print("建议的选择器:")
            selectors = []
            
            for div in divs:
                class_name = ' '.join(div.get('class', []))
                if any(keyword in class_name.lower() for keyword in ['content', 'article', 'text', 'main', 'body']):
                    selector = f".{class_name.replace(' ', '.')}"
                    selectors.append(selector)
            
            # 去重并排序
            unique_selectors = list(set(selectors))
            unique_selectors.sort()
            
            for selector in unique_selectors[:10]:
                print(f"  {selector}")
            
            return unique_selectors
            
    except Exception as e:
        print(f"分析失败: {e}")
        return []


def test_selectors():
    """测试选择器效果"""
    print("\n🧪 测试选择器效果...")
    print("=" * 50)
    
    test_url = "http://politics.people.com.cn/n1/2025/0908/c1024-40559264.html"
    
    # 新的选择器列表
    new_selectors = [
        '.rm_txt_con',
        '.content',
        '.article-content',
        '#content',
        '.main-content',
        '.text-content',
        '.article-body',
        '.post-content',
        '.entry-content',
        '.article-text',
        '.content-text',
        '.main-text',
        '.body-text',
        '.article-main',
        '.content-main',
        '.text-main',
        '.main-body',
        '.content-body',
        '.text-body',
        '.article-content-text',
        '.content-article',
        '.text-article',
        '.main-article',
        '.body-content',
        '.body-article',
        '.body-text',
        '.article',
        '.post',
        '.entry',
        '.text',
        '.body',
        '.main',
        '.content'
    ]
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print("测试选择器:")
            working_selectors = []
            
            for selector in new_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        # 检查是否包含实际内容
                        total_text = sum(len(elem.get_text(strip=True)) for elem in elements)
                        if total_text > 100:  # 至少100个字符
                            working_selectors.append({
                                'selector': selector,
                                'count': len(elements),
                                'text_length': total_text
                            })
                            print(f"  ✅ {selector}: {len(elements)} 个元素, {total_text} 字符")
                        else:
                            print(f"  ⚠️ {selector}: {len(elements)} 个元素, 但内容太少 ({total_text} 字符)")
                    else:
                        print(f"  ❌ {selector}: 未找到元素")
                except Exception as e:
                    print(f"  ❌ {selector}: 错误 - {e}")
            
            print(f"\n找到 {len(working_selectors)} 个有效的选择器")
            
            # 推荐最佳选择器
            if working_selectors:
                best_selector = max(working_selectors, key=lambda x: x['text_length'])
                print(f"推荐使用: {best_selector['selector']}")
                return best_selector['selector']
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    return None


def main():
    """主函数"""
    print("🚀 开始修复crawler选择器...")
    print("=" * 60)
    
    # 分析网站结构
    selectors = analyze_people_website()
    
    # 测试选择器
    best_selector = test_selectors()
    
    print("\n✅ 分析完成！")
    print("=" * 60)
    print("📋 修复建议:")
    print("   1. 更新 crawler/services.py 中的 _extract_content 方法")
    print("   2. 添加新的选择器到 content_selectors 列表")
    print("   3. 测试新的选择器是否有效")
    
    if best_selector:
        print(f"\n💡 推荐的选择器: {best_selector}")
        print("   可以将此选择器添加到现有列表中")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闲鱼可点击链接版 - 优化：确保链接在聊天窗口中可点击
保持所有功能不变，仅优化输出结果
"""

import sys
import os
import time
import json
import re
from datetime import datetime
from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(__file__))

# ========== 数据提取函数 ==========

def extract_price_from_element(element):
    """从元素中提取价格"""
    try:
        element_text = element.text
        patterns = [
            r'¥\s*[\d,]+(?:\.\d+)?',
            r'￥\s*[\d,]+(?:\.\d+)?',
            r'[\d,]+(?:\.\d+)?\s*元'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, element_text)
            if matches:
                price = matches[0]
                numbers = re.findall(r'[\d,.]+', price)
                if numbers:
                    return f"¥{numbers[0]}"
        
        lines = element_text.split('\n')
        for line in lines:
            if '¥' in line or '￥' in line:
                numbers = re.findall(r'[\d,.]+', line)
                if numbers:
                    return f"¥{numbers[0]}"
            
    except:
        pass
    
    return "价格未知"

def extract_location_from_element(element):
    """从元素中提取地区"""
    try:
        element_text = element.text
        
        locations = [
            '北京', '上海', '天津', '重庆',
            '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
            '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾',
            '内蒙古', '广西', '西藏', '宁夏', '新疆', '香港', '澳门',
            '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '苏州', '郑州', '长沙', '东莞', '沈阳'
        ]
        
        for location in locations:
            if location in element_text:
                return location
        
        location_keywords = ['同城', '自提', '本地', '当面交易', '附近', '周边']
        for line in element_text.split('\n'):
            for keyword in location_keywords:
                if keyword in line:
                    return "同城交易"
        
        for line in element_text.split('\n'):
            if any(marker in line for marker in ['省', '市', '区', '县', '镇']):
                for location in locations:
                    if location in line:
                        return location
                return line.strip()[:20]
            
    except:
        pass
    
    return "地区未知"

def extract_time_from_element(element):
    """从元素中提取时间（修复优化版）"""
    try:
        element_text = element.text
        
        # 扩展时间匹配模式，支持更多格式
        patterns = [
            r'\d+\s*分钟前\s*(发布)?',      # 5分钟前, 5分钟前发布
            r'\d+\s*小时前\s*(发布)?',      # 3小时前, 3小时前发布
            r'\d+\s*天前\s*(发布)?',        # 2天前, 2天前发布
            r'\d+\s*天内\s*(发布)?',        # 3天内, 7天内发布 (新增)
            r'刚刚\s*(发布)?',              # 刚刚, 刚刚发布
            r'今天\s*(发布)?',              # 今天, 今天发布
            r'昨天\s*(发布)?',              # 昨天, 昨天发布
            r'前天\s*(发布)?',              # 前天, 前天发布 (新增)
            r'\d+-\d+\s*发布',              # 03-19 发布
            r'\d+月\d+日\s*发布',           # 3月19日 发布
            r'\d+:\d+\s*发布',              # 12:30 发布
            r'\d+/\d+\s*发布'               # 03/19 发布
        ]
        
        lines = element_text.split('\n')
        # 优先处理短文本（时间信息通常较短）
        short_lines = [line.strip() for line in lines if 5 <= len(line.strip()) <= 30]
        long_lines = [line.strip() for line in lines if len(line.strip()) > 30]
        
        # 1. 首先检查短文本（时间信息通常是短文本）
        for line in short_lines:
            if not line:
                continue
                
            # 1.1 正则匹配
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    # 验证确实是时间格式
                    if any(keyword in line for keyword in ['分钟前', '小时前', '天前', '天内', '刚刚', '今天', '昨天', '前天', '发布']):
                        return line
            
            # 1.2 关键词匹配
            time_keywords = ['分钟前', '小时前', '天前', '天内', '刚刚', '今天', '昨天', '前天', '前发布', '发布']
            for keyword in time_keywords:
                if keyword in line:
                    # 排除价格信息
                    if not any(price_keyword in line for price_keyword in ['¥', '￥', '元', '价格']):
                        return line
        
        # 2. 尝试多种CSS选择器直接获取时间元素
        try:
            from selenium.webdriver.common.by import By
            
            # 时间选择器列表（按优先级）
            time_selectors = [
                "span[class*='time']",
                "div[class*='time']",
                "span[class*='Time']", 
                "div[class*='Time']",
                "span[class*='publish']",
                "div[class*='publish']",
                "span[class*='date']",
                "div[class*='date']"
            ]
            
            for selector in time_selectors:
                try:
                    time_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for time_elem in time_elements:
                        time_text = time_elem.text.strip()
                        if time_text and len(time_text) <= 30:  # 时间文本通常较短
                            if any(keyword in time_text for keyword in ['前', '发布', '天', '天内', '小时', '分钟', '今天', '昨天', '刚刚']):
                                # 排除价格信息
                                if not any(price_keyword in time_text for price_keyword in ['¥', '￥', '元']):
                                    return time_text
                except:
                    continue
            
            # 3. 遍历所有子元素查找短文本（可能是时间）
            all_elements = element.find_elements(By.XPATH, ".//*")
            for elem in all_elements:
                try:
                    elem_text = elem.text.strip()
                    if elem_text and 5 <= len(elem_text) <= 25:  # 时间文本通常很简短
                        # 检查是否包含时间关键词
                        time_indicators = ['分钟前', '小时前', '天前', '天内', '刚刚', '今天', '昨天', '前天', '发布']
                        for indicator in time_indicators:
                            if indicator in elem_text:
                                # 排除包含长描述的情况
                                if len(elem_text) <= 25 and not any(price_keyword in elem_text for price_keyword in ['¥', '￥', '元']):
                                    return elem_text
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ CSS选择器时间提取失败: {e}")
        
        # 4. 智能文本分析：查找包含时间信息的简短文本段
        full_text = element_text
        # 只查找简短的、包含时间关键词的文本
        time_pattern = re.compile(r'([^。，！？\n]{5,30}?(?:分钟前|小时前|天前|天内|刚刚|今天|昨天|前天)[^。，！？\n]{0,10})', re.IGNORECASE)
        matches = time_pattern.findall(full_text)
        if matches:
            for match in matches:
                match = match.strip()
                if match and 5 <= len(match) <= 40:  # 严格长度限制
                    # 验证是时间信息，不是描述
                    if any(keyword in match for keyword in ['分钟前', '小时前', '天前', '天内', '刚刚', '今天', '昨天', '前天']):
                        if len(match.split()) <= 3:  # 时间信息通常很简短
                            return match
        
        # 5. 最后的安全检查：如果前面的方法都失败，返回"时间未知"
        # 不尝试匹配长文本，避免错误识别商品描述
        
    except Exception as e:
        print(f"⚠️ 时间提取失败: {e}")
    
    return "时间未知"

def get_price_value(price_str):
    """提取价格数值用于排序"""
    if not price_str or price_str == "价格未知":
        return float('inf')
    
    numbers = re.findall(r'[\d,.]+', price_str)
    if not numbers:
        return float('inf')
    
    try:
        return float(numbers[0].replace(',', ''))
    except:
        return float('inf')

# ========== 个人闲置功能 ==========

def click_personal_idle_button(driver):
    """点击个人闲置按钮"""
    try:
        print("\n检测到'个人'参数，开始查找'个人闲置'按钮...")
        
        time.sleep(2)
        
        # 查找所有包含"个人"的元素
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '个人')]")
        
        for elem in all_elements[:20]:
            try:
                text = elem.text.strip()
                if '个人闲置' in text:
                    print(f"找到'个人闲置'按钮: {text}")
                    elem.click()
                    time.sleep(1)
                    print("'个人闲置'按钮点击成功")
                    return True
            except:
                continue
        
        return False
        
    except Exception as e:
        print(f"点击个人闲置按钮失败: {e}")
        return False

# ========== 优化输出函数 ==========

def extract_product_id_from_url(url):
    """从URL中提取商品ID"""
    if not url:
        return None
    
    try:
        # 从URL中提取商品ID
        # 格式1: https://www.goofish.com/item?id=1033485933604&categoryId=126866353
        # 格式2: https://www.goofish.com/item/1033485933604
        import re
        
        # 尝试提取id参数
        match = re.search(r'[?&]id=(\d+)', url)
        if match:
            return match.group(1)
        
        # 尝试从路径中提取
        match = re.search(r'/item/(\d+)', url)
        if match:
            return match.group(1)
        
        # 尝试其他可能的格式
        match = re.search(r'/(\d{10,})', url)
        if match:
            return match.group(1)
        
    except:
        pass
    
    return None

def generate_deep_links(product_id):
    """生成两种链接格式：web_link 和 deep_link"""
    if not product_id:
        return {
            'web_link': '',      # 网页版链接
            'deep_link': ''      # deep link
        }
    
    # web_link: 原网页链接
    web_link = f"https://www.goofish.com/item?id={product_id}&categoryId=126866353"
    
    # deep_link: 移动网页版链接，飞书兼容
    deep_link = f"https://h5.m.goofish.com/item?id={product_id}"
    
    return {
        'web_link': web_link,
        'deep_link': deep_link
    }

def format_output_for_chat(keyword, min_price, max_price, has_personal, sorted_items, linked_count, screenshot, json_file):
    """为聊天窗口优化输出格式，确保链接可点击"""
    
    output_lines = []
    
    # 1. 搜索结果概览
    output_lines.append(f"\n搜索完成: {keyword} (¥{min_price}-¥{max_price})")
    if has_personal:
        output_lines.append("筛选条件: 个人闲置 已应用")
    output_lines.append(f"抓取产品: {len(sorted_items)} 个")
    output_lines.append(f"链接匹配: {linked_count}/{len(sorted_items)}")
    output_lines.append(f"截图保存: {screenshot}")
    output_lines.append(f"数据保存: {json_file}")
    
    # 2. 前10个产品（确保链接可点击）
    output_lines.append(f"\n前10个产品:")
    
    for i, item in enumerate(sorted_items[:10], 1):
        output_lines.append(f"\n{i}. {item['title']}")
        output_lines.append(f"   价格: {item['price']}")
        output_lines.append(f"   时间: {item['time']}")
        output_lines.append(f"   地区: {item['location']}")
        
        if item.get('product_id'):
            # 显示两种链接格式：web_link 和 deep_link
            output_lines.append(f"   商品ID: {item['product_id']}")
            output_lines.append(f"   web_link: {item.get('web_link', '')}")
            output_lines.append(f"   deep_link: {item.get('deep_link', '')}")
            
        elif item.get('link'):
            # 向后兼容：如果没有提取到商品ID，使用原链接
            output_lines.append(f"   链接: {item['link']}")
        else:
            output_lines.append(f"   链接: 无链接")
    
    # 3. 价格分析
    prices = []
    for item in sorted_items:
        price_str = item['price']
        if price_str != "价格未知":
            numbers = re.findall(r'[\d,.]+', price_str)
            if numbers:
                try:
                    prices.append(float(numbers[0].replace(',', '')))
                except:
                    pass
    
    if prices:
        output_lines.append(f"\n价格分析 ({len(prices)} 个有效价格):")
        output_lines.append(f"   最低: ¥{min(prices):.2f}")
        output_lines.append(f"   最高: ¥{max(prices):.2f}")
        output_lines.append(f"   平均: ¥{sum(prices)/len(prices):.2f}")
        
        # 在筛选范围内的产品数量
        in_range = [p for p in prices if min_price <= p <= max_price]
        output_lines.append(f"   在筛选范围内: {len(in_range)} 个 ({len(in_range)/len(prices)*100:.1f}%)")
    
    # 4. 地区统计
    locations = {}
    for item in sorted_items:
        loc = item['location']
        if loc != "地区未知":
            locations[loc] = locations.get(loc, 0) + 1
    
    if locations:
        output_lines.append(f"\n地区分布:")
        sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
        for loc, count in sorted_locations[:8]:
            output_lines.append(f"   {loc}: {count} 个")
    
    # 5. 链接使用说明
    output_lines.append(f"\n🔗 链接使用说明:")
    output_lines.append(f"   1. web_link: 网页版链接，在浏览器中打开商品页面")
    output_lines.append(f"   2. deep_link: 移动网页版链接，自动唤醒闲鱼App")
    output_lines.append(f"   3. 共找到 {linked_count} 个可点击链接")
    output_lines.append(f"   4. 链接覆盖率: {linked_count}/{len(sorted_items)} ({linked_count/len(sorted_items)*100:.1f}%)")
    output_lines.append(f"   💡 提示: deep_link 在飞书中可直接点击")
    
    return "\n".join(output_lines)

# ========== 主函数 ==========

def main():
    """主函数"""
    # 解析参数
    if len(sys.argv) < 5 or sys.argv[1] != '闲鱼搜':
        print("格式: python3 xianyu_clickable_links.py 闲鱼搜 关键词 最低价 最高价 [个人]")
        print("     可选参数: 在价格后加'个人'自动勾选个人闲置按钮")
        sys.exit(1)
    
    keyword = sys.argv[2]
    min_price = float(sys.argv[3])
    max_price = float(sys.argv[4])
    
    # 检查是否有"个人"参数
    has_personal = len(sys.argv) > 5 and sys.argv[5] == '个人'
    
    # ========== 导入最稳定的版本 ==========
    try:
        from xianyu_hover_confirm import XianYuHoverConfirm
    except ImportError:
        print("导入最稳定版本失败")
        sys.exit(1)
    
    # 执行原有功能
    solution = XianYuHoverConfirm(headless=False)
    
    try:
        # 1. 浏览器
        if not solution.setup_driver():
            return
        
        # 2. 登录
        if not solution.ensure_login_once():
            return
        
        # 3. 搜索
        if not solution.search_items(keyword):
            return
        
        # 4. 按钮
        if not solution.click_new_release():
            return
        
        if not solution.click_latest():
            return
        
        # 5. 价格筛选
        if not solution.set_price_range_with_hover(min_price, max_price):
            return
        
        # 6. 个人闲置功能
        if has_personal:
            click_personal_idle_button(solution.driver)
            time.sleep(3)
        
        # 7. 截图
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        personal_suffix = "_个人" if has_personal else ""
        screenshot = f"clickable{personal_suffix}_{keyword}_min{min_price}_max{max_price}_{timestamp}.png"
        solution.driver.save_screenshot(screenshot)
        
        time.sleep(3)
        
        # ========== 抓取数据 ==========
        
        # 抓取产品
        items = []
        try:
            elements = solution.driver.find_elements(By.CSS_SELECTOR, "div[class*='feeds-content']")
            
            for i, elem in enumerate(elements[:50]):
                try:
                    text = elem.text.strip()
                    if not text or len(text) < 20:
                        continue
                    
                    # 提取标题
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if len(lines) < 2:
                        continue
                    
                    title = ""
                    for line in lines:
                        if len(line) > 10 and len(line) < 100:
                            if len(line) > len(title):
                                title = line
                    
                    if not title:
                        title = lines[0] if lines else "未知标题"
                    
                    # 提取信息
                    price = extract_price_from_element(elem)
                    time_str = extract_time_from_element(elem)
                    location = extract_location_from_element(elem)
                    
                    items.append({
                        'index': i + 1,
                        'title': title[:80],
                        'price': price,
                        'time': time_str,
                        'location': location,
                        'link': "",  # 原链接
                        'product_id': "",  # 商品ID
                        'web_link': "",  # 网页版链接
                        'deep_link': ""   # Deep Link
                    })
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"抓取产品失败: {e}")
        
        # 获取所有链接
        all_links = []
        try:
            links = solution.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and 'goofish.com/item' in href:
                        text = link.text.strip()
                        if text:
                            # 提取商品ID
                            product_id = extract_product_id_from_url(href)
                            all_links.append({
                                'href': href, 
                                'text': text,
                                'product_id': product_id
                            })
                except:
                    continue
        except Exception as e:
            print(f"获取链接失败: {e}")
        
        # 匹配链接
        linked_count = 0
        for item in items:
            title = item['title']
            best_link = ""
            best_product_id = ""
            best_score = 0
            
            for link_data in all_links:
                link_text = link_data['text']
                href = link_data['href']
                product_id = link_data['product_id']
                
                # 简单匹配
                score = 0
                if title in link_text:
                    score += 5
                elif any(keyword in link_text for keyword in title.split()[:3]):
                    score += 3
                
                if score > best_score:
                    best_score = score
                    best_link = href
                    best_product_id = product_id
            
            if best_score >= 2:
                # 生成两种链接格式
                item['link'] = best_link
                item['product_id'] = best_product_id
                
                # 生成两种链接格式
                deep_links = generate_deep_links(best_product_id)
                
                # 存储两种链接格式
                item['web_link'] = deep_links['web_link']      # 网页版链接
                item['deep_link'] = deep_links['deep_link']    # deep link
                
                linked_count += 1
        
        # ========== 保持原始顺序（与浏览器窗口一致） ==========
        
        # 不重新排序，保持页面原始顺序（最新在前）
        sorted_items = items
        
        # 更新索引（按原始顺序）
        for i, item in enumerate(sorted_items):
            item['index'] = i + 1
        
        # ========== 保存JSON数据 ==========
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"clickable{personal_suffix}_{keyword}_min{min_price}_max{max_price}_{timestamp}.json"
        
        # 准备产品数据，确保包含所有链接信息
        products_data = []
        for item in sorted_items:
            # 为每个商品生成多种链接格式
            deep_links = generate_deep_links(item.get('product_id'))
            
            product_data = {
                'index': item.get('index'),
                'title': item.get('title'),
                'price': item.get('price'),
                'time': item.get('time'),
                'location': item.get('location'),
                'product_id': item.get('product_id'),
                'web_link': item.get('web_link', item.get('link')),
                'deep_link': item.get('deep_link', deep_links['deep_link'])
            }
            products_data.append(product_data)
        
        data = {
            'search': {
                'keyword': keyword,
                'min_price': min_price,
                'max_price': max_price,
                'personal_idle': has_personal,
                'timestamp': timestamp,
                'total_products': len(sorted_items),
                'linked_products': linked_count,
                'sort_by': 'latest',  # 按最新发布排序（与浏览器窗口一致）
                'link_types': [
                    'web_link', 
                    'deep_link'
                ],
                'feishu_compatible': True,
                'recommended_for_feishu': 'deep_link'
            },
            'products': products_data
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # ========== 优化输出到聊天窗口 ==========
        output = format_output_for_chat(
            keyword, min_price, max_price, has_personal,
            sorted_items, linked_count, screenshot, json_file
        )
        
        # 输出结果
        print(output)
        
        # 保持浏览器打开
        print("\n浏览器保持打开，按Enter关闭...")
        
        try:
            input()
        except:
            pass
        
        solution.driver.quit()
        
        print("\n执行完成")
        
    except KeyboardInterrupt:
        print("\n用户中断")
        if solution.driver:
            solution.driver.quit()
    except Exception as e:
        print(f"\n异常: {e}")
        if solution.driver:
            solution.driver.quit()

if __name__ == "__main__":
    main()
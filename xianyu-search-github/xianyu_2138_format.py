#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闲鱼21:38格式版 - 保持所有功能不变，只优化输出格式为21:38之前的模式
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
    """从元素中提取时间"""
    try:
        element_text = element.text
        
        patterns = [
            r'\d+分钟前发布',
            r'\d+小时前发布', 
            r'\d+天前发布',
            r'刚刚发布',
            r'今天发布',
            r'昨天发布'
        ]
        
        lines = element_text.split('\n')
        for line in lines:
            for pattern in patterns:
                if re.search(pattern, line):
                    return line.strip()
            
            if any(keyword in line for keyword in ['前发布', '分钟前', '小时前', '天前', '刚刚', '今天', '昨天']):
                return line.strip()
            
    except:
        pass
    
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

# ========== 主函数 ==========

def main():
    """主函数"""
    # 解析参数
    if len(sys.argv) < 5 or sys.argv[1] != '闲鱼搜':
        print("格式: python3 xianyu_2138_format.py 闲鱼搜 关键词 最低价 最高价 [个人]")
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
        screenshot = f"2138{personal_suffix}_{keyword}_min{min_price}_max{max_price}_{timestamp}.png"
        solution.driver.save_screenshot(screenshot)
        
        time.sleep(3)
        
        # ========== 抓取和显示结果 ==========
        
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
                        'link': ""  # 稍后添加
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
                            all_links.append({'href': href, 'text': text})
                except:
                    continue
        except Exception as e:
            print(f"获取链接失败: {e}")
        
        # 匹配链接
        linked_count = 0
        for item in items:
            title = item['title']
            best_link = ""
            best_score = 0
            
            for link_data in all_links:
                link_text = link_data['text']
                href = link_data['href']
                
                # 简单匹配
                score = 0
                if title in link_text:
                    score += 5
                elif any(keyword in link_text for keyword in title.split()[:3]):
                    score += 3
                
                if score > best_score:
                    best_score = score
                    best_link = href
            
            if best_score >= 2:
                item['link'] = best_link
                linked_count += 1
        
        # ========== 排序同步 ==========
        
        # 按价格排序
        sorted_items = sorted(items, key=lambda x: get_price_value(x['price']))
        
        # 更新索引
        for i, item in enumerate(sorted_items):
            item['index'] = i + 1
        
        # ========== 输出结果（21:38之前的格式） ==========
        
        # 功能执行状态
        print(f"\n搜索完成: {keyword} (¥{min_price}-¥{max_price})")
        if has_personal:
            print("筛选条件: 个人闲置 已应用")
        
        print(f"抓取产品: {len(sorted_items)} 个")
        print(f"链接匹配: {linked_count}/{len(sorted_items)}")
        print(f"截图保存: {screenshot}")
        
        # 显示前15个产品（21:38之前的简洁格式）
        print(f"\n前15个产品:")
        
        for i, item in enumerate(sorted_items[:15], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   价格: {item['price']}")
            print(f"   时间: {item['time']}")
            print(f"   地区: {item['location']}")
            
            if item['link']:
                print(f"   链接: {item['link']}")
            else:
                print(f"   链接: 无链接")
        
        # 价格分析
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
            print(f"\n价格分析 ({len(prices)} 个有效价格):")
            print(f"   最低: ¥{min(prices):.2f}")
            print(f"   最高: ¥{max(prices):.2f}")
            print(f"   平均: ¥{sum(prices)/len(prices):.2f}")
            
            # 在筛选范围内的产品数量
            in_range = [p for p in prices if min_price <= p <= max_price]
            print(f"   在筛选范围内: {len(in_range)} 个 ({len(in_range)/len(prices)*100:.1f}%)")
        
        # 地区统计
        locations = {}
        for item in sorted_items:
            loc = item['location']
            if loc != "地区未知":
                locations[loc] = locations.get(loc, 0) + 1
        
        if locations:
            print(f"\n地区分布:")
            sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
            for loc, count in sorted_locations[:8]:
                print(f"   {loc}: {count} 个")
        
        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        personal_suffix = "_个人" if has_personal else ""
        filename = f"2138{personal_suffix}_{keyword}_min{min_price}_max{max_price}_{timestamp}.json"
        
        data = {
            'search': {
                'keyword': keyword,
                'min_price': min_price,
                'max_price': max_price,
                'personal_idle': has_personal,
                'timestamp': timestamp,
                'total_products': len(sorted_items),
                'linked_products': linked_count,
                'sort_by': 'price_asc'
            },
            'products': sorted_items
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n数据保存: {filename}")
        
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
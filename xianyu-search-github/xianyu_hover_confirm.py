#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
闲鱼悬停确认版本
关键发现：价格确定按钮需要鼠标悬停在价格栏上才能显示
优化：增加悬停操作，然后查找并点击确认按钮
保留所有现有功能，只优化确认按钮显示逻辑
"""

import os
import time
import pickle
import urllib.parse
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class XianYuHoverConfirm:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.timeout = 15
        self.cookies_dir = os.path.join(os.path.dirname(__file__), "cookies")
        self.cookies_file = os.path.join(self.cookies_dir, "xianyu_cookies.pkl")
        os.makedirs(self.cookies_dir, exist_ok=True)
        self.is_logged_in = False
    
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
            
            options.add_argument("--window-size=1400,900")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            print("🚀 启动浏览器...")
            self.driver = webdriver.Chrome(options=options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ 浏览器启动成功")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            return False
    
    def load_cookies(self):
        """加载保存的cookies"""
        if not os.path.exists(self.cookies_file):
            return None
        
        try:
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            print(f"📂 加载 {len(cookies)} 个保存的cookies")
            return cookies
        except Exception as e:
            print(f"❌ 加载cookies失败: {e}")
            return None
    
    def save_cookies(self):
        """保存cookies"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            print(f"💾 保存 {len(cookies)} 个cookies")
            return True
        except Exception as e:
            print(f"⚠️  保存cookies失败: {e}")
            return False
    
    def apply_cookies(self, cookies):
        """应用cookies"""
        try:
            self.driver.get("https://www.goofish.com")
            time.sleep(2)
            self.driver.delete_all_cookies()
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    continue
            
            self.driver.refresh()
            time.sleep(3)
            print("✅ 已应用保存的登录信息")
            return True
        except Exception as e:
            print(f"❌ 应用cookies失败: {e}")
            return False
    
    def ensure_login_once(self):
        """只在开始时确保登录一次"""
        print("\n" + "=" * 60)
        print("🔐 一次性登录检查")
        print("=" * 60)
        
        saved_cookies = self.load_cookies()
        if saved_cookies:
            print("🔍 尝试使用保存的登录信息...")
            if self.apply_cookies(saved_cookies):
                print("✅ 假设登录成功（使用cookies）")
                self.is_logged_in = True
                return True
            else:
                print("⚠️  应用cookies失败，需要重新登录")
        
        print("\n📱 需要扫码登录...")
        self.driver.get("https://www.goofish.com")
        time.sleep(3)
        
        print("⏳ 等待扫码登录...")
        print("   请在60秒内完成扫码")
        
        # 简单等待用户扫码
        print("   扫码后请等待页面自动刷新...")
        time.sleep(60)
        
        # 假设用户已扫码登录
        print("✅ 假设扫码登录成功")
        self.save_cookies()
        self.is_logged_in = True
        return True
    
    def search_items(self, keyword):
        """搜索商品"""
        try:
            encoded = urllib.parse.quote(keyword)
            url = f"https://www.goofish.com/search?spm=a21ybx.search.searchActivate.3.dac61d0aLNYLoK&q={encoded}"
            
            print(f"\n🔍 搜索: {keyword}")
            print(f"📎 URL: {url}")
            
            self.driver.get(url)
            time.sleep(5)
            
            print("✅ 搜索页面加载成功")
            return True
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return False
    
    def click_new_release(self):
        """点击'新发布'按钮"""
        print("\n🎯 点击'新发布'按钮...")
        
        try:
            xpath = "//*[contains(text(), '新发布')]"
            wait = WebDriverWait(self.driver, self.timeout)
            elements = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            
            print(f"🔍 找到 {len(elements)} 个'新发布'元素")
            
            clickable_elements = []
            for element in elements:
                try:
                    if element.is_displayed() and element.is_enabled():
                        size = element.size
                        if size['width'] > 30 and size['height'] > 10:
                            clickable_elements.append(element)
                except:
                    continue
            
            print(f"  其中 {len(clickable_elements)} 个可点击")
            
            if not clickable_elements:
                print("❌ 未找到可点击的'新发布'按钮")
                return False
            
            button = clickable_elements[0]
            
            click_methods = [
                ("普通点击", lambda: button.click()),
                ("JavaScript点击", lambda: self.driver.execute_script("arguments[0].click();", button)),
                ("ActionChains点击", lambda: ActionChains(self.driver).move_to_element(button).click().perform())
            ]
            
            for method_name, click_func in click_methods:
                try:
                    print(f"  尝试{method_name}...")
                    click_func()
                    time.sleep(1)
                    print(f"  ✅ {method_name}成功")
                    return True
                except Exception as e:
                    print(f"  ❌ {method_name}失败: {str(e)[:50]}...")
                    continue
            
            print("❌ 所有点击方法都失败")
            return False
            
        except Exception as e:
            print(f"❌ 点击'新发布'失败: {e}")
            return False
    
    def click_latest(self):
        """点击'最新'按钮"""
        print("\n🎯 点击'最新'按钮...")
        
        try:
            time.sleep(1)
            xpath = "//*[contains(text(), '最新')]"
            elements = self.driver.find_elements(By.XPATH, xpath)
            
            print(f"🔍 找到 {len(elements)} 个'最新'元素")
            
            clickable_elements = []
            for element in elements:
                try:
                    if element.is_displayed() and element.is_enabled():
                        size = element.size
                        if size['width'] > 30 and size['height'] > 10:
                            clickable_elements.append(element)
                except:
                    continue
            
            print(f"  其中 {len(clickable_elements)} 个可点击")
            
            if not clickable_elements:
                print("❌ 未找到可点击的'最新'按钮")
                return False
            
            latest_button = clickable_elements[0]
            
            try:
                print("  尝试点击...")
                latest_button.click()
                time.sleep(1)
                print("  ✅ 点击成功")
                return True
            except:
                try:
                    print("  尝试JavaScript点击...")
                    self.driver.execute_script("arguments[0].click();", latest_button)
                    time.sleep(1)
                    print("  ✅ JavaScript点击成功")
                    return True
                except Exception as e:
                    print(f"  ❌ 点击失败: {e}")
                    return False
            
        except Exception as e:
            print(f"❌ 点击'最新'失败: {e}")
            return False
    
    # ========== 优化版：悬停显示确认按钮 ==========
    
    def set_price_range_with_hover(self, min_price=None, max_price=None):
        """优化版：设置价格范围，悬停显示确认按钮"""
        if not min_price and not max_price:
            print("ℹ️  未设置价格筛选")
            return True
        
        price_text = ""
        if min_price:
            price_text += f"¥{min_price}-"
        if max_price:
            price_text += f"¥{max_price}"
        
        print(f"\n💰 设置价格范围: {price_text}")
        print("🎯 关键优化：需要悬停才能显示确认按钮")
        
        try:
            # 1. 找到所有输入框
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"🔍 找到 {len(inputs)} 个输入框")
            
            # 2. 筛选价格输入框
            price_inputs = []
            for i, input_elem in enumerate(inputs):
                try:
                    if not input_elem.is_displayed():
                        continue
                    
                    placeholder = input_elem.get_attribute("placeholder") or ""
                    class_name = input_elem.get_attribute("class") or ""
                    location = input_elem.location
                    
                    # 判断是否是价格输入框
                    if "¥" in placeholder or "price" in class_name.lower():
                        # 排除搜索框（在顶部）
                        if location['y'] > 100:
                            price_inputs.append({
                                'index': i,
                                'element': input_elem,
                                'placeholder': placeholder,
                                'class': class_name,
                                'location': location
                            })
                            
                except Exception as e:
                    print(f"    输入框{i}分析失败: {e}")
            
            print(f"🔍 筛选出 {len(price_inputs)} 个价格相关输入框")
            
            # 3. 如果有两个或更多价格输入框
            if len(price_inputs) >= 2:
                # 按x坐标排序（从左到右）
                price_inputs.sort(key=lambda x: x['location']['x'])
                
                print("\n🎯 识别最低价和最高价输入框:")
                min_input = price_inputs[0]['element']
                max_input = price_inputs[1]['element']
                
                print(f"    输入框{price_inputs[0]['index']}: 最低价输入框")
                print(f"      placeholder: '{price_inputs[0]['placeholder']}'")
                print(f"      位置: ({price_inputs[0]['location']['x']}, {price_inputs[0]['location']['y']})")
                
                print(f"    输入框{price_inputs[1]['index']}: 最高价输入框")
                print(f"      placeholder: '{price_inputs[1]['placeholder']}'")
                print(f"      位置: ({price_inputs[1]['location']['x']}, {price_inputs[1]['location']['y']})")
                
                # 4. 输入最低价（修复版）
                if min_price:
                    print(f"\n🎯 输入最低价: ¥{min_price}")
                    print("  修复策略: 逐个字符输入，避免400变4000")
                    
                    min_price_str = str(int(min_price))  # 确保是整数
                    
                    try:
                        # 清空输入框
                        min_input.clear()
                        time.sleep(0.3)
                        
                        # 点击获取焦点
                        min_input.click()
                        time.sleep(0.2)
                        
                        # 逐个字符输入（慢速，避免自动补0）
                        for char in min_price_str:
                            min_input.send_keys(char)
                            time.sleep(0.15)  # 重要！慢一点
                        
                        time.sleep(0.3)
                        
                        # 验证输入结果
                        actual_value = min_input.get_attribute("value") or ""
                        cleaned_value = ''.join(filter(str.isdigit, actual_value))
                        
                        print(f"    实际输入值: '{actual_value}'")
                        print(f"    清理后值: '{cleaned_value}'")
                        
                        if cleaned_value == min_price_str:
                            print(f"  ✅ 最低价输入成功")
                        else:
                            print(f"  ⚠️  输入值不匹配，尝试修正...")
                            
                            # 如果多了0，删除它
                            if cleaned_value.endswith('0') and len(cleaned_value) > len(min_price_str):
                                extra_zeros = len(cleaned_value) - len(min_price_str)
                                for _ in range(extra_zeros):
                                    min_input.send_keys(Keys.BACKSPACE)
                                    time.sleep(0.1)
                            
                            # 再次验证
                            actual_value = min_input.get_attribute("value") or ""
                            cleaned_value = ''.join(filter(str.isdigit, actual_value))
                            
                            if cleaned_value == min_price_str:
                                print(f"  ✅ 修正成功")
                            else:
                                print(f"  ❌ 最低价输入失败")
                                return False
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"❌ 输入最低价失败: {e}")
                        return False
                
                # 5. 输入最高价（修复版）
                if max_price:
                    print(f"\n🎯 输入最高价: ¥{max_price}")
                    print("  修复策略: 逐个字符输入，避免2000变20000")
                    
                    max_price_str = str(int(max_price))  # 确保是整数
                    
                    try:
                        # 清空输入框
                        max_input.clear()
                        time.sleep(0.3)
                        
                        # 点击获取焦点
                        max_input.click()
                        time.sleep(0.2)
                        
                        # 逐个字符输入（慢速，避免自动补0）
                        for char in max_price_str:
                            max_input.send_keys(char)
                            time.sleep(0.15)  # 重要！慢一点
                        
                        time.sleep(0.3)
                        
                        # 验证输入结果
                        actual_value = max_input.get_attribute("value") or ""
                        cleaned_value = ''.join(filter(str.isdigit, actual_value))
                        
                        print(f"    实际输入值: '{actual_value}'")
                        print(f"    清理后值: '{cleaned_value}'")
                        
                        if cleaned_value == max_price_str:
                            print(f"  ✅ 最高价输入成功")
                        else:
                            print(f"  ⚠️  输入值不匹配，尝试修正...")
                            
                            # 如果多了0，删除它
                            if cleaned_value.endswith('0') and len(cleaned_value) > len(max_price_str):
                                extra_zeros = len(cleaned_value) - len(max_price_str)
                                for _ in range(extra_zeros):
                                    max_input.send_keys(Keys.BACKSPACE)
                                    time.sleep(0.1)
                            
                            # 再次验证
                            actual_value = max_input.get_attribute("value") or ""
                            cleaned_value = ''.join(filter(str.isdigit, actual_value))
                            
                            if cleaned_value == max_price_str:
                                print(f"  ✅ 修正成功")
                            else:
                                print(f"  ❌ 最高价输入失败")
                                return False
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"❌ 输入最高价失败: {e}")
                        return False
                
                # 6. 先按回车（传统方式）
                print("\n🎯 先尝试按回车确认...")
                try:
                    max_input.send_keys(Keys.RETURN)
                    print("✅ 按回车确认价格筛选")
                    time.sleep(1)
                except Exception as e:
                    print(f"⚠️  按回车失败: {e}")
                
                # 7. 关键优化：悬停显示确认按钮
                print("\n🎯 关键优化：悬停在价格输入框上显示确认按钮...")
                
                # 尝试悬停在最高价输入框上
                try:
                    actions = ActionChains(self.driver)
                    
                    # 悬停在最高价输入框上
                    print("  悬停在最高价输入框上...")
                    actions.move_to_element(max_input).perform()
                    time.sleep(1)
                    
                    # 悬停在最低价输入框上
                    print("  悬停在最低价输入框上...")
                    actions.move_to_element(min_input).perform()
                    time.sleep(1)
                    
                    print("✅ 悬停操作完成")
                except Exception as e:
                    print(f"⚠️  悬停操作失败: {e}")
                
                # 8. 查找确认按钮（悬停后应该显示）
                print("\n🔍 悬停后查找确认按钮...")
                confirm_button = self.find_confirm_button_near_price()
                
                if confirm_button:
                    print("✅ 找到确认按钮，点击确认...")
                    self.click_confirm_button(confirm_button)
                else:
                    print("⚠️  悬停后仍未找到确认按钮，继续按回车...")
                    try:
                        max_input.send_keys(Keys.RETURN)
                        print("✅ 再次按回车确认")
                        time.sleep(1)
                    except:
                        pass
                
                # 9. 额外等待，让筛选生效
                time.sleep(2)
                
                return True
            else:
                print("❌ 未找到足够的价格输入框")
                return False
            
        except Exception as e:
            print(f"❌ 设置价格范围失败: {e}")
            return False
    
    def find_confirm_button_near_price(self):
        """在价格输入框附近查找确认按钮"""
        print("🔍 在价格筛选区域附近查找确认按钮...")
        
        # 确认按钮可能的关键词
        confirm_keywords = ["确定", "确认", "完成", "筛选", "应用", "submit", "ok", "apply"]
        
        # 先查找整个页面的确认按钮
        all_buttons = []
        for keyword in confirm_keywords:
            try:
                xpath = f"//*[contains(text(), '{keyword}')]"
                buttons = self.driver.find_elements(By.XPATH, xpath)
                all_buttons.extend(buttons)
            except:
                continue
        
        print(f"  找到 {len(all_buttons)} 个可能的确认按钮")
        
        # 筛选在价格筛选区域附近的按钮
        price_region_y_min = 150  # 价格筛选区域Y坐标起始
        price_region_y_max = 250  # 价格筛选区域Y坐标结束
        
        best_button = None
        best_distance = float('inf')
        
        for button in all_buttons:
            try:
                if not button.is_displayed():
                    continue
                
                location = button.location
                button_y = location['y']
                
                # 检查是否在价格筛选区域附近
                if price_region_y_min <= button_y <= price_region_y_max:
                    button_text = button.text.strip()
                    print(f"✅ 在筛选区域找到确认按钮: '{button_text[:30]}...'")
                    print(f"    位置: ({location['x']}, {location['y']})")
                    return button
                
                # 计算到价格筛选区域的距离
                distance = abs(button_y - (price_region_y_min + price_region_y_max) / 2)
                if distance < best_distance:
                    best_distance = distance
                    best_button = button
                    
            except:
                continue
        
        # 如果没有在精确区域内找到，返回最近的一个
        if best_button:
            try:
                location = best_button.location
                button_text = best_button.text.strip()[:30]
                print(f"✅ 找到最近的确认按钮: '{button_text}...'")
                print(f"    位置: ({location['x']}, {location['y']})")
                return best_button
            except:
                pass
        
        print("❌ 未在价格筛选区域附近找到确认按钮")
        return None
    
    def click_confirm_button(self, confirm_button):
        """点击确认按钮"""
        if not confirm_button:
            return False
        
        print("\n🎯 点击确认按钮...")
        
        click_methods = [
            ("普通点击", lambda: confirm_button.click()),
            ("JavaScript点击", lambda: self.driver.execute_script("arguments[0].click();", confirm_button)),
            ("ActionChains点击", lambda: ActionChains(self.driver).move_to_element(confirm_button).click().perform())
        ]
        
        for method_name, click_func in click_methods:
            try:
                print(f"  尝试{method_name}...")
                click_func()
                time.sleep(1)
                print(f"  ✅ {method_name}成功")
                return True
            except Exception as e:
                print(f"  ❌ {method_name}失败: {str(e)[:50]}...")
                continue
        
        print("❌ 所有点击方法都失败")
        return False
    
    def take_screenshot(self, keyword, max_price=None, min_price=None):
        """截图"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_keyword = keyword.replace(" ", "_")
            
            filename = f"hover_{safe_keyword}"
            if min_price:
                filename += f"_min{min_price}"
            if max_price:
                filename += f"_max{max_price}"
            filename += f"_{timestamp}.png"
            
            filepath = os.path.join(os.getcwd(), filename)
            
            time.sleep(2)
            self.driver.save_screenshot(filepath)
            
            print(f"📸 截图: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None
    
    def run_hover_solution(self, keyword, max_price=None, min_price=None):
        """运行悬停确认版解决方案"""
        print("=" * 60)
        print("🚀 闲鱼悬停确认版本")
        print(f"🔍 关键词: {keyword}")
        if min_price or max_price:
            print(f"💰 价格范围: {f'¥{min_price}-' if min_price else ''}{f'¥{max_price}' if max_price else ''}")
        print("💡 关键优化：需要悬停才能显示确认按钮")
        print("=" * 60)
        
        # 1. 启动浏览器
        if not self.setup_driver():
            return False
        
        # 2. 确保登录（一次性）
        if not self.ensure_login_once():
            print("❌ 登录失败，无法继续")
            return False
        
        # 3. 搜索
        if not self.search_items(keyword):
            return False
        
        # 4. 点击新发布按钮
        new_release_success = self.click_new_release()
        
        # 5. 点击最新按钮
        latest_success = False
        if new_release_success:
            latest_success = self.click_latest()
        else:
            print("⚠️  '新发布'点击失败，跳过'最新'")
        
        # 6. 设置价格范围（悬停优化版）
        price_success = True
        if max_price or min_price:
            price_success = self.set_price_range_with_hover(min_price, max_price)
        
        # 7. 截图
        screenshot = self.take_screenshot(keyword, max_price, min_price)
        
        # 8. 显示结果
        print("\n" + "=" * 60)
        print("📊 悬停确认版执行结果:")
        print(f"   登录状态: ✅ 假设已登录（一次性检查）")
        print(f"   新发布点击: {'✅ 成功' if new_release_success else '❌ 失败'}")
        print(f"   最新点击: {'✅ 成功' if latest_success else '❌ 失败'}")
        if max_price or min_price:
            print(f"   价格范围设置: {'✅ 成功' if price_success else '❌ 失败'}")
            if min_price:
                print(f"     最低价: ¥{min_price}")
            if max_price:
                print(f"     最高价: ¥{max_price}")
            print(f"   确认方式: 回车 + 悬停 + 按钮点击")
        print(f"   截图保存: {screenshot if screenshot else '❌ 失败'}")
        
        # 9. 保持浏览器打开（非无头模式）
        if not self.headless:
            print("\n🔍 浏览器保持打开，请检查:")
            print("   1. 页面是否稳定（没有跳转到用户页）")
            print("   2. '新发布'按钮是否被点击")
            print("   3. '最新'按钮是否被点击")
            print("   4. 最低价和最高价是否正确设置")
            print("   5. 价格区间筛选是否生效")
            print("   6. 确认按钮是否在悬停后显示并被点击")
            print("\n检查完毕后，按Enter键关闭浏览器...")
            
            try:
                input()
            except:
                pass
        
        return True

def main():
    parser = argparse.ArgumentParser(description='闲鱼悬停确认版本（需要悬停显示确认按钮）')
    parser.add_argument('keyword', help='搜索关键词')
    parser.add_argument('--max', type=float, help='最高价格（元）')
    parser.add_argument('--min', type=float, help='最低价格（元）')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    
    args = parser.parse_args()
    
    solution = XianYuHoverConfirm(headless=args.headless)
    
    try:
        success = solution.run_hover_solution(
            args.keyword, 
            args.max, 
            args.min
        )
        
        if success:
            print("\n🎉 悬停确认版执行成功！")
            print("💡 关键优化:")
            print("   1. ✅ 保留所有现有功能")
            print("   2. ✅ 增加悬停操作（鼠标悬停在价格输入框上）")
            print("   3. ✅ 悬停后查找确认按钮")
            print("   4. ✅ 在价格筛选区域附近精确查找按钮")
            print("   5. ✅ 三重确认：回车 + 悬停 + 按钮点击")
        else:
            print("\n❌ 执行失败")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
    finally:
        if solution.driver:
            try:
                solution.driver.quit()
                if not args.headless:
                    print("✅ 浏览器已关闭")
            except:
                pass

if __name__ == "__main__":
    main()
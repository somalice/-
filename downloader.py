import time
import random
import logging
import subprocess
import os
import sys
import re
import zipfile
import socket

class WSYDownloader:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        self.logger = logging.getLogger('WSYDownloader')
        self.browser = None
        self.playwright = None
        self.context = None
        self.page = None
        self.is_logged_in = False
        self.is_running = False
        self.should_stop = False
        
        self.CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.DEBUG_PORT = 9222
        # 使用参考文件的方式，指定一个配置目录
        self.CHROME_PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chrome_profile")

    def set_logger(self, logger):
        self.logger = logger

    def random_delay(self, min_delay=1, max_delay=3):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def is_debug_port_open(self):
        """检查Chrome调试端口是否开启"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex(('localhost', self.DEBUG_PORT)) == 0
        except Exception as e:
            self.logger.debug(f'端口检查异常: {e}')
            return False

    def is_chrome_running(self):
        """检查Chrome是否正在运行"""
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], 
                                  capture_output=True, text=True)
            return 'chrome.exe' in result.stdout
        except:
            return False

    def start_chrome_with_profile(self):
        """参考文件方式：使用配置目录启动Chrome"""
        try:
            if not os.path.exists(self.CHROME_PATH):
                self.logger.error(f'Chrome可执行文件不存在: {self.CHROME_PATH}')
                return False

            # 创建配置目录（如果不存在）
            if not os.path.exists(self.CHROME_PROFILE_DIR):
                os.makedirs(self.CHROME_PROFILE_DIR)
                self.logger.info(f'✓ 创建配置目录: {self.CHROME_PROFILE_DIR}')

            self.logger.info(f'Chrome 路径: {self.CHROME_PATH}')
            self.logger.info(f'配置目录: {self.CHROME_PROFILE_DIR}')

            # 构建启动命令 - 参照参考文件的方式，直接跳转到金牌档口
            cmd = [
                self.CHROME_PATH,
                "--remote-debugging-port=9222",
                "--start-maximized",
                f"--user-data-dir={self.CHROME_PROFILE_DIR}",
                "https://www.wsy.com/new/goldStall"
            ]
            self.logger.info(f'启动命令: {" ".join(cmd)}')

            # 先关闭所有Chrome实例，避免冲突
            self.logger.info('正在关闭所有Chrome实例...')
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'],
                         capture_output=True, stderr=subprocess.DEVNULL)

            # 等待Chrome完全关闭
            self.logger.info('等待Chrome完全关闭...')
            time.sleep(5)

            # 启动Chrome
            self.logger.info('正在启动Chrome调试模式...')
            subprocess.Popen(cmd)
            self.logger.info('✓ Chrome调试模式已启动！')

            return True

        except Exception as e:
            self.logger.error(f'启动Chrome失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def start_chrome(self):
        """连接到Chrome并跳转到金牌档口"""
        self.logger.info('正在连接到Chrome浏览器...')

        # 检查调试端口是否开启
        if self.is_debug_port_open():
            self.logger.info('检测到Chrome调试端口已开启，正在连接...')
            return self.connect_and_go_to_goldstall()

        # 检查Chrome是否正在运行
        if self.is_chrome_running():
            self.logger.error('检测到Chrome正在运行！')
            self.logger.error('=' * 60)
            self.logger.error('请先关闭所有Chrome浏览器窗口！')
            self.logger.error('关闭后，再次点击按钮')
            self.logger.error('=' * 60)
            return False

        # 启动新的Chrome
        self.logger.info('正在启动Chrome...')
        if not self.start_chrome_with_profile():
            self.logger.error('启动Chrome失败！')
            return False

        # 等待端口就绪
        timeout = 60
        start_time = time.time()
        self.logger.info(f'等待Chrome调试端口就绪...')

        while not self.is_debug_port_open():
            time.sleep(2)
            elapsed = time.time() - start_time
            if elapsed > timeout:
                self.logger.error('Chrome启动超时！')
                self.logger.error('请手动检查Chrome是否成功启动')
                return False
            self.logger.info(f'等待Chrome就绪... {int(elapsed)}/{timeout}秒')

        self.logger.info('Chrome调试端口已就绪！')

        return self.connect_and_go_to_goldstall()

    def connect_and_go_to_goldstall(self):
        """参考文件方式：连接到Chrome并跳转"""
        try:
            from playwright.sync_api import sync_playwright

            self.logger.info('正在通过CDP连接到Chrome...')

            self.playwright = sync_playwright().start()

            try:
                self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
            except Exception as cdp_error:
                self.logger.error(f'CDP连接失败: {str(cdp_error)}')
                if self.playwright:
                    self.playwright.stop()
                return False

            self.logger.info('✓ 成功连接到Chrome！')

            if self.browser.contexts:
                self.context = self.browser.contexts[0]
                self.logger.info('✓ 使用现有浏览器上下文')
            else:
                self.context = self.browser.new_context(accept_downloads=True)
                self.logger.info('✓ 创建新浏览器上下文')

            # 参照参考文件的方式：创建新页面
            self.page = self.context.new_page()
            self.logger.info('✓ 已在Chrome中新增页签！')

            self.logger.info('正在跳转到金牌档口页面...')
            self.page.goto("https://www.wsy.com/new/goldStall")
            time.sleep(5)  # 参照参考文件的等待方式
            self.logger.info('✓ 成功跳转到金牌档口！')

            self.is_logged_in = True
            return True

        except Exception as e:
            self.logger.error(f'连接Chrome失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
            return False

    def click_first_stall(self):
        """点击第一个店铺"""
        self.logger.info('📍 正在点击第一个店铺...')

        try:
            stall_selector = 'div.stall-item:first-child .s-name a'
            self.page.wait_for_selector(stall_selector, timeout=30000)
            self.page.click(stall_selector)
            self.logger.info('✅ 已点击第一个店铺')

            self.random_delay(2, 3)

            return True

        except Exception as e:
            self.logger.error(f'点击店铺失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def click_first_product(self):
        """点击第一件商品 - 优化选择器顺序，缩短超时时间"""
        self.logger.info('📍 正在点击第一件商品...')

        selectors = [
            'img.lazy',
            'a:has(img.lazy)',
            'ul.clearfix.goods-list li:first-child div.image-con a',
            'ul.goods-list li:first-child .goods-img a',
            '.goods-item:first-child .goods-img a',
            '.goods-item:first-child a',
            '.product-item:first-child img',
            'div.goods-list div.item:first-child a',
            'li:first-child a:has(img)'
        ]

        try:
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    self.page.click(selector)
                    self.logger.info(f'✅ 已点击第一件商品 (选择器: {selector})')
                    self.random_delay(2, 3)
                    return True
                except:
                    self.logger.info(f'尝试选择器 {selector} 失败，尝试下一个...')
            
            self.logger.error('✗ 未找到商品选择器')
            return False

        except Exception as e:
            self.logger.error(f'点击商品失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def click_one_key_download(self):
        """点击一键下载按钮 - 简单直接的方式"""
        self.logger.info('📍 正在点击「一键下载」按钮...')

        selectors = [
            'div.fs-item-btn a.item-btn-addtp',
            '.fs-item-btn a.item-btn-addtp',
            'a.item-btn-addtp',
            '.item-btn-addtp',
            'a.J_pic_upload',
            'a:has(.iconicon_down)'
        ]

        try:
            for selector in selectors:
                try:
                    self.logger.info(f'尝试选择器: {selector}')
                    self.page.wait_for_selector(selector, timeout=3000)
                    self.page.click(selector)
                    self.logger.info(f'✅ 已点击「一键下载」按钮 (选择器: {selector})')
                    self.random_delay(3, 5)
                    return True
                except Exception as e:
                    self.logger.info(f'尝试选择器 {selector} 失败，尝试下一个...')
            
            self.logger.info('尝试通过文本内容查找...')
            try:
                all_links = self.page.locator('a')
                total = all_links.count()
                self.logger.info(f'页面上共有 {total} 个链接')
                
                for i in range(min(total, 50)):
                    try:
                        text = all_links.nth(i).text_content()
                        if text and '一键下载' in text:
                            self.logger.info(f'找到包含"一键下载"的链接，索引: {i}')
                            all_links.nth(i).scroll_into_view_if_needed()
                            self.random_delay(1, 2)
                            all_links.nth(i).click()
                            self.logger.info('✅ 通过文本查找点击成功')
                            self.random_delay(3, 5)
                            return True
                    except Exception as e:
                        continue
            except Exception as e:
                self.logger.info(f'文本查找失败: {str(e)[:50]}...')
            
            self.logger.error('✗ 未找到一键下载按钮')
            return False

        except Exception as e:
            self.logger.error(f'点击一键下载失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def click_detail_download(self):
        """点击详情图下载按钮 - 简单直接的方式"""
        self.logger.info('📍 正在点击「详情图」下载按钮...')

        selectors = [
            '#picupload',
            'a:has-text("下载")',
            'button:has-text("下载")',
            '.cloud-box a',
            'div:has-text("详情图") a'
        ]

        try:
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    self.page.click(selector)
                    self.logger.info(f'✅ 已点击详情图下载按钮 (选择器: {selector})')
                    self.random_delay(2, 3)
                    return True
                except Exception as e:
                    self.logger.info(f'尝试选择器 {selector} 失败，尝试下一个...')
            
            self.logger.error('✗ 未找到详情图下载按钮')
            return False

        except Exception as e:
            self.logger.error(f'点击详情图下载失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def start_download(self, shop_link=None):
        """执行自动化下载流程 - 单连接完成所有操作"""
        self.logger.info('=' * 60)
        self.logger.info('开始自动化下载流程')
        self.logger.info('=' * 60)

        try:
            from playwright.sync_api import sync_playwright

            if not shop_link:
                self.logger.error('✗ 需要提供店铺链接')
                return False

            # 步骤1：连接到 Chrome
            self.logger.info('📍 步骤1/5: 连接到Chrome')
            self.playwright = sync_playwright().start()
            
            try:
                self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
            except Exception as cdp_error:
                self.logger.error(f'CDP连接失败: {str(cdp_error)}')
                if self.playwright:
                    self.playwright.stop()
                return False

            self.logger.info('✓ 成功连接到Chrome！')

            if self.browser.contexts:
                self.context = self.browser.contexts[0]
                self.logger.info('✓ 使用现有浏览器上下文')
            else:
                self.context = self.browser.new_context(accept_downloads=True)
                self.logger.info('✓ 创建新浏览器上下文')

            # 创建新页面
            self.page = self.context.new_page()
            self.logger.info('✓ 已在Chrome中新增页签！')

            # 步骤2：跳转到店铺链接
            self.logger.info('📍 步骤2/5: 跳转到店铺链接')
            clean_link = shop_link.strip().strip('`').strip()
            self.logger.info(f'准备跳转到: {clean_link}')
            try:
                self.page.goto(clean_link, timeout=30000, wait_until='domcontentloaded')
            except:
                pass
            time.sleep(5)
            self.logger.info(f'✓ 成功跳转到: {clean_link}')

            # 步骤3：获取并跳转到第一个商品详情页
            self.logger.info('📍 步骤3/5: 获取第一个商品链接并跳转到商品详情页')
            
            product_link = None
            
            # 方法1: 使用 href*=item.htm?id=
            try:
                links = self.page.locator("a[href*='item.htm?id=']")
                if links.count() > 0:
                    href = links.first.get_attribute("href")
                    if href:
                        product_link = href
                        self.logger.info(f'✅ 使用方法1获取到商品链接: {product_link}')
            except Exception as e:
                self.logger.info(f'方法1出错: {e}')
            
            # 方法2: 使用 img.lazy 找外层链接
            if not product_link:
                try:
                    for selector in ['a:has(img.lazy)', 'ul.clearfix.goods-list li:first-child a', 'ul.goods-list li:first-child a']:
                        elem = self.page.locator(selector).first
                        if elem.is_visible():
                            href = elem.get_attribute("href")
                            if href:
                                product_link = href
                                self.logger.info(f'✅ 使用方法2获取到商品链接: {product_link}')
                                break
                except Exception as e:
                    self.logger.info(f'方法2出错: {e}')
            
            if not product_link:
                self.logger.error('✗ 未找到商品链接')
                return False
            
            # 处理相对链接
            if not product_link.startswith("http"):
                product_link = "https://cs.wsy.com" + product_link
            
            # 跳转到商品详情页
            self.logger.info(f'正在跳转到商品详情页: {product_link}')
            try:
                self.page.goto(product_link, timeout=30000, wait_until="domcontentloaded")
            except:
                pass
            time.sleep(5)
            self.logger.info('✅ 已跳转到商品详情页')

            # 步骤4：点击一键下载按钮
            self.logger.info('📍 步骤4/5: 点击一键下载按钮')
            
            # 等待页面加载完成
            time.sleep(2)
            
            # 参考 gui_ultimate_final_v2.py 的实现方式
            found_download = False
            try:
                self.logger.info('尝试使用 .item-btn-addtp 选择器...')
                one_click_download = self.page.locator(".item-btn-addtp").first
                if one_click_download.is_visible():
                    self.logger.info('找到一键下载按钮，点击...')
                    one_click_download.click()
                    self.logger.info('✅ 已点击一键下载按钮')
                    found_download = True
                    time.sleep(1)
                else:
                    self.logger.info('.item-btn-addtp 按钮不可见')
            except Exception as e:
                self.logger.info(f'选择器 .item-btn-addtp 失败: {str(e)[:80]}...')
            
            # 如果选择器失败，尝试 JavaScript 方式
            if not found_download:
                self.logger.info('使用JavaScript查找一键下载按钮...')
                try:
                    js_result = self.page.evaluate('''
                        () => {
                            const links = Array.from(document.querySelectorAll('a'));
                            for (let link of links) {
                                if (link.textContent.includes('一键下载') && link.className.includes('item-btn-addtp')) {
                                    link.click();
                                    return true;
                                }
                            }
                            return false;
                        }
                    ''')
                    if js_result:
                        self.logger.info('✅ 已通过JavaScript点击一键下载按钮')
                        found_download = True
                        time.sleep(3)
                    else:
                        self.logger.info('JavaScript未找到按钮')
                except Exception as e:
                    self.logger.info(f'JavaScript查找失败: {str(e)[:80]}...')
            
            if not found_download:
                self.logger.error('✗ 未找到一键下载按钮')
                return False

            # 步骤5：点击详情图下载按钮
            self.logger.info('📍 步骤5/5: 点击详情图下载按钮')
            detail_selectors = [
                '#picupload',
                'a:has-text("下载")',
                'button:has-text("下载")',
                '.cloud-box a'
            ]
            found_detail = False
            for selector in detail_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    self.page.click(selector)
                    self.logger.info(f'✅ 已点击详情图下载按钮 (选择器: {selector})')
                    found_detail = True
                    time.sleep(2)
                    break
                except Exception as e:
                    continue
            
            if not found_detail:
                self.logger.error('✗ 未找到详情图下载按钮')
                return False

            self.logger.info('=' * 60)
            self.logger.info('✅ 自动化下载流程完成！')
            self.logger.info('=' * 60)
            return True

        except Exception as e:
            self.logger.error(f'下载流程出错: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def go_to_link(self, link):
        """跳转到用户指定的链接 - 完全参考金牌档口逻辑"""
        clean_link = link.strip().strip('`').strip()
        self.logger.info(f'正在通过CDP连接到Chrome...')

        try:
            from playwright.sync_api import sync_playwright

            self.playwright = sync_playwright().start()

            try:
                self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
            except Exception as cdp_error:
                self.logger.error(f'CDP连接失败: {str(cdp_error)}')
                if self.playwright:
                    self.playwright.stop()
                return False

            self.logger.info('✓ 成功连接到Chrome！')

            if self.browser.contexts:
                self.context = self.browser.contexts[0]
                self.logger.info('✓ 使用现有浏览器上下文')
            else:
                self.context = self.browser.new_context(accept_downloads=True)
                self.logger.info('✓ 创建新浏览器上下文')

            self.page = self.context.new_page()
            self.logger.info('✓ 已在Chrome中新增页签！')

            self.logger.info(f'正在跳转到: {clean_link}')
            self.page.goto(clean_link)
            time.sleep(5)
            self.logger.info(f'✓ 成功跳转到: {clean_link}')

            self.is_logged_in = True
            return True

        except Exception as e:
            self.logger.error(f'跳转失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
            return False

    def go_to_goldstall(self):
        """单独的跳转方法：在已打开的Chrome中跳转到金牌档口"""
        self.logger.info('[DEBUG] 进入 go_to_goldstall 方法...')
        
        try:
            from playwright.sync_api import sync_playwright

            self.logger.info('[DEBUG] 检查调试端口是否开启...')
            if not self.is_debug_port_open():
                self.logger.error('❌ 调试端口未开启！')
                self.logger.error('请先启动Chrome调试模式！')
                return False
            
            self.logger.info('✓ 调试端口已开启！')
            self.logger.info('正在通过CDP连接到Chrome...')

            self.playwright = sync_playwright().start()
            self.logger.info('[DEBUG] Playwright 已启动！')

            try:
                self.logger.info('[DEBUG] 正在连接 CDP...')
                self.browser = self.playwright.chromium.connect_over_cdp("http://localhost:9222")
                self.logger.info('[DEBUG] CDP 连接成功！')
            except Exception as cdp_error:
                self.logger.error(f'CDP连接失败: {str(cdp_error)}')
                self.logger.error('请确保Chrome已启动并开启了调试模式！')
                if self.playwright:
                    self.playwright.stop()
                return False

            self.logger.info('✓ 成功连接到Chrome！')

            self.logger.info(f'[DEBUG] 上下文数量: {len(self.browser.contexts)}')
            if self.browser.contexts:
                self.context = self.browser.contexts[0]
                self.logger.info('✓ 使用现有浏览器上下文')
            else:
                self.context = self.browser.new_context(accept_downloads=True)
                self.logger.info('✓ 创建新浏览器上下文')

            # 使用现有页面或创建新页面
            self.logger.info(f'[DEBUG] 页面数量: {len(self.context.pages)}')
            if self.context.pages:
                self.page = self.context.pages[0]
                self.logger.info('✓ 使用现有Chrome页面')
            else:
                self.logger.info('[DEBUG] 正在创建新页面...')
                self.page = self.context.new_page()
                self.logger.info('✓ 创建新页面')

            self.logger.info('正在跳转到金牌档口页面...')
            self.logger.info('[DEBUG] 执行 self.page.goto...')
            result = self.page.goto("https://www.wsy.com/new/goldStall")
            self.logger.info(f'[DEBUG] goto 完成！状态: {result.status if result else "None"}')
            
            self.logger.info('[DEBUG] 等待 5 秒...')
            time.sleep(5)  # 等待页面加载
            self.logger.info('✓ 成功跳转到金牌档口！')

            self.is_logged_in = True
            return True

        except Exception as e:
            self.logger.error(f'跳转失败: {str(e)}')
            import traceback
            self.logger.error(traceback.format_exc())
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
            return False

    def close_browser(self):
        """关闭连接"""
        try:
            if self.page:
                try:
                    self.page.close()
                except:
                    pass
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
            self.is_logged_in = False
            self.logger.info('已断开浏览器连接')
        except Exception as e:
            self.logger.error(f'断开连接出错: {str(e)}')

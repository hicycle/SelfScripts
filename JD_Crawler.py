# -*- coding: utf-8 -*-
```
关注店铺获取京豆脚本
版本：v1.0
```
import os
import re
import requests
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException


class JD_Crawler:
    def __init__(self, exe_path="C:/Temp/geckodriver.exe"):
        firefox_opt = Options()
        firefox_opt.set_headless(headless=True)
        self.driver = webdriver.Firefox(executable_path=exe_path, options=firefox_opt)

    def login(self):
        login_url = "https://passport.jd.com/new/login.aspx"
        self.driver.get(login_url)
        # 选择登陆方式 账户登录
        self.driver.find_element_by_class_name('login-tab-r').click()
        self.driver.find_element_by_id('loginname').send_keys(input('用户名:'))
        self.driver.find_element_by_id('nloginpwd').send_keys(input('密码:'))

        auth = self.driver.find_element_by_id('JD_Verification1')
        input_authcode = self.driver.find_element_by_id('authcode')

        if auth.is_displayed():
            auth.screenshot('authcode.png')
            input_authcode.send_keys(input("输入验证码:"))

        self.driver.find_element_by_id('loginsubmit').click()
        time.sleep(2)

        while (self.driver.current_url != 'https://www.jd.com/'):
            self.driver.save_screenshot('test.png')
            if "账户名与密码不匹配，请重新输入" in self.driver.page_source:
                exit(1)
            if auth.is_displayed():
                auth.screenshot('authcode.png')
                input_authcode.send_keys(input("输入验证码:"))
                self.driver.find_element_by_id('loginsubmit').click()
            time.sleep(1)
        self.driver.save_screenshot('test.png')
        print('登陆成功')

# 关注店铺

    def GuanZhu(self, new_shopids):
        for new_shopid in new_shopids:
            self.driver.get("https://mall.jd.com/index-%s.html" % new_shopid)
            time.sleep(2)
            print('等待2s页面载入...')
            try:
                self.driver.find_element_by_class_name('J_drawGift').click()
                print('关注成功：', self.driver.title.strip())
                # self.driver.save_screenshot(self.driver.current_url[26:][:-5] + '_OK.png')
            except NoSuchElementException:
                print('无效的店铺:', self.driver.current_url[26:][:-5], self.driver.title.strip())
                if len(self.driver.current_url[26:][:-5]) < 1:
                    print(self.driver.current_url)
                    self.driver.save_screenshot(new_shopid + '.png')
                    # with open('unknow_error.log', 'a') as f:
                    #     f.write(self.driver.page_source)
                # self.driver.save_screenshot(self.driver.current_url[26:][:-5] + '_NOK.png')

# 店铺签到

    def Qiandao(self, new_shopids):
        for new_shopid in new_shopids:
            self.driver.get("https://mall.jd.com/shopSign-%s.html" % new_shopid)
            time.sleep(1)
            if "everyday-area J_everyday_area big-award" in self.driver.page_source:
                print('签到成功：', new_shopid, self.driver.title.strip())
            else:
                print('无效店铺：', new_shopid, self.driver.title.strip())


# 取消关注店铺

    def unfollow(self):
        self.driver.get('https://t.jd.com/vender/followVenderList.action')
        while ("您还没有关注过任何店铺哦" not in self.driver.page_source):
            self.driver.find_element_by_class_name('batch-btn').click()
            self.driver.find_element_by_class_name('u-check').click()
            self.driver.find_element_by_class_name('u-unfollow').click()
            self.driver.find_element_by_class_name('ui-dialog-btn-submit').click()
            time.sleep(1)

    def check_jb_num(self):
        self.driver.get("https://bean.jd.com/myJingBean/list")
        num_jb = self.driver.find_element_by_class_name("bi-number")
        print(num_jb.text)

    def quit(self):
        self.driver.quit()

    def manual(self, new_xianbao):
        self.login()
        self.check_jb_num()
        pattern1 = re.compile(r'href="https://mall.jd.com/index-(.*?).html', re.S)
        pattern2 = re.compile(r'href="https://mall.jd.com/shopSign-(.*?).html', re.S)
        Guanzhu_shopids = set()
        Qiandao_shopids = set()
        if os.path.exists("Guanzhu_shopids.txt"):
            with open('Guanzhu_shopids.txt', 'r') as f:
                Guanzhu_shopids = set(f.readline().split(','))
        if os.path.exists("Qiandao_shopids.txt"):
            with open('Qiandao_shopids.txt', 'r') as f:
                Qiandao_shopids = set(f.readline().split(','))
        if new_xianbao == 'Y' or new_xianbao == 'y':
            while True:
                xianbao = input("输入线报地址:")
                if xianbao != 'no':
                    html = requests.get(xianbao)
                    _Guanzhu_shopids = set(re.findall(pattern1, html.text))
                    _Qiandao_shopids = set(re.findall(pattern2, html.text))
                    self.GuanZhu(list(_Guanzhu_shopids - Guanzhu_shopids))
                    self.Qiandao(_Qiandao_shopids - Qiandao_shopids)
                    Guanzhu_shopids = Guanzhu_shopids | _Guanzhu_shopids
                    Qiandao_shopids = Qiandao_shopids | _Qiandao_shopids
                    with open('Guanzhu_shopids.txt', 'w') as f:
                        f.write(','.join(Guanzhu_shopids))
                    with open('Qiandao_shopids.txt', 'w') as f:
                        f.write(','.join(Qiandao_shopids))
                    self.check_jb_num()
                else:
                    break
        else:
            self.GuanZhu(list(Guanzhu_shopids))
            self.Qiandao(Qiandao_shopids)
        self.unfollow()
        self.check_jb_num()
        self.quit()

    def auto(self, xbs):
            self.login()
            self.check_jb_num()
            pattern1 = re.compile(r'href="https://mall.jd.com/index-(.*?).html', re.S)
            pattern2 = re.compile(r'href="https://mall.jd.com/shopSign-(.*?).html', re.S)
            Guanzhu_shopids = set()
            Qiandao_shopids = set()
            if os.path.exists("Guanzhu_shopids.txt"):
                with open('Guanzhu_shopids.txt', 'r') as f:
                    Guanzhu_shopids = set(f.readline().split(','))
            if os.path.exists("Qiandao_shopids.txt"):
                with open('Qiandao_shopids.txt', 'r') as f:
                    Qiandao_shopids = set(f.readline().split(','))
            for xb in xbs:
                xianbao = "http://www.0818tuan.com/xb/%s.html" % xb[0]
                html = requests.get(xianbao)
                _Guanzhu_shopids = set(re.findall(pattern1, html.text))
                _Qiandao_shopids = set(re.findall(pattern2, html.text))
                self.GuanZhu(list(_Guanzhu_shopids - Guanzhu_shopids))
                self.Qiandao(_Qiandao_shopids - Qiandao_shopids)
                Guanzhu_shopids = Guanzhu_shopids | _Guanzhu_shopids
                Qiandao_shopids = Qiandao_shopids | _Qiandao_shopids
                with open('Guanzhu_shopids.txt', 'w') as f:
                    f.write(','.join(Guanzhu_shopids))
                with open('Qiandao_shopids.txt', 'w') as f:
                    f.write(','.join(Qiandao_shopids))
            self.unfollow()
            self.check_jb_num()
            self.quit()

def get_xianbao():
    page = requests.get("http://www.0818tuan.com/plus/0818search.php?kwtype=0&q=%B6%B9")
    pattern = re.compile(r'<li class="list-group-item">.*?/xb/(.*?).html.*?<span.*?>(.*?)</span> </li>',re.S)
    pattern_next = re.compile(r"<td width='50'><a href='(.*?)'>下一页</a></td>", re.S)
    xbs = re.findall(pattern, page.text)
    next_add = re.findall(pattern_next, page.text)[0]
    # xbs += re.findall(pattern, requests.get("http://www.0818tuan.com/" + next_add).text)
    return xbs
        


if __name__ == '__main__': 
    while True:
        jd = JD_Crawler()
        choice = input("手动 or 自动 or 退出(M/A/Q):")
        if choice == 'M' or choice == 'm':
            jd.manual(input("是否有新线报(Y/N):"))
        elif choice == 'A' or choice == 'a':
            jd.auto(get_xianbao())
        elif choice == 'Q' or choice == 'q':
            break
        else:
            continue

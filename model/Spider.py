from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

class Spider:
    def __init__(self, driver):
        self.driver = driver

    def getPage(self):
        page_content = self.driver.page_source
        # 將 HTML 內容轉換成 BeautifulSoup 物件，html.parser 為使用的解析器
        soup = BeautifulSoup(page_content, 'html.parser')
        # 透過 select 使用 CSS 選擇器 選取我們要選的 html 內容
        return soup.select('.jftiEf.fontBodyMedium')

    def scrollPage(self,times):   # 滾動頁面
        counter = 0
        while counter <= times:
            pane = self.driver.find_element("xpath",'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", pane)
            time.sleep(1)
            counter += 1

    def openFullComment(self,elements):   # 展開所有留言
        for element in elements:
            target = self.driver.find_elements(By.CSS_SELECTOR, '.MyEned span button')
            # 判斷有「全文」按鈕，就點擊展開
            if target:
                more = self.driver.find_element(By.CSS_SELECTOR,'.MyEned span button.w8nwRe.kyuRq')
                more.click()

    def getCommentStar(self,element):
        for i  in range(1, 6):
            star_type = len(element.select('span.kvMYJc > img:nth-child({})'.format(i))[0].get('class'))
            if i == 5 and star_type == 2:
                star = i
                break
            if star_type != 2:
                star = i-1
                break 
        return star
    
    def getElement(self):  # 抓取目前的所有留言
        row_list = []
        self.scrollPage(5)
        elements = self.getPage()
        self.openFullComment(elements)
        elements = self.getPage()

        for element in elements:
            # 抓時間、星數、留言
            user = element.select('.d4r55')[0].text
            setTime = element.select('.rsqaWe')[0].text
            star = self.getCommentStar(element)
            content = element.select('span.wiI7pd')[0].text if len(element.select('span.wiI7pd')) != 0 else ""

            data = {}
            data['name'] = user
            data['setTime'] = setTime
            data['star'] = star
            data['content'] = content
            row_list.append(data)
        return row_list

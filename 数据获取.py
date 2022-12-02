from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import time
import requests
from bs4 import BeautifulSoup
import csv


def get_links(url):
    option = ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    bro = webdriver.Chrome(options=option)
    bro.get(url)
    # 等待一下，手工下拉加载
    time.sleep(15)
    # 获取每日疫情通报的推文链接，存在列表中，发现此集合漏了5日的，手动找到他5日的推文链接
    links = ['https://mp.weixin.qq.com/s/7_k5dzz8-grObLvIGzaCIw']
    elements = bro.find_elements(by=By.XPATH, value='/html/body/div[1]/div[1]/div/div[5]/ul/li')
    for i in elements[:27]:
        data_link = i.get_attribute('data-link')
        links.append(data_link)
    return links


def get_data(link):
    response = requests.get(link)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    target_div = soup.find('div', class_="rich_media_content")
    # 日期在目标div标签中的第二个strong标签
    date = target_div.find_all('strong')[1].text.split('广州市')[0]
    # 确诊或无症状数据都在目标div标签中的p标签中
    ps = target_div.find_all('p')
    for p in ps:
        if p.text.startswith('本土确诊病例') or p.text.startswith('本土无症状感染者'):
            # 以追加的形式写入到本地文件
            with open('data.csv', mode='a', encoding='utf-8', newline='') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerow([date, p.text])
    print(date,'的数据采集完毕！')
    time.sleep(1)


if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU2NTA0NTI0Ng==&action=getalbum&album_id=1806057435938258951&scene=173&from_msgid=2247628948&from_itemidx=1&count=3&nolastread=1#wechat_redirect'
    links = get_links(url)
    for link in links:
        get_data(link)


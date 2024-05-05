download_js_code = """
async function exportIndexDB(dbname){
  const loadScript = function(src){
    return new Promise(function(resolve){ 
      let script = document.createElement('script')
      script.src = src;
      script.onload = resolve;
      document.body.appendChild(script);
    })
  } 
  await loadScript('https://unpkg.com/dexie');
  await loadScript('https://unpkg.com/dexie-export-import');
  
  let db = new Dexie(dbname);
  const { verno, tables } = await db.open();
  db.close();
  
  db = new Dexie(dbname);
  db.version(verno).stores(tables.reduce((p,c) => {
    p[c.name] = c.schema.primKey.keyPath || "";
    return p;
  }, {}));
  return await db.export();
}

function download(downfile,name) {
  const tmpLink = document.createElement("a");
  const objectUrl = URL.createObjectURL(downfile);
  tmpLink.href = objectUrl;
  tmpLink.download = name;
  tmpLink.click();
  URL.revokeObjectURL(objectUrl);
}

let dbblob = await exportIndexDB('flomo');
download(dbblob,'flomo.json');
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seletools.actions import scroll_to_top, scroll_to_bottom
from seletools.indexeddb import IndexedDB
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.flomo_credentials.env')
# 从环境变量中获取用户名和密码
username = os.getenv('FLOMO_USERNAME')
password = os.getenv('FLOMO_PASSWORD')
print(username)
print(password)

# 设置无头模式，这样就不会打开一个真正的浏览器窗口
chrome_options = Options()
# chrome_options.add_argument("--headless")

# 创建 WebDriver 对象
driver = webdriver.Chrome(options=chrome_options)

# 打开网页
driver.get("https://v.flomoapp.com/")

# 登录
inputs = driver.find_elements(By.CLASS_NAME, "el-input__inner")
# print(inputs)
username_ele, password_ele = inputs[0], inputs[1]
username_ele.send_keys(username)
password_ele.send_keys(password)
driver.find_elements(By.CLASS_NAME, 'el-button--primary')[0].click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".memo.normal"))
)

# 找到主要元素
# 法1
# driver.find_element(By.XPATH, '//*[@id="app"]/div/section/main/div/div[3]')
# 法2
# memos = driver.find_element(By.CLASS_NAME, "memo normal")
memos = driver.find_elements(By.CSS_SELECTOR, ".memo.normal")
# print(memos)
# memo_eles = memos.find_element(By.XPATH, "./*")
for memo in memos:
    header = memo.find_element(By.CLASS_NAME, "header")
    main_content = memo.find_element(By.CLASS_NAME, "mainContent")
    # print(header.text)
    # print(main_content.text)
print(len(memos))

# idb = IndexedDB(driver, "flomo", 3)  # webdriver instance, db name, db version
# # GET value
# value = idb.get_value("memos", "751")  # table name, key in table
# print(value)

local_storage_data_str = driver.execute_script("return JSON.stringify(localStorage);")
local_storage_data = json.loads(local_storage_data_str)
print(local_storage_data)
# 简单粗暴地试用了别人的代码进行下载：https://zhuanlan.zhihu.com/p/584861893
driver.execute_script(download_js_code)

# 滚动到页面底部并模拟下拉加载
while True:
    # 滚动到页面底部
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try_memo = driver.find_element(By.XPATH, "/html/body/div[1]/div/section/main/div/div[3]")
    scroll_to_bottom(driver, try_memo)
    # print(try_memo)
    # js = 'document.getElementsByClassName("memos")[0].scrollTop=10000'
    # driver.execute(js)

    # 等待一个新元素加载（例如，一个特定的memo）
    # 这里需要根据实际情况调整选择器
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".memo.normal"))
        )
        # 找到所有class为"memo normal"的元素作为一个列表
        memos = driver.find_elements_by_css_selector(".memo.normal")
        print(f"Found {len(memos)} memos after scrolling.")
        
        # 假设您希望在找到一定数量的memo后停止加载
        if len(memos) >= 1000:
            break

        # 再次加载可能需要一些时间
        sleep(2)

    except Exception as e:
        print(f"An error occurred: {e}")
        break

driver.quit()

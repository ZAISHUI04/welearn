import requests
import re
import base64
from random import randint
from bs4 import BeautifulSoup
import time

# 新增
from selenium import webdriver


def printline():
    print('-'*51)


def to_hex_byte_array(byte_array):
    return ''.join([f'{byte:02x}' for byte in byte_array])


def generate_cipher_text(password):
    T0 = int(round(time.time() * 1000))
    P = password.encode('utf-8')
    V = (T0 >> 16) & 0xFF
    for byte in P:
        V ^= byte
    remainder = V % 100
    T1 = int((T0 / 100) * 100 + remainder)
    P1 = to_hex_byte_array(P)
    S = f"{T1}*" + P1
    S_encoded = S.encode('utf-8')
    E = base64.b64encode(S_encoded).decode('utf-8')
    return [E, T1]


# 新增：浏览器手动登录
def login():
    global session
    driver = webdriver.Edge()  # 你也可以用Chrome等
    driver.get(
        "https://sso.sflep.com/idsvr/login.html?returnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dwelearn_web%26redirect_uri%3Dhttps%253A%252F%252Fwelearn.sflep.com%252Fsignin-sflep%26response_type%3Dcode%26scope%3Dopenid%2520profile%2520email%2520phone%2520address%26code_challenge%3DNOEMTsm67sLFq6t3hnwMdUNOZs3CvQSdAp7wZEnYfek%26code_challenge_method%3DS256%26state%3DOpenIdConnect.AuthenticationProperties%253DX9AWxkQLsazgTK2GoGHM-_pkM-CgbUjpl9IFkIlRZcCgiDsf3l4WbeADX1blYdI45Q7s-HKahU_ncfHhiwZMvD18Y_tcZuYFUXsZvyZ8I1d3CArym3iX0_LuFNF0-ZC0h1Jon8l65p_FBaXJtesWvJhitUBNT_Q8nHOqR0jFZpHPbip76hJZdMA2W2lrX5izVthR9Gc3tsVk5jai5K42eP6x1ORUMgFIZFZRaA48Z8hEfXHmgpz7taYgOR37vhE-3hyiafxzttut98k46VJscwr3Jv_xPAKdTMrtWeQnklcClkISWbr-hvT-raoTE7Rd-jEU71scUs1HXY-HKhbyKw%26x-client-SKU%3DID_NET472%26x-client-ver%3D6.32.1.0"
    )
    print("请在Edge浏览器中手动输入账号和密码并完成所有验证，直到看到课程主页，再回到终端按回车继续...")
    input(">>> 登录完成后请按回车 <<<")
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
    headers = {
        'Referer': 'https://welearn.sflep.com/2019/student/index.aspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    resp = session.get('https://welearn.sflep.com/ajax/authCourse.aspx?action=gmc', headers=headers)
    print("课程接口返回内容：", resp.text)
    if '"clist"' not in resp.text:
        print("登录失败或未获取到课程信息，请检查登录状态！")
        driver.quit()
        exit(1)
    else:
        print("登录成功，已获取到课程信息。")
    driver.quit()


# 用全局 session
session = None
login()
printline()
while True:
    # 查询课程信息
    url = "https://welearn.sflep.com/ajax/authCourse.aspx?action=gmc"
    response = session.get(
        url, headers={"Referer": "https://welearn.sflep.com/2019/student/index.aspx"})
    if '\"clist\":[]}' in response.text:
        input('发生错误!!!可能是登录错误或没有课程!!!')
        exit(0)
    else:
        print('查询课程成功!!!')
        printline()
        print('我的课程: \n')
    back = response.json()["clist"]
    for i, course in enumerate(back, start=1):
        print(f'[NO.{i:>2}] 完成度{course["per"]:>3}% {course["name"]}')

    # 选择课程
    order = int(input("\n请输入需要完成的课程序号（上方[]内的数字）: "))
    cid = back[order - 1]["cid"]
    printline()
    print("获取单元中...")
    printline()
    # 刷课模块

    url = f"https://welearn.sflep.com/student/course_info.aspx?cid={cid}"
    response = session.get(url)
    script = BeautifulSoup(response.text, "html.parser").find_all("script")[13]
   # uid = re.search(r"uid=(\d+)", script.text).group(1)
    #classid = re.search(r"classid=(\d+)", script.text).group(1)

    uid = re.search('"uid":(.*?),', response.text).group(1)
    classid = re.search('"classid":"(.*?)"', response.text).group(1)

    url = 'https://welearn.sflep.com/ajax/StudyStat.aspx'
    response = session.get(url,params={'action':'courseunits','cid':cid,'uid':uid},headers={'Referer':'https://welearn.sflep.com/2019/student/course_info.aspx'})
    back = response.json()['info']

    # 选择单元 使用了WELearnToSleeep的代码
    print('[NO. 0]  按顺序完成全部单元课程')
    unitsnum = len(back)
    for i,x in enumerate(back,start=1):
        if x['visible']=='true':
            print(f'[NO.{i:>2d}]  [已开放]  {x["unitname"]}  {x["name"]}')
        else:
            print(f'[NO.{i:>2d}] ![未开放]! {x["unitname"]}  {x["name"]}')
    unitidx = int(input('\n\n请选择需要完成的单元序号（上方[]内的数字，输入0为按顺序刷全部单元）： '))
    printline()
    inputcrate = input('模式1:每个练习指定正确率，请直接输入指定的正确率\n如:希望每个练习正确率均为100，则输入 100\n\n模式2:每个练习随机正确率，请输入正确率上下限并用英文逗号隔开\n如:希望每个练习正确率为70～100，则输入 70,100\n\n请严格按照以上格式输入每个练习的正确率: ')
    if ',' in inputcrate:
        mycrate=eval(inputcrate)
        randommode=True
    else:
        mycrate=inputcrate
        randommode=False
    printline()
    # 伪造请求
    way1Succeed, way2Succeed, way1Failed, way2Failed = 0, 0, 0, 0

    ajaxUrl = "https://welearn.sflep.com/Ajax/SCO.aspx"
    infoHeaders = {
        "Referer": f"https://welearn.sflep.com/2019/student/course_info.aspx?cid={cid}",
    }

    if(unitidx == 0):
        i = 0
    else:
        i = unitidx - 1
        unitsnum = unitidx

    while True:
        response = session.get(
            f'https://welearn.sflep.com/ajax/StudyStat.aspx?action=scoLeaves&cid={cid}&uid={uid}&unitidx={i}&classid={classid}', headers=infoHeaders)

        if "异常" in response.text or "出错了" in response.text:
            break

        for course in response.json()["info"]:
            if course['isvisible']=='false':  # 跳过未开放课程
                print(f'[!!跳过!!]    {course["location"]}')
            elif "未" in course["iscomplete"]:  # 章节未完成
                print(f'[即将完成]    {course["location"]}')
                if randommode is True:
                    crate=str(randint(mycrate[0],mycrate[1]))
                else:
                    crate=mycrate
                data = '{"cmi":{"completion_status":"completed","interactions":[],"launch_data":"","progress_measure":"1","score":{"scaled":"'+crate+'","raw":"100"},"session_time":"0","success_status":"unknown","total_time":"0","mode":"normal"},"adl":{"data":[]},"cci":{"data":[],"service":{"dictionary":{"headword":"","short_cuts":""},"new_words":[],"notes":[],"writing_marking":[],"record":{"files":[]},"play":{"offline_media_id":"9999"}},"retry_count":"0","submit_time":""}}[INTERACTIONINFO]'

                id = course["id"]
                session.post(ajaxUrl, data={"action": "startsco160928",
                                            "cid": cid,
                                            "scoid": id,
                                            "uid": uid
                                            },
                             headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})
                response = session.post(ajaxUrl, data={"action": "setscoinfo",
                                                       "cid": cid,
                                                       "scoid": id,
                                                       "uid": uid,
                                                       "data": data,
                                                       "isend": "False" },
                                        headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})
                print(f'>>>>>>>>>>>>>>正确率:{crate:>3}%',end='  ')
                if '"ret":0' in response.text:
                    print("方式1:成功!!!", end="  ")
                    way1Succeed += 1
                else:
                    print("方式1:失败!!!", end="  ")
                    way1Failed += 1

                response = session.post(ajaxUrl, data={"action": "savescoinfo160928",
                                                       "cid": cid,
                                                       "scoid": id,
                                                       "uid": uid,
                                                       "progress": "100",
                                                       "crate": crate,
                                                       "status": "unknown",
                                                       "cstatus": "completed",
                                                       "trycount": "0",
                                                       },
                                        headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})
#                sleep(1) # 延迟1秒防止服务器压力过大
                if '"ret":0' in response.text:
                    print("方式2:成功!!!")
                    way2Succeed += 1
                else:
                    print("方式2:失败!!!")
                    way2Failed += 1
            else:  # 章节已完成
                print(f'[ 已完成 ]    {course["location"]}')

        if unitidx != 0:
            break
        else:
            i += 1
    if unitidx == 0:
        break
    else:
        print('本单元运行完毕！回到选课处！！\n\n\n\n')
        printline()

printline()
print(f"""
***************************************************
全部完成!!

总计:
方式1: {way1Succeed} 成功, {way1Failed} 失败
方式2: {way2Succeed} 成功, {way2Failed} 失败

https://github.com/Avenshy/WELearnToSleep

维护：https://github.com/YZBRH/Welearn_helper
    
本软件遵守GPLv3协议，且免费、开源，禁止售卖!
本软件遵守GPLv3协议，且免费、开源，禁止售卖!
本软件遵守GPLv3协议，且免费、开源，禁止售卖!
**********  Created By Avenshy & SSmJaE  **********""")
input("Press any key to exit...")
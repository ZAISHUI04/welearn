import asyncio
import json
import random
import re
import time
from textwrap import dedent
from typing import Any, Dict, List, Union
from bs4 import BeautifulSoup
import base64
from selenium import webdriver
import requests




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

# 登录（只用浏览器手动登录，不用终端输入账号密码）
def login():
    global session
    driver = webdriver.Edge()
    driver.get("https://sso.sflep.com/idsvr/login.html?returnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3Dwelearn_web%26redirect_uri%3Dhttps%253A%252F%252Fwelearn.sflep.com%252Fsignin-sflep%26response_type%3Dcode%26scope%3Dopenid%2520profile%2520email%2520phone%2520address%26code_challenge%3DNOEMTsm67sLFq6t3hnwMdUNOZs3CvQSdAp7wZEnYfek%26code_challenge_method%3DS256%26state%3DOpenIdConnect.AuthenticationProperties%253DX9AWxkQLsazgTK2GoGHM-_pkM-CgbUjpl9IFkIlRZcCgiDsf3l4WbeADX1blYdI45Q7s-HKahU_ncfHhiwZMvD18Y_tcZuYFUXsZvyZ8I1d3CArym3iX0_LuFNF0-ZC0h1Jon8l65p_FBaXJtesWvJhitUBNT_Q8nHOqR0jFZpHPbip76hJZdMA2W2lrX5izVthR9Gc3tsVk5jai5K42eP6x1ORUMgFIZFZRaA48Z8hEfXHmgpz7taYgOR37vhE-3hyiafxzttut98k46VJscwr3Jv_xPAKdTMrtWeQnklcClkISWbr-hvT-raoTE7Rd-jEU71scUs1HXY-HKhbyKw%26x-client-SKU%3DID_NET472%26x-client-ver%3D6.32.1.0")
    print("请在Edge浏览器中手动输入账号和密码并完成所有验证，直到看到课程主页，再回到终端按回车继续...")
    input(">>> 登录完成后请按回车 <<<")

    # 登录后获取cookie
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))

    # 检查登录是否成功
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

def get_target_course_info():
    global cid, uid, classid, courseInfo

    headers = {
        'Referer': 'https://welearn.sflep.com/2019/student/index.aspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    response = session.get(
        'https://welearn.sflep.com/ajax/authCourse.aspx?action=gmc',
        headers=headers
    )
    courseList = response.json()['clist']
    for index, course in enumerate(courseList, start=1):
        print('[id:{:>2d}]  完成度 {:>3d}%  {}'.format(index, course['per'], course['name']))

    index = int(input('\n请输入需要刷时长的课程id（id为上方[]内的序号）: '))
    cid = str(courseList[index - 1]['cid'])
    response = session.get(
        'https://welearn.sflep.com/2019/student/course_info.aspx?cid=' + cid,
        headers=headers
    )

    url = f"https://welearn.sflep.com/student/course_info.aspx?cid={cid}"
    response = session.get(url)
    scripts = BeautifulSoup(response.text, "html.parser").find_all("script")
    for idx, script in enumerate(scripts):
        if "uid=" in script.text and "classid=" in script.text:
            print(f"\n--- script[{idx}] ---\n{script.text}\n")
    uid, classid = None, None
    for script in scripts:
        if "uid=" in script.text and "classid=" in script.text:
            uid_match = re.search(r"uid=(\d+)", script.text)
            classid_match = re.search(r"classid=(\d+)", script.text)
            if uid_match and classid_match:
                uid = uid_match.group(1)
                classid = classid_match.group(1)
                break
    if not uid or not classid:
        print("未能在页面中找到uid或classid，请检查页面结构！")
        exit(1)

    req = session.get(
        'https://welearn.sflep.com/ajax/StudyStat.aspx',
        params={
            'action': 'courseunits',
            'cid': cid,
            'uid': uid
        },
        headers={
            'Referer': 'https://welearn.sflep.com/2019/student/course_info.aspx'
        }
    )
    courseInfo = req.json()['info']

def choose_unit():
    global unitIndex

    print("\n\n")
    print('[id: 0]  按顺序刷全部单元学习时长')
    for index, unit in enumerate(courseInfo, start=1):
        print(f"""[id:{index:>2d}]  {unit['unitname']}  {unit['name']}""")

    print("\n\n")
    unitIndex = int(input('请选择要刷时长的单元id（id为上方[]内的序号，输入0为刷全部单元）： '))

def input_time():
    global targetTime

    print("\n\n")
    print(dedent('''\
        模式1:每个练习增加指定学习时长，请直接输入时间
        如:希望每个练习增加30秒，则输入 30

        模式2:每个练习增加随机时长，请输入时间上下限并用英文逗号隔开
        如:希望每个练习增加10～30秒，则输入 10,30
    '''))
    print("\n\n")

    input_ = input("请严格按照以上格式输入: ")
    if(',' in input_):
        try:
            targetTime = [int(temp) for temp in input_.split(',')]
        except:
            print("格式异常")
            exit(0)
    else:
        targetTime = int(input_)

def generate_learning_time():
    global targetTime

    if type(targetTime) is int:
        learntime = targetTime
    else:
        learntime = random.randint(targetTime[0], targetTime[1])
    return learntime

def output_results():
    print('运行结束!!\n错误:', len(errors), '个')
    for index, error in enumerate(errors, start=1):
        print(f"第{index}个错误:{ error}")

    print("\n\n")
    print(dedent('''\
        **********  Created By Avenshy & SSmJaE  **********
                        Version : 0.3.0
           基于GPL3.0，完全开源，免费，禁止二次倒卖或商用
           https://www.github.com/Avenshy/WELearnToSleeep
                        仅供学习，勿滥用
        ***************************************************
    '''))
    print("\n\n")
    input("Press any key to exit...")

async def simulate(learningTime: int, chapter: Dict):
    print(f"""章节 : {chapter['location']}""")
    print(f"""已学 : {chapter['learntime']} 将学 : {learningTime}""")

    commonHeaders = {
        'Referer': 'https://welearn.sflep.com/student/StudyCourse.aspx'
    }

    scoid = chapter['id']
    commonData = {
        'uid': uid,
        'cid': cid,
        'scoid': scoid
    }

    await asyncio.sleep(REQUEST_INTERVAL)
    response = session.post(
        AJAX_URL,
        data={
            **commonData,
            'action': 'getscoinfo_v7',
        },
        headers=commonHeaders
    )

    if('学习数据不正确' in response.text):  # 重试
        await asyncio.sleep(REQUEST_INTERVAL)

        response = session.post(
            AJAX_URL,
            data={
                **commonData,
                'action': 'startsco160928',
            },
            headers=commonHeaders
        )
        response = session.post(
            AJAX_URL,
            data={
                **commonData,
                'action': 'getscoinfo_v7',
            },
            headers=commonHeaders
        )

        if('学习数据不正确' in response.text):
            print('\n错误:', chapter['location'])
            errors.append(chapter['location'])
            return

    returnJson = response.json()['comment']
    if('cmi' in returnJson):
        cmi = json.loads(returnJson)['cmi']

        crate = cmi['score']['scaled']
        cstatus = cmi['completion_status']
        progress = cmi['progress_measure']
        total_time = cmi['total_time']
        session_time = cmi['session_time']
    else:
        crate = ''
        cstatus = 'not_attempted'
        progress = '0'
        total_time = '0'
        session_time = '0'

    await asyncio.sleep(REQUEST_INTERVAL)
    session.post(
        AJAX_URL,
        data={
            **commonData,
            'action': 'keepsco_with_getticket_with_updatecmitime',
            'session_time': session_time,
            'total_time': total_time
        },
        headers=commonHeaders
    )

    for currentTime in range(1, learningTime + 1):
        await asyncio.sleep(1)

        if(currentTime % 60 == 0):
            session.post(
                AJAX_URL,
                data={
                    **commonData,
                    'action': 'keepsco_with_getticket_with_updatecmitime',
                    'session_time': session_time,
                    'total_time': total_time},
                headers=commonHeaders
            )

    await asyncio.sleep(REQUEST_INTERVAL)
    session.post(
        AJAX_URL,
        data={
            **commonData,
            'action': 'savescoinfo160928',
            'crate': crate,
            'cstatus': cstatus,
            'status': 'unknown',
            'progress': progress,
            'trycount': '0'
        },
        headers=commonHeaders
    )

async def heartbeat():
    startTime = time.time()
    for _ in range(maxLearningTime+4*REQUEST_INTERVAL):
        print(
            f"""\r预计学习时长 : {maxLearningTime+4*REQUEST_INTERVAL} 已学习时长 : {int(time.time()-startTime)}""", end="")
        await asyncio.sleep(HEARTBEAT_INTERVAL)

async def watcher():
    global maxLearningTime

    while True:
        get_target_course_info()
        choose_unit()
        input_time()

        if(unitIndex == 0):
            startIndex = 0
            endIndex = len(courseInfo)
        else:
            startIndex = unitIndex-1
            endIndex = unitIndex

        tasks = []
        for unit in range(startIndex, endIndex):
            response = session.get(
                f"https://welearn.sflep.com/ajax/StudyStat.aspx?action=scoLeaves&cid={cid}&uid={uid}&unitidx={str(unit)}&classid={classid}",
                headers={
                    'Referer': 'https://welearn.sflep.com/2019/student/course_info.aspx?cid=' + cid
                }
            )

            for chapter in response.json()['info']:
                learningTime = generate_learning_time()

                if learningTime > maxLearningTime:
                    maxLearningTime = learningTime

                tasks.append(asyncio.create_task(simulate(learningTime, chapter)))

        await heartbeat()
        [await task for task in tasks]

        if (unitIndex == 0):  # 如果已经刷完所有单元
            break
        else:  # 如果只刷了指定单元
            print("\n\n")
            print(f'本单元结束！错误 : {len(errors)}个')

            for index, error in enumerate(errors, start=1):
                print(f"第{index}个错误章节 : {error}")

            print('回到选课处！！')
            print("\n\n")
            maxLearningTime = 0

async def main():
    await asyncio.gather(
        watcher()
    )

if __name__ == "__main__":
    REQUEST_INTERVAL = 2
    HEARTBEAT_INTERVAL = 1
    AJAX_URL = "https://welearn.sflep.com/Ajax/SCO.aspx"

    cid: str
    uid: str
    classid: str
    courseInfo: List[Any]
    unitIndex: int
    targetTime: Union['int', List['int']]

    errors: List[str] = []
    maxLearningTime: int = 0
    session = requests.Session()

    login()
    asyncio.run(main())
    output_results()

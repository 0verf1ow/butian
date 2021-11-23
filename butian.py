# !/usr/bin/python3
# _*_ coding:utf-8 _*_
"""
date: 2021.11.13
检测补天专属厂商数量数量，有上架或者下架会有邮件通知
如果报错信息显示："错误信息：'utf-8' codec can't decode byte 0xbb in position 0: invalid start byte"，请放linux上跑
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import time
import re
import json


# 获取专属厂商列表数量
def get_num():
    try:
        url = "https://www.butian.net/Reward/corps"
        data = {'s': 3, 'p': 1, 'sort': 1, 'token': ''}
        r = requests.post(url, data=data)
        j = json.loads(r.text)
        num = len(j['data']['list'])  # 厂商数量
        name_list = []                # 厂商列表
        for row in j['data']['list']:
            d = {'company_name': row['company_name'], 'company_id': row['company_id']}
            name_list.append(d)
        return num, name_list
    except:
        time.sleep(30)
        return get_num()


# 发送邮件，暂只支持qq邮箱和163邮箱
def send_Email(send_mail, key, person, content):
    ret = True
    if re.findall(r'@\w+.com', send_mail)[0] == '@qq.com':  # 判断是否qq邮箱
        smtp_server = "smtp.qq.com"
    elif re.findall(r'@\w+.com', send_mail)[0] == '@163.com':  # 判断是否网易邮箱
        smtp_server = "smtp.163.com"
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr(["wooyun路人甲", send_mail])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        # msg['To'] = formataddr(["尊敬的白帽子", 'xxxxx@163.com'])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "补天专属列表监控"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL(smtp_server, 465)  # 发件人邮箱中的SMTP服务器，端口是465
        server.login(send_mail, key)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(send_mail, person, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
        s = "[!]错误信息：" + str(e)
        output_log(s)
    return ret


# 日志保存
def output_log(s):  # 写日志,打印信息
    print(s)
    with open('log.txt', 'a', encoding='utf-8') as log:
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log.write(t + "   " + s + "\n")


def main(n, old_name_list):
    num, new_name_list = get_num()  # 获取网页内的礼品数量
    if num > n:
        """
        对比变化前后的厂商，找出新增的厂商
        """
        try:
            for new in new_name_list:
                if not new in old_name_list:
                    company_name = new['company_name']
                    company_id = new['company_id']
                    break
        except:
            company_name = ''
            company_id = ''

        msg = "检测到厂商[ {} ]上架，请登录到平台查看 https://www.butian.net/Company/{}".format(company_name, company_id)
        ret = send_Email(send_mail, key, person, msg)  # 调用发送邮件
        if ret:
            s = "[+]检测到厂商[ {} ]上架，邮件发送成功".format(company_name)
            output_log(s)
        else:
            s = "[!]检测到厂商[ {} ]上架，但邮件发送失败".format(company_name)
            output_log(s)

    # 取消注释下面代码监控下架
    # elif num < n:
    #     msg = "检测到厂商有下架，请登录到平台查看https://www.butian.net/Reward/plan/2"
    #     ret = send_Email(send_mail, key, person, msg)  # 调用发送邮件
    #     if ret:
    #         s = "[+]检测到厂商下架，邮件发送成功"
    #         output_log(s)
    #     else:
    #         s = "[!]检测到厂商下架，但邮件发送失败"
    #         output_log(s)
    else:
        s = "[-]没改动"
        output_log(s)

    # 把获取到的礼品数返回,这样下次就是对比上次的数量，而不是对比初始值，防止变动后一直发邮件
    return num, new_name_list


def get_email_list():
    with open('email.txt', 'r', encoding="utf-8") as f:
        list = f.read().split('\n')
        return list


if __name__ == '__main__':
    # [配置区域]
    num, old_name_list = get_num()  # 当前专属数量,当前厂商列表
    send_mail = 'xxxxxxxxx@qq.com'  # 发件人邮箱账号
    key = 'xxxxxxxxx'               # 发件人邮箱smtp口令
    person = 'xxxxxxxx@qq.com'      # 收件人邮箱账号，多个收件人的话写成列表形式或者使用下面的代码
    # person = get_email_list()

    while True:  # 一直检测
        num, old_name_list = main(num, old_name_list)
        time.sleep(600)  # 设置多久检测一次有没有上架，默认10分钟

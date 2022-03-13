# !/usr/bin/python3
# coding: utf-8
"""
date: 2022.03.13
监控补天专属厂商上架，或者监控用户漏洞审核信息
如果报错信息显示："错误信息：'utf-8' codec can't decode byte 0xbb in position 0: invalid start byte"，请放linux上跑
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import time
import re
import json


class Butian():

    # 初始化读取配置
    def __init__(self):
        # 检查配置文件格式
        try:
            with open('config.ini', encoding="utf-8") as f:
                self.config = json.loads(f.read().strip())
        except:
            exit("[!] 配置文件格式错误")
        self.send_mail = self.config["send_mail"]  # 发送邮件通知的Email账号
        self.send_mail_stmp_key = self.config["send_mail_stmp_key"]  # 发送邮件通知的Smtp口令
        self.add_company_email = self.config["add_company_email"]  # 需要接收厂商上架通知的邮箱账号
        self.add_message_email = self.config["add_message_email"]  # 需要接受漏洞审核信息的邮箱账号
        self.h = {}
        self.h["cookie"] = self.config["cookie"]  # 补天平台的cookie
        self.delay = self.config["delay"]  # 监控延时
        self.run_add_company = self.config["run_add_company"]  # 是否监控厂商上架
        self.run_add_message = self.config["run_add_message"]  # 时候监控信息通知
        self.run()  # 开启运行

    # 程序的主方法
    def run(self):
        self.number, self.old_name_list = self.get_num()  # 获取初始的厂商数量
        self.old_id_list = self.get_id_list()  # 获取初始的消息id列表
        while True:
            if self.run_add_company == 1:  # 运行厂商监控
                self.number, self.old_name_list = self.add_company()

            if self.run_add_message == 1:  # 运行消息监控
                self.old_id_list, self.new_msg_dict = self.get_new_id(self.old_id_list)
                if self.new_msg_dict:  # 如果新增列表不为空
                    self.add_message()  # 调用发送邮件通知
                else:
                    s = "[-]审核无变动"
                    self.output_log(s)

            # 没有选择操作的话直接退出程序
            if self.run_add_company == 0 and self.run_add_message == 0: break  #

            time.sleep(self.delay)

    # 获取专属厂商列表数量
    def get_num(self):
        if self.run_add_company == 0: return 0, 0
        try:
            url = "https://www.butian.net/Reward/corps"  # 查询厂商列表的接口
            data = {'s': 3, 'p': 1, 'sort': 1, 'token': ''}
            r = requests.post(url, data=data)
            j = json.loads(r.text)
            num = len(j['data']['list'])  # 厂商数量
            name_list = []  # 厂商列表
            for row in j['data']['list']:
                d = {'company_name': row['company_name'], 'company_id': row['company_id']}
                name_list.append(d)
            return num, name_list
        except:
            time.sleep(30)
            return self.get_num()

    # 监控厂商上架
    def add_company(self):
        num, new_name_list = self.get_num()  # 获取网页内的礼品数量
        if num > self.number:
            """
            对比变化前后的厂商，找出新增的厂商
            """
            try:
                for new in new_name_list:
                    if not new in self.old_name_list:
                        company_name = new['company_name']
                        company_id = new['company_id']
                        break
            except:
                company_name = ''
                company_id = ''

            msg = "检测到厂商[ {} ]上架，请登录到平台查看 https://www.butian.net/Company/{}".format(company_name, company_id)
            ret = self.send_Email(self.send_mail, self.send_mail_stmp_key, self.add_company_email, msg)  # 调用发送邮件
            if ret:
                s = "[+]检测到厂商[ {} ]上架，邮件发送成功".format(company_name)
                self.output_log(s)
            else:
                s = "[!]检测到厂商[ {} ]上架，但邮件发送失败".format(company_name)
                self.output_log(s)

        else:
            s = "[-]厂商没改动"
            self.output_log(s)

        # 把获取到的礼品数返回,这样下次就是对比上次的数量，而不是对比初始值，防止变动后一直发邮件
        return num, new_name_list

    # 监控审核信息
    def add_message(self):
        msg = "有新的服务消息通知：可点击 https://www.butian.net/Message 查看\n"
        for id, title in self.new_msg_dict.items():
            msg += title + "\n"
        ret = self.send_Email(self.send_mail, self.send_mail_stmp_key, self.add_message_email, msg)  # 调用发送邮件
        if ret:
            s = "[+]检测到有新的漏洞审核通知，邮件发送成功"
            self.output_log(s)
        else:
            s = "[!]检测到有新的漏洞审核通知，但邮件发送失败"
            self.output_log(s)

    # 获取所有的通知信息
    def get_id_list(self):
        # 未读消息
        data = {"ajax": 1, "id": 0, "status": 0, "page": 1}
        # 获取通知的接口，返回对象类型是字符串
        try:
            r = requests.post("https://www.butian.net/Home/Message/lists", headers=self.h, data=data, )
            # 转为json对象好操作
            r_data = json.loads(r.text)

            # cookie失效检测
            if r_data["status"] == 0:
                msg = "[!]Cookie已过期，请从新获取cookie填入配置文件，再从新运行程序"
                ret = self.send_Email(self.send_mail, self.send_mail_stmp_key, self.add_company_email, msg)  # 调用发送邮件
                if ret:
                    s = "[+]检测到 cookie 失效，邮件发送成功"
                    self.output_log(s)
                    self.run_add_message = 0  # 发送不再监控漏洞审核通知的信号
                    return 0
                else:
                    s = "[!]检测到 cookie 失效，但邮件发送失败"
                    self.output_log(s)
                    self.run_add_message = 0  # 发送不再监控漏洞审核通知的信号
                    return 0

            last_lists = r_data['data']['list']  # 通知列表
            last_ids = {}  # 通知的id和title的字典
            try:
                for i in last_lists:
                    last_ids[i["id"]] = i["title"]
                return last_ids  # 返回的是最新的id和title字典
            except:
                return {'1': ''}  # 防止用户的消息列表为空
        except:
            # 网络错误的话，延时60秒再重新获取
            time.sleep(60)
            return self.get_id_list()

    # 获取新信息的id
    def get_new_id(self, old_id_list):
        new_id_lists = self.get_id_list()  # 获取最新的消息列表
        if self.run_add_message == 0: return 0, 0  # 截取
        new_msg_dict = {}
        for new_id in new_id_lists.keys():
            if new_id not in old_id_list.keys():  # id不在上一个返回值的列表中，那么他是新的
                new_msg_dict[new_id] = new_id_lists[new_id]
        new_id_lists['1'] = ''
        return new_id_lists, new_msg_dict  # 返回的是最新获取的消息列表，和已经新增的消息列表

    # 发送邮件，暂只支持qq邮箱和163邮箱作为发送箱
    def send_Email(self, send_mail, key, person, content):
        ret = True
        if re.findall(r'@\w+.com', send_mail)[0] == '@qq.com':  # 判断是否qq邮箱
            smtp_server = "smtp.qq.com"
        elif re.findall(r'@\w+.com', send_mail)[0] == '@163.com':  # 判断是否网易邮箱
            smtp_server = "smtp.163.com"
        try:
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = formataddr(["监控信息", send_mail])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['Subject'] = "补天监控"  # 邮件的主题，也可以说是标题
            server = smtplib.SMTP_SSL(smtp_server, 465)  # 发件人邮箱中的SMTP服务器，端口是465
            server.login(send_mail, key)  # 括号中对应的是发件人邮箱账号、邮箱密码
            server.sendmail(send_mail, person, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.quit()  # 关闭连接
        except Exception as e:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            ret = False
            s = "[!]错误信息：" + str(e)
            self.output_log(s)
        return ret

    # 日志保存
    def output_log(self, s):  # 写日志,打印信息
        print(s)
        with open('log.txt', 'a', encoding='utf-8') as log:
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            log.write(t + "   " + s + "\n")


if __name__ == '__main__':
    Butian()

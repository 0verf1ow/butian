# coding: utf-8
"""
此程序用于检测配置文件格式是否错误
"""
import json

with open('config.ini', encoding="utf-8") as f:
    j = json.loads(f.read().strip())
    print("[+] 配置文件格式无误")

### 文件说明

- butian.py                      监控程序，采用Python3编写

- email.txt                       需要接收监控信息的邮箱列表

- log.txt                           程序运行日志，包括监控信息和邮件发送日志

- requirements.txt        程序依赖包

  

### 拉取程序：

```
wget https://github.com/0verf1ow/butian/archive/refs/heads/main.zip
```

### 安装依赖：

```
pip intsall -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

### 运行程序(放到后台运行)：

```
nohup python3 butian.py>log 2>&1 &
```


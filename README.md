## 程序说明

该程序采用Python编写，可监控补天平台的专属列表变动和审核通知。

### 文件说明

- butian.py                      监控程序，采用Python3编写
- check_config                检测配置文件格式是否错误
- log.txt                            程序运行日志，包括监控信息和邮件发送日志
- requirements.txt         程序依赖包
- config.ini                       配置文件

### 拉取程序：

```
wget https://github.com/0verf1ow/butian/archive/refs/heads/main.zip
```

### 安装依赖：

```
pip intsall -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

### 编辑配置文件说明

qq邮箱获取smtp口令方法：https://www.cnblogs.com/hai-/p/13490814.html?ivk_sa=1024320u

浏览器获取cookie，只需要 "btuc" 开头的这一个

![image-20211126214955229](http://0verflow-img-submit.oss-cn-beijing.aliyuncs.com/img/image-20211126214955229.png)

```json
# 这里填的是要发送邮件的邮箱号
"send_mail": "xxxxxxxxxx@qq.com",

# 这里填的是要发送邮件的邮箱号的SMTP口令
"send_mail_stmp_key": "xxxxxxx", 

# 这里填的是接收专属厂商上架的邮箱号
"add_company_email": ["xxxxxx@qq.com","xxxxxxx@163.com","xxxxxxx@gmail.com"],

# 这里填的是接收审核通知的邮箱号
"add_message_email": "xxxxx@qq.com",

# 是否运行监控专属厂商上架监控，1 是运行，0 是不运行 
"run_add_company" : 1,

# 是否运行监控账号漏洞审核信息变动，1 是运行，0 是不运行 
"run_add_message" : 1,

# 补天平台的cookie,如果不监控漏洞审核的话不用填
"cookie" : "btuc_xxxxxxxxxxxxxxxxxxxx=xxxxxxxxxxxxxxxxxxxxxxxxxxxx;",

# 监控时间间隔，单位（秒）,时间不宜太小，否则会导致IP被Ban
"delay" : 600
```

### 运行程序：

运行监控程序前请先运行配置文件检查，如无报错再运行butian.py，有报错的话就是配置文件格式错误，请仔细检查配置文件

```
python3 check_config.py
```

linux(放到后台运行):

```linux
nohup python3 butian.py>log 2>&1 &
```

windows:

```
python3 butian.py
```

### 邮件说明

该通知为厂商上架通知：

<img src="http://0verflow-img-submit.oss-cn-beijing.aliyuncs.com/img/image-20211126215409919.png" alt="image-20211126215409919" style="zoom: 150%;" />

该通知为漏洞审核通知：

<img src="http://0verflow-img-submit.oss-cn-beijing.aliyuncs.com/img/image-20211126215449114.png" alt="image-20211126215449114" style="zoom:150%;" />

该通知为cookie过期告警（请及时更换有效cookie，否则无法监控漏洞审核变动）：

<img src="http://0verflow-img-submit.oss-cn-beijing.aliyuncs.com/img/image-20211126215532316.png" alt="image-20211126215532316" style="zoom:150%;" />


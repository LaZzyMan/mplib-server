# 后台接口

## 测试

/test
/schema

## 账户相关

### 登录

user/login

#### 参数

- code
- nickName
- avatarUrl
- gender
- city
- province
- country

#### 返回

- session
- libBind

### 更新微信session

user/update_session

#### 参数

- code
- session

#### 返回

- session
- status

### 验证登录状态

user/vertify_session

#### 参数

- session

#### 返回

- session
- login
- libBind

### 绑定图书馆账号

user/bind_lib

#### 参数

- session
- libId

#### 返回

- session
- status

### 图书馆账号解绑

user/unbind_lib

#### 参数

- session

#### 返回

- session
- status

### 图书馆账户登录

libuser/login

#### 参数

- session
- libId
- libPsw

#### 返回

- session
- status
- user

### 查询图书馆用户信息

libuser/bor_info

#### 参数

- session

#### 返回

- session
- result
- status

### 更新用户邮箱

libuser/update_email

#### 参数

- session
- email

#### 返回

- session
- status

### 更新用户电话

libuser/update_telephone

#### 参数

- session
- tel

#### 返回

- session
- status

## 馆藏查询

libuser/find

#### 参数

- session
- keyword
- code(wrd, wti, WAU, CAN, ISS, ISB)

#### 返回

- session
- status
- result

libuser/present

#### 参数

- session
- set_num
- entry(default 1)

#### 返回

- session
- status
- result

libuser/book_detail

#### 参数

- session
- doc_num

#### 返回

- session
- status
- result

libuser/bor_rank

#### 参数

- session
- lang: 01, 09, ALL
- category: ALL, A-Z
- time: y, s, w, m

#### 返回

- session
- status
- result


## 借阅相关

### 借阅信息

libuser/borrow_info

#### 参数

- session

#### 返回

- session
- status
- result

### 预约信息

libuser/hold_info

#### 参数

- session

#### 返回

- session
- status
- result

### 借阅历史

libuser/loan_history

#### 参数

- session

#### 返回

- session
- status
- result

### 续借

libuser/renew

#### 参数

- session
- bar_code

#### 返回

- session
- status
- reuslt

### 欠费记录

libuser/fine_info

#### 参数

- session

#### 返回

- session
- status
- result

### 续借

libuser/renew

#### 参数

- session
- bar_code

#### 返回

- session
- status

### 入馆记录

libuser/visit_info

#### 参数

- session

#### 返回

- session
- result
- status

### 预约图书

libuser/hold_req

#### 参数

- session
- bar_code
- pickup(WL, XX, GX, YX)

#### 返回

- session
- status

### 取消预约

libuser/hold_req_cancel

#### 参数

- session
- doc_number
- item_sequence
- sequence

#### 返回

- session
- status

## 通知公告

### 通知查询

/notice

#### 参数

- type: N(通知), Z(资源动态), P(培训活动)

#### 返回

- count
- next
- previous
- results

### 培训查询

/training

#### 参数

- type: B(毕业指导), X(学习助手), S(实用软件)
-session: 用于查询用户预约的活动

#### 返回

- count
- next
- previous
- results

### 活动查询

/activity

#### 返回

- count
- next
- previous
- results

### 投诉查询

/advise

#### 返回

- count
- next
- previous
- results

### 投诉上传（post）

/advise

#### 参数实例
```json
{
    "tel": "18642160183",
    "contents": "hhhhhh",
    "publishTime": "2019-07-01 21:34:00"
}
```

#### 返回

- id
- tel
- contents
- ...

## 消息推送

### 培训信息
training/add_training_reminder

发送前请在前端判断时间是否在7天之内，只接受7天内的推送请求
#### 参数
- session
- formId：用户提交时的表单id
- page：消息需要跳转的页面
- trainId：培训的id
- remindText：提醒的文本（备注）

#### 返回
- status
- session

### 取消培训预约
training/cancel_training_reminder
#### 参数
- session
- trainId：培训的id

#### 返回
- status
- session

### 书籍到期提醒
user/add_book_reminder

发送前请在前端判断时间是否在7天之内，只接受7天内的推送请求
#### 参数
- session
- formId：用户提交时的表单id
- page：消息需要跳转的页面
- bookName：书名
- borrowTime：借阅时间 %Y-%m-%d
- expiredTime：到期时间 %Y-%m-%d

#### 返回
- status
- session

## 新生游戏session检测
user/game_check_session
### 参数（get）
- session

### 返回
- status
- libBind：用户是否绑定图书馆账号
- info：若绑定则返回账户信息，否则为空
    - libId：用户的图书馆账号
    - openId：用户的openid

## 报错信息

```python
# 正常返回(返回中包含session)
status: 0
# session错误
status: 1
err_msg: LOGIN_FAILED
# 微信登录返回错误
status: 2
err_msg: 返回微信报错
# 服务器网络错误
status: 3
err_msg: SERVER_NETWORK_ERROR
# 参数缺少
status: 4
err_msg: PARAM_参数名_MISS
# RSA密钥错误
status: 5
err_msg: RSA_KEY_ERROR
# 图书馆接口返回错误
status: 6
err_msg: 图书馆错误接口
err_detail: 图书馆接口具体报错返回
```
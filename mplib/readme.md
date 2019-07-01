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

- count
- next
- previous
- results
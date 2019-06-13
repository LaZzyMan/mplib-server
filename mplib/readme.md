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

libuser/loan_info

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

### 预约图书

libuser/hold_req

#### 参数

- session
- bar_code
- pickup

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

### 登录界面

**功能：读者、管理员登录**

- 读者使用**读者号**、管理员通过**工号**进行登录，并选择用户类型
- 提示账号或密码未输入
- 提示账号或密码输入错误
- 对登录成功的账号进行对应的首页自动跳转
- 当账户不活跃时，登录状态额外保持30分钟


> ```
> 登录后的session:
> request.session['login_type']: 读者'dz'  管理员'gly'
> request.session['id']: 读者号  管理员工号 
> request.session['xm']: 读者姓名 管理员姓名
> ```

------


### 读者注册界面

**功能：对没有账户的读者提供注册新账户服务**

- 读者注册需要填写完整的姓名、密码，不得留空
- 密码需要输入两遍，并进行一致性确认
- 密码**长度**至少六位
- 用户名不能与现有用户重复
- 注册成功后重定向到登录界面
- 密码在数据库中只存SHA256密文，避免脱库造成用户账号信息泄露

------

### 书籍详情页面（读者和管理员该页面的不同仅在于侧边栏）

- 显示书名、ISBN、作者、出版社、出版时间、库存数量、评分、馆藏信息、本书相关评论

### 读者界面

- 显示读者姓名和读者号
- 侧边栏提供读者首页、当前借阅书籍、书籍查询与评论、借书、还书、评书记录、排行榜功能的链接跳转
- 提供退出登录选项
- 对未登录或登录权限错误的用户重定向至登录界面

### 读者首页界面

- 当前借阅数量
- 总借阅数量：0
- 排名/总人数
- 借阅历史（仅显示在库图书）：图书id/书名/借阅时间/应还时间/归还时间

### 读者书籍查询与评论界面

- 输入书名（必填，支持模糊搜索）、作者、ISBN、出版社（后三者均选填）
  - 注：也可以对代码稍作改动以搜索某个作者/ISBN/出版社的所有书
- 显示查询结果：ISBN（可以点击跳转书籍详情页面）、书名、作者、出版社、出版时间、库藏册数、不外借册数（在阅览室的）、未借出册数、已借出册数、评书按钮
- 点击评书按钮会弹出评书的表单，其中评分必填（范围为1-10），评语选填（字数限于100），写完后点提交按钮会显示成功或者报错信息（如之前已经评价过此书，需要删除原来的评论才能重新评价）

### 读者借书界面

- 录入正确的读者id和ISBN号进行借书（应由刷卡机导入数据）
  - 拦截读者id或ISBN号缺失
  - 拦截错误的读者id或ISBN号
- 检查读者借阅书籍数是否**达到上限**（10本）
- 检查该书是否**被该读者成功预约到**
  - 对于**成功预约到**图书的情况，将对应图书id的图书借阅给读者
    - 此后删除对应预约登记记录
  - 对于**未预约**或**未预约到**的情况，检查是否有未借出的图书
    - 若不存在未借出图书，不允许借阅已预约的图书
    - 若存在未借出图书，则挑选一本借阅给读者
- 对于成功借出的情况，通过邮件发送**借书凭证**，告知借阅的图书id

### 读者还书查询界面

- 录入正确的读者id和图书id进行还书
  - 拦截读者id或图书id缺失
  - 拦截错误的读者id或图书id
  - 拦截**读者未借阅该本图书**的情况
- 检查图书的应还时间：
  - 对于**期限内归还**的图书，无需缴纳费用
  - 对于**逾期未还**的图书，计算缴纳费用：超期天数*0.1元
- 检查该类图书是否存在预约但**未预约到**的记录：
  - 若存在未预约到记录，将图书按时间顺序分配给其中第一条记录
    - 更新预约表
    - 更新书目状态为**已预约**
    - 发送预约借书通知函
  - 若不存在未预约到记录，更新书目状态为**未借出**

### 评书记录

- 显示评书记录序号、ISBN、书名、评分、评语、评论时间、撤回评论按钮

### 排行榜

- 显示评分最高的十本书和被借阅次数最多的十本书

----

### 管理员首页界面

**功能：图书管理员首页，欢迎界面**

- 显示管理员姓名信息
- 提供书目状态查询、借书、还书、入库、出库功能的链接跳转
- 提供退出登录选项
- **对未登录或登录权限错误的用户重定向至登录界面**
- 后续所有读者页面都提供以上功能
- 额外提供图书馆状态刷新按钮
  - **清理过期的预约信息**并邮件预约过期通知函
  - **提醒即将借书逾期的用户**并邮件借书逾期通知函
  - 该功能每日执行一次即可
  - 该功能若上线，将被定时任务代替执行

### 管理员书目状态查询界面

- 输入书名（必填，支持模糊搜索）、作者、ISBN、出版社（后三者均选填）
- 显示查询结果：ISBN（可以点击跳转书籍详情页面）、书名、作者、出版社、出版时间、库藏册数、不外借册数（在阅览室的）、未借出册数、已借出册数


### 管理员入库界面

**功能：图书管理员将新的图书入库**

- 一次入库必须登记ISBN号、入库数量和入库后状态（流通室或阅览室）
  - 拦截ISBN号、入库数量和入库后状态缺失
  - 拦截**错误的入库数量**（非正、非整数）
- 检查图书ISBN号是否已经录入：
  - 若为**旧书录入**，选填书名等信息，若填写则检查信息是否正确
  - 若为**新书录入**，必填书名、作者、出版社和出版年月
- 系统自动为图书分配图书id，更新各表
- 对于分配到浏览室的每本图书，检查该类图书是否存在预约但**未预约到**的记录：
  - 若存在未预约到记录，将图书按时间顺序分配，更新各表，发送预约借书通知函
  - 若不存在未预约到记录，更新书目状态为**未借出**



### 管理员出库界面

**功能：图书管理员将书从馆内出库**

- 一次出库必须登记ISBN号、出库数量和优先从何处出库（流通室或阅览室）
  - 拦截ISBN号、出库数量和优先从何处出库的缺失
  - 拦截错误的ISBN号（ISBN号不存在）
  - 拦截**错误的出库数量**：
    - 非正、非整数
    - 超过馆藏总数
    - 超过馆藏总数 - 已借出图书数
- 根据优先从何处出库**选择出库策略**：
  - 优先从流通室出库：未借出 > 已预约 > 不外借
  - 优先从阅览室出库：不外借 > 未借出 > 已预约
- 对于被出库的已预约图书，邮件发送**预约失效通知函**
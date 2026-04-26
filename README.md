# 简易版 Offer Show 教学复刻

这是一个基于 Django + 微信公众号消息接口的练手项目。

- 用户发送文本命令给公众号
- 后端解析命令
- 把 Offer 数据存进 SQLite
- 按条件查询 Offer 并返回结果
- 这个项目的代码和说明都尽量写得更直白，方便第一次做项目的同学阅读。

## 1. 这个项目能做什么

- `help`：查看命令帮助
- `help <command>`：查看某个命令的详细说明
- `ping`：回复 pong（用于连通性测试）
- `stats`：查看我提交的 Offer 统计
- `my`：只看我提交的 Offer（支持分页）
- `latest`：查看全库最新 N 条 Offer
- `commit`：提交一条 Offer
- `query`：查询 Offer
- `group-commit`：一次提交多条 Offer
- `edit`：编辑一条 Offer（按字段更新 / 整体替换）
- `delete`：删除 Offer（单条 / 删除自己的全部）
- 自动记录用户
- 简单的高频请求检测
- 接收微信文本消息
- 接收微信图片消息并保存到 `main/pics/`

## 2. 项目结构

```text
myAssign1/
├── docs/                  # 新手说明文档
│   └── 新手复刻说明.md
├── main/                  # 主应用
│   ├── migrations/        # 数据库迁移文件
│   │   ├── 0001_initial.py
│   │   ├── 0002_*.py
│   │   └── __init__.py
│   ├── services/          # 业务逻辑
│   │   ├── __init__.py
│   │   ├── offer_services.py
│   │   └── user_services.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── constants.py       # 常量和提示文本
│   ├── lexer.py           # 命令解析器
│   ├── models.py          # 数据模型：User、Offer
│   ├── tests.py           # 基础测试
│   ├── urls.py
│   ├── views.py           # 微信请求入口
│   ├── wechat_utils.py    # XML 回复和微信工具函数
│   └── pics/              # 保存收到的图片（运行后自动生成）
├── wechat_robot/          # Django 项目配置
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .gitignore
├── README.md
├── manage.py              # Django 入口
└── requirements.txt       # 依赖
```

## 3. 环境要求

- Python 3.10 或更高版本
- `pip`

## 4. 快速运行

### 第一步：安装依赖

```bash
pip install -r requirements.txt
```

### 第二步：生成数据库表

```bash
python manage.py migrate
```

如果你修改了 `main/models.py` 里的模型，再执行：

```bash
python manage.py makemigrations
python manage.py migrate
```

### 第三步：启动开发服务器

```bash
python manage.py runserver
```

### 第四步：打开地址

在浏览器里访问：

```text
http://127.0.0.1:8000/wechat/
```

如果你直接访问这个地址，页面会显示：

```text
wechat server is running
```

这说明 Django 服务已经启动成功。

## 5. 命令示例

### `help`

```text
help
```

示例输出（公众号回复文本）：

```text
简易版 Offer Show 命令说明

1. help
   查看帮助信息（也可以：help <command>）

2. ping
   回复 pong（用于连通性测试）

3. stats
   查看我提交的 Offer 统计

4. my [--page 页码]
   只查看我提交的 Offer

5. latest [N]
   查看全库最新 N 条 Offer（默认 5，最大 20）

6. commit <公司> <城市> <岗位> <薪资>
   提交一条 Offer

7. query [--id ID] [--company 公司] [--city 城市] [--position 岗位] [--page 页码] [--sort-new] [--sort-salary]
   查询 Offer

8. group-commit <公司1> <城市1> <岗位1> <薪资1> [公司2] [城市2] [岗位2] [薪资2] ...
   一次提交多条 Offer

9. edit <id> [--company <公司>] [--city <城市>] [--position <岗位>] [--salary <薪资>]
   编辑一条 Offer（按字段更新，至少提供 1 个字段）

10. edit <id> <公司> <城市> <岗位> <薪资>
    编辑一条 Offer（整体替换）

11. delete <id>
    删除一条 Offer（只能删除自己提交的）

12. delete --all
    删除你提交的所有 Offer
```

### `help <command>`

```text
help query
```

示例输出（公众号回复文本）：

```text
query [--id ID] [--company 公司] [--city 城市] [--position 岗位] [--page 页码] [--sort-new] [--sort-salary]
查询 Offer；当使用 --id 时返回单条详情。
```

### `ping`

```text
ping
```

示例输出（公众号回复文本）：

```text
pong
```

### `latest`

```text
latest 5
```

示例输出（公众号回复文本）：

```text
最新 2 条 Offer
{
  Offer(Tencent, Shenzhen, Backend, 30000)
  Offer(ByteDance, Shenzhen, Backend, 28000)
}
```

### `stats`

```text
stats
```

示例输出（公众号回复文本）：

```text
我的统计：
count: 3
last_created_at: 2026-04-21 10:12:00
max_salary: 30000
min_salary: 20000
avg_salary: 25000
```

### `my`

```text
my --page 1
```

示例输出（公众号回复文本）：

```text
我的 Offer（第 1 / 1 页）
{
  Offer(Tencent, Shenzhen, Backend, 30000)
  Offer(ByteDance, Shenzhen, Backend, 28000)
}
```

### `commit`

```text
commit Tencent Shenzhen Backend 30000
```

示例输出（公众号回复文本）：

```text
收到啦，这条 Offer 已经保存。
ID: 1a2b3c4d
```

### `query`

```text
query
query --city Shenzhen
query --company Tencent --sort-salary
query --city Shenzhen --page 2
```

示例输出（公众号回复文本，示例为 `query --city Shenzhen --sort-salary`）：

```text
第 1 / 1 页
{
  Offer(Tencent, Shenzhen, Backend, 30000)
  Offer(ByteDance, Shenzhen, Backend, 28000)
}
```

### `group-commit`

```text
group-commit Tencent Shenzhen Backend 30000 Alibaba Beijing PM 25000
```

示例输出（公众号回复文本）：

```text
收到啦，这些 Offer 已经保存。
IDs:
1a2b3c4d
9e8f7a6b
```

### `edit`

```text
edit 1a2b3c4d --salary 32000
```

示例输出（公众号回复文本）：

```text
编辑成功：
ID: 1a2b3c4d
company: Tencent
city: Shenzhen
position: Backend
salary: 32000
created_at: 2026-04-21 10:12:00
from_user: some_user
```

### `delete`

```text
delete 1a2b3c4d
```

示例输出（公众号回复文本）：

```text
删除成功。
ID: 1a2b3c4d
```

## 6. 数据库里有什么表

### `User`

用来记录微信用户和用户状态：

- `username`：用户标识
- `state`：用户状态
- `request_queue`：最近请求时间列表

### `Offer`

用来保存 Offer：

- `public_id`：对外暴露的 8 位 ID（用于 query/edit/delete）
- `company`：公司
- `city`：城市
- `position`：岗位
- `salary`：薪资
- `created_at`：创建时间
- `from_user`：是谁提交的

## 7. 微信公众号配置说明

如果你只是在本地学习代码，这一步可以先跳过。

如果你真的要接公众号，需要在 `wechat_robot/settings.py` 里填写：

```python
WECHAT_TOKEN = "你的 token"
WECHAT_APP_ID = "你的 appid"
WECHAT_APP_SECRET = "你的 secret"
```

然后把公众号后台的服务器地址指向：

```text
https://你的域名/wechat/
```

注意：

- 微信要求公网地址
- 一般还需要 HTTPS
- 本地开发阶段不必先做完这一步

## 8. 推荐阅读顺序

如果你第一次看这个项目，建议按下面顺序阅读：

1. `README.md`
2. `docs/新手复刻说明.md`
3. `main/models.py`
4. `main/services/`
5. `main/lexer.py`
6. `main/views.py`

## 9. 运行测试

```bash
python manage.py test
```

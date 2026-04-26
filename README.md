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

7. query [--company 公司] [--city 城市] [--position 岗位] [--page 页码] [--sort-new] [--sort-salary]
   查询 Offer（分页列表）

8. detail <id>
   查看某条 Offer 详情

9. group-commit <公司1> <城市1> <岗位1> <薪资1> [公司2] [城市2] [岗位2] [薪资2] ...
   一次提交多条 Offer

10. edit <id> [--company <公司>] [--city <城市>] [--position <岗位>] [--salary <薪资>]
    编辑一条 Offer（按字段更新，至少提供 1 个字段）

11. edit <id> <公司> <城市> <岗位> <薪资>
    编辑一条 Offer（整体替换）

12. delete <id>
    删除一条 Offer（只能删除自己提交的）

13. delete --all
    删除你提交的所有 Offer
```

### `help <command>`

```text
help query
```

示例输出（公众号回复文本）：

```text
query [--company 公司] [--city 城市] [--position 岗位] [--page 页码] [--sort-new] [--sort-salary]
查询 Offer（分页列表）。
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
  Offer(1a2b3c4d, Tencent, Shenzhen, Backend, 30000)
  Offer(9e8f7a6b, ByteDance, Shenzhen, Backend, 28000)
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
  Offer(1a2b3c4d, Tencent, Shenzhen, Backend, 30000)
  Offer(9e8f7a6b, ByteDance, Shenzhen, Backend, 28000)
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
  Offer(1a2b3c4d, Tencent, Shenzhen, Backend, 30000)
  Offer(9e8f7a6b, ByteDance, Shenzhen, Backend, 28000)
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

## 10. 部署到服务器（详细教程）

下面以一台 Ubuntu 22.04 服务器为例，演示把本项目部署成可被微信回调访问的公网服务。

### 10.1 准备条件

- 一台公网服务器（能被外网访问）
- 一个域名（建议）：例如 `example.com`，并把域名 A 记录解析到服务器公网 IP
- 放通端口：80（HTTP）与 443（HTTPS）

微信的“服务器地址 URL”要求以 `http://` 或 `https://` 开头，且通常需要公网可访问的 80/443 端口。

### 10.2 在服务器上安装运行环境

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx
```

### 10.3 上传代码并安装依赖

把项目上传到服务器（例如放在 `/srv/myAssign1/`），然后：

```bash
cd /srv/myAssign1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 10.4 配置 Django（生产建议）

打开 `wechat_robot/settings.py`，至少做这些修改（示例）：

- `DEBUG = False`
- `SECRET_KEY` 改成你自己的随机字符串（不要公开）
- `ALLOWED_HOSTS` 加上你的域名（以及需要时的公网 IP）
- `WECHAT_TOKEN` 填一个你自定义的字符串（稍后要在公众号后台填同一个）

例如：

```python
DEBUG = False
ALLOWED_HOSTS = ["example.com"]
WECHAT_TOKEN = "your-wechat-token"
```

关于 `WECHAT_APP_ID/WECHAT_APP_SECRET`：

- 如果你没有真实的 appid/secret，建议保持空字符串（否则会尝试请求微信 `access_token` 并失败）。

### 10.5 初始化数据库

```bash
source /srv/myAssign1/.venv/bin/activate
cd /srv/myAssign1
python manage.py migrate
```

如需使用 Django 后台（可选）：

```bash
python manage.py createsuperuser
```

### 10.6 配置静态文件（推荐）

当 `DEBUG=False` 时，Django 不会自动帮你提供静态文件（包括 `/admin/` 的静态资源），推荐这样做：

1) 在 `wechat_robot/settings.py` 增加一行：

```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

2) 收集静态文件：

```bash
python manage.py collectstatic
```

### 10.7 用 Gunicorn 启动 Django（systemd 常驻）

创建 systemd 服务文件：

`/etc/systemd/system/myassign1.service`

内容如下（把路径按你的实际目录改掉）：

```ini
[Unit]
Description=myAssign1 Django (gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/myAssign1
Environment="PATH=/srv/myAssign1/.venv/bin"
ExecStart=/srv/myAssign1/.venv/bin/gunicorn wechat_robot.wsgi:application --workers 2 --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动并设置开机自启：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myassign1
sudo systemctl status myassign1
```

### 10.8 配置 Nginx 反向代理（绑定 80/443）

创建 Nginx 站点配置：

`/etc/nginx/sites-available/myassign1`

```nginx
   server {
      listen 80;
      server_name example.com;

      location /static/ {
         alias /srv/myAssign1/staticfiles/;
      }

      location / {
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_set_header X-Forwarded-Proto $scheme;
         proxy_pass http://127.0.0.1:8000;
      }
   }
```

启用并重载：

```bash
sudo ln -s /etc/nginx/sites-available/myassign1 /etc/nginx/sites-enabled/myassign1
sudo nginx -t
sudo systemctl reload nginx
```

此时访问：

- `http://example.com/wechat/` 应该能看到 `wechat server is running`

### 10.9 配置 HTTPS（Let’s Encrypt）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com
```

完成后，Nginx 会自动升级为 HTTPS，并配置自动续期。

### 10.10 在公众号后台配置“服务器地址”

在公众号后台把“服务器地址 URL”填写为：

```text
https://example.com/wechat/
```

并填写：

- Token：与你 `settings.WECHAT_TOKEN` 完全一致
- 消息加解密方式：选择明文模式（本项目目前按明文 XML 处理）

如果你看到 403（`invalid signature`），基本就是 Token 没对上或 URL 配错（例如少了 `/wechat/`）。

### 10.11 常见问题排查

- Nginx 502：Gunicorn 没起来或端口不对  
  - `sudo systemctl status myassign1`
  - `sudo journalctl -u myassign1 -n 200 --no-pager`
- 公众号校验失败：确认 URL、Token、是否公网可访问、是否走了 HTTPS 证书
- `/admin/` 样式丢失：通常是 `DEBUG=False` 但没配 `STATIC_ROOT + collectstatic + Nginx /static/`

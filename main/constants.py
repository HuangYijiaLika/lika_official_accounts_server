"""
本文件集中存放项目用到的常量与提示文本。
包括：返回码、用户状态位、高频请求限制参数、以及给用户的固定回复文案。
"""

RETURN_STATE_SUCCESS = 0
RETURN_STATE_NOT_FOUND_RECORD = 1
RETURN_STATE_ARGUMENT_NOT_COMPLETE = 2

USER_STATE_DEFAULT = 0b0000
USER_STATE_BANNED = 0b0001
USER_STATE_SPIDER = 0b0010

AUTHORITY_CHECK_PASS = 0
AUTHORITY_CHECK_FAILED = 1
AUTHORITY_CHECK_USER_NOT_EXIST = 2

REQUEST_QUEUE_LIMIT_TIME = 30
REQUEST_QUEUE_LIMIT_SIZE = 30

RECORDS_PER_PAGE = 10

MESSAGE_HELLO = "你好！"
MESSAGE_UNKNOWN_COMMAND = "这个命令我没有看懂。"
MESSAGE_COMMIT_SUCCESS = "收到啦，这条 Offer 已经保存。"
MESSAGE_VALUE_ERROR = "参数格式不对，请检查是不是把薪资写成了整数。"
MESSAGE_ONLY_TEXT_OR_IMAGE = "目前只支持文本消息和图片消息。"
MESSAGE_NO_PERMISSION = "你的账号目前不能继续使用查询功能。"
MESSAGE_NOT_OWNER = "只能操作自己提交的 Offer。"
MESSAGE_OFFER_NOT_FOUND = "没有找到对应的 Offer。"

HELP_BY_COMMAND = {
    "help": "help\n查看帮助信息，也可以用 help <command> 查看某个命令的详细说明。",
    "ping": "ping\n回复 pong，用于快速验证公众号链路与解析器是否正常。",
    "stats": "stats\n查看我提交的 Offer 统计：数量、最近一次提交时间、最高/最低/平均薪资。",
    "my": "my [--page 页码]\n只查看我提交的 Offer（支持分页）。",
    "latest": "latest [N]\n查看全库最新 N 条 Offer（默认 5，最大 20），按 created_at 倒序。",
    "commit": "commit <公司> <城市> <岗位> <薪资>\n提交一条 Offer，并返回该条 Offer 的 8 位 ID。",
    "query": "query [--id ID] [--company 公司] [--city 城市] [--position 岗位] [--page 页码] [--sort-new] [--sort-salary]\n查询 Offer；当使用 --id 时返回单条详情。",
    "group-commit": "group-commit <公司1> <城市1> <岗位1> <薪资1> [公司2] [城市2] [岗位2] [薪资2] ...\n一次提交多条 Offer，并返回每条的 8 位 ID。",
    "edit": "edit <id> [--company <公司>] [--city <城市>] [--position <岗位>] [--salary <薪资>]\n按字段更新；或 edit <id> <公司> <城市> <岗位> <薪资> 整体替换。",
    "delete": "delete <id>\n删除一条 Offer；或 delete --all 删除我提交的所有 Offer。",
}

MESSAGE_HELP = """简易版 Offer Show 命令说明

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
"""

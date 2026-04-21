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

MESSAGE_HELLO = "Ciallo~"
MESSAGE_UNKNOWN_COMMAND = "这个命令我没有看懂。"
MESSAGE_COMMIT_SUCCESS = "收到啦，这条 Offer 已经保存。"
MESSAGE_VALUE_ERROR = "参数格式不对，请检查是不是把薪资写成了整数。"
MESSAGE_ONLY_TEXT_OR_IMAGE = "目前只支持文本消息和图片消息。"
MESSAGE_NO_PERMISSION = "你的账号目前不能继续使用查询功能。"

MESSAGE_HELP = """简易版 Offer Show 命令说明

1. help
   查看帮助信息

2. commit <公司> <城市> <岗位> <薪资>
   提交一条 Offer

3. query [--company 公司] [--city 城市] [--position 岗位] [--page 页码] [--sort-new] [--sort-salary]
   查询 Offer

4. group-commit <公司1> <城市1> <岗位1> <薪资1> [公司2] [城市2] [岗位2] [薪资2] ...
   一次提交多条 Offer
"""

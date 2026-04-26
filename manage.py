"""
本文件是 Django 项目的命令行入口。
常用：python manage.py runserver / migrate / test / createsuperuser 等。
"""

import os
import sys


def main() -> None:
    """Django 管理命令入口：负责把命令行参数交给 Django 执行。"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wechat_robot.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. Run 'pip install -r requirements.txt' first."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

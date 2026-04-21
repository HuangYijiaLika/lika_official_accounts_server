"""
本文件是项目的自动化测试。
通过 Django TestCase 验证：命令解析、Offer 的批量写入与分页/排序、以及用户高频请求限制等核心逻辑。
"""

from django.test import TestCase

from main.constants import AUTHORITY_CHECK_FAILED, AUTHORITY_CHECK_PASS
from main.lexer import parse_command
from main.models import Offer
from main.services.offer_services import batch_create_offers, list_offers_with_page
from main.services.user_services import check_user_state, create_user, get_user


class LexerTests(TestCase):
    def test_commit_command_can_be_parsed(self) -> None:
        result = parse_command("commit Tencent Shenzhen Backend 30000")
        self.assertEqual(
            result,
            {
                "command": "commit",
                "company": "Tencent",
                "city": "Shenzhen",
                "position": "Backend",
                "salary": 30000,
            },
        )

    def test_query_command_can_be_parsed(self) -> None:
        result = parse_command("query --city Shenzhen --sort-salary --page 2")
        self.assertEqual(result["command"], "query")
        self.assertEqual(result["city"], "Shenzhen")
        self.assertEqual(result["page"], 2)
        self.assertTrue(result["sort-salary"])

    def test_group_commit_requires_four_values_per_offer(self) -> None:
        result = parse_command("group-commit Tencent Shenzhen Backend")
        self.assertIsNone(result)


class OfferServiceTests(TestCase):
    def setUp(self) -> None:
        create_user("alice")

    def test_batch_create_and_pagination_work(self) -> None:
        batch_create_offers(
            [
                {"company": f"C{i}", "city": "Beijing", "position": "Dev", "salary": 10000 + i}
                for i in range(12)
            ],
            "alice",
        )

        first_page, current_page, page_count = list_offers_with_page({"page": 1})
        second_page, _, _ = list_offers_with_page({"page": 2})

        self.assertEqual(current_page, 1)
        self.assertEqual(page_count, 2)
        self.assertEqual(len(first_page), 10)
        self.assertEqual(len(second_page), 2)

    def test_sort_by_salary_works(self) -> None:
        batch_create_offers(
            [
                {"company": "A", "city": "Beijing", "position": "Dev", "salary": 15000},
                {"company": "B", "city": "Beijing", "position": "Dev", "salary": 30000},
            ],
            "alice",
        )

        results, _, _ = list_offers_with_page({"sort-salary": True})
        salaries = [offer.salary for offer in results]
        self.assertEqual(salaries[:2], [30000, 15000])


class UserServiceTests(TestCase):
    def test_user_is_marked_as_spider_after_too_many_requests(self) -> None:
        username = "high-frequency-user"

        for _ in range(29):
            self.assertEqual(check_user_state(username, "query", update=True), AUTHORITY_CHECK_PASS)

        self.assertEqual(check_user_state(username, "query", update=True), AUTHORITY_CHECK_FAILED)
        self.assertIsNotNone(get_user(username))

    def test_first_request_can_create_user(self) -> None:
        username = "new-user"
        result = check_user_state(username, "help", update=True)
        self.assertEqual(result, AUTHORITY_CHECK_PASS)
        self.assertIsNotNone(get_user(username))

    def test_offers_are_stored_in_database(self) -> None:
        create_user("bob")
        batch_create_offers(
            [{"company": "Tencent", "city": "Shenzhen", "position": "SDE", "salary": 25000}],
            "bob",
        )
        self.assertEqual(Offer.objects.count(), 1)

"""
本文件是项目的自动化测试。
通过 Django TestCase 验证：命令解析、Offer 的批量写入与分页/排序、以及用户高频请求限制等核心逻辑。
"""

from unittest import mock

from django.test import TestCase

from main.constants import AUTHORITY_CHECK_FAILED, AUTHORITY_CHECK_PASS
from main.lexer import parse_command
from main.models import Offer
from main.services.offer_services import (
    batch_create_offers,
    create_offer,
    delete_all_offers_by_username,
    delete_offer_by_public_id,
    get_offer_by_public_id,
    list_offers_with_page,
    replace_offer_by_public_id,
    update_offer_by_public_id,
)
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

    def test_query_can_parse_id(self) -> None:
        result = parse_command("query --id 1A2b3C4d")
        self.assertEqual(result["command"], "query")
        self.assertEqual(result["id"], "1A2b3C4d")

    def test_group_commit_requires_four_values_per_offer(self) -> None:
        result = parse_command("group-commit Tencent Shenzhen Backend")
        self.assertIsNone(result)

    def test_edit_update_can_be_parsed(self) -> None:
        result = parse_command("edit 1a2b3c4d --city Shenzhen --salary 20000")
        self.assertEqual(result["command"], "edit_update")
        self.assertEqual(result["id"], "1a2b3c4d")
        self.assertEqual(result["updates"]["city"], "Shenzhen")
        self.assertEqual(result["updates"]["salary"], 20000)

    def test_edit_replace_can_be_parsed(self) -> None:
        result = parse_command("edit 1a2b3c4d Tencent Shenzhen Backend 30000")
        self.assertEqual(result["command"], "edit_replace")
        self.assertEqual(result["id"], "1a2b3c4d")
        self.assertEqual(result["salary"], 30000)

    def test_delete_commands_can_be_parsed(self) -> None:
        self.assertEqual(parse_command("delete --all"), {"command": "delete_all"})
        self.assertEqual(parse_command("delete 1a2b3c4d"), {"command": "delete_one", "id": "1a2b3c4d"})

    def test_edit_update_rejects_unknown_field(self) -> None:
        self.assertIsNone(parse_command("edit 1a2b3c4d --unknown X"))

    def test_edit_update_rejects_odd_pairs(self) -> None:
        self.assertIsNone(parse_command("edit 1a2b3c4d --city"))

    def test_edit_update_rejects_non_int_salary(self) -> None:
        self.assertIsNone(parse_command("edit 1a2b3c4d --salary abc"))


class OfferServiceTests(TestCase):
    def setUp(self) -> None:
        create_user("alice")
        create_user("bob")

    def test_batch_create_and_pagination_work(self) -> None:
        public_ids = batch_create_offers(
            [
                {"company": f"C{i}", "city": "Beijing", "position": "Dev", "salary": 10000 + i}
                for i in range(12)
            ],
            "alice",
        )
        self.assertEqual(len(public_ids), 12)
        self.assertTrue(all(isinstance(item, str) and len(item) == 8 for item in public_ids))

        first_page, current_page, page_count = list_offers_with_page({"page": 1})
        second_page, _, _ = list_offers_with_page({"page": 2})

        self.assertEqual(current_page, 1)
        self.assertEqual(page_count, 2)
        self.assertEqual(len(first_page), 10)
        self.assertEqual(len(second_page), 2)
        self.assertTrue(all(offer.public_id for offer in first_page))

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

    def test_get_offer_by_public_id_works_case_insensitive(self) -> None:
        public_id = create_offer(
            {"company": "Tencent", "city": "Shenzhen", "position": "SDE", "salary": 25000},
            "alice",
        )
        offer = get_offer_by_public_id(public_id.upper())
        self.assertIsNotNone(offer)
        self.assertEqual(offer.public_id, public_id)

    def test_public_id_collision_is_resolved_by_suffix(self) -> None:
        def fake_compute(base: str) -> str:
            return "deadbeef" if "#1" not in base else "cafebabe"

        with mock.patch("main.services.offer_services._compute_public_id", side_effect=fake_compute):
            first = create_offer(
                {"company": "A", "city": "B", "position": "C", "salary": 1},
                "alice",
            )
            second = create_offer(
                {"company": "A", "city": "B", "position": "C", "salary": 1},
                "alice",
            )

        self.assertEqual(first, "deadbeef")
        self.assertEqual(second, "cafebabe")

    def test_update_offer_requires_owner(self) -> None:
        public_id = create_offer(
            {"company": "Tencent", "city": "Shenzhen", "position": "SDE", "salary": 25000},
            "alice",
        )
        result = update_offer_by_public_id(public_id, "bob", {"salary": 1})
        self.assertFalse(result)

    def test_update_offer_keeps_public_id(self) -> None:
        public_id = create_offer(
            {"company": "Tencent", "city": "Shenzhen", "position": "SDE", "salary": 25000},
            "alice",
        )
        result = update_offer_by_public_id(public_id, "alice", {"salary": 26000})
        self.assertIsNotNone(result)
        self.assertNotEqual(result, False)
        offer = get_offer_by_public_id(public_id)
        self.assertIsNotNone(offer)
        self.assertEqual(offer.public_id, public_id)
        self.assertEqual(offer.salary, 26000)

    def test_replace_offer_keeps_public_id(self) -> None:
        public_id = create_offer(
            {"company": "Tencent", "city": "Shenzhen", "position": "SDE", "salary": 25000},
            "alice",
        )
        result = replace_offer_by_public_id(public_id, "alice", "A", "B", "C", 1)
        self.assertIsNotNone(result)
        self.assertNotEqual(result, False)
        offer = get_offer_by_public_id(public_id)
        self.assertIsNotNone(offer)
        self.assertEqual(offer.public_id, public_id)
        self.assertEqual(offer.company, "A")
        self.assertEqual(offer.salary, 1)

    def test_delete_offer_requires_owner(self) -> None:
        public_id = create_offer(
            {"company": "Tencent", "city": "Shenzhen", "position": "SDE", "salary": 25000},
            "alice",
        )
        result = delete_offer_by_public_id(public_id, "bob")
        self.assertFalse(result)
        self.assertIsNotNone(get_offer_by_public_id(public_id))

    def test_delete_offer_works(self) -> None:
        public_id = create_offer(
            {"company": "Tencent", "city": "Shenzhen", "position": "SDE", "salary": 25000},
            "alice",
        )
        self.assertTrue(delete_offer_by_public_id(public_id, "alice"))
        self.assertIsNone(get_offer_by_public_id(public_id))

    def test_delete_all_offers_by_username(self) -> None:
        create_offer({"company": "A", "city": "B", "position": "C", "salary": 1}, "alice")
        create_offer({"company": "D", "city": "E", "position": "F", "salary": 2}, "alice")
        create_offer({"company": "X", "city": "Y", "position": "Z", "salary": 3}, "bob")
        count = delete_all_offers_by_username("alice")
        self.assertEqual(count, 2)
        self.assertEqual(Offer.objects.filter(from_user__username="alice").count(), 0)
        self.assertEqual(Offer.objects.filter(from_user__username="bob").count(), 1)


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

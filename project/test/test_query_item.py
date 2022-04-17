import re
import unittest
import datetime
from typing import Dict, List

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import rdb_create_all, remove_test_db, User, Item, ItemContents
from project.query.err_codes import ItemQueryErrorCode
from project.query.item_query import ItemQuery
from project.query.user_query import UserQuery
from project.test.csv_reader_for_test import csv_reader_for_test


class TestQueryUser(unittest.TestCase):
    """ 사용자 CRUD 테스트
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 처음 클래스를 시작 할 때 작동
        # DB 생성
        DatabaseConnectionGenerator.get().connect()
        rdb_create_all()

    @classmethod
    def tearDownClass(cls) -> None:
        # 테스트 클래스 자체 종료
        # DB 자체 제거
        DatabaseConnectionGenerator.get().disconnect()
        remove_test_db()

    def tearDown(self) -> None:
        # 테스트 함수가 끝날 때마다 호출
        # 모든 데이터 전부 삭제
        db_session = DatabaseConnectionGenerator.get_session()
        db_session.query(ItemContents).delete()
        db_session.query(Item).delete()
        db_session.query(User).delete()

    def test_create(self):
        """ 상품(만) 생성 (펀딩관련 생성 X)

            * 상품 이름이 128자를 넘어가면 안된다.
            * 펀딩 종료일은 과거여도 상관없음
            * 동일한 이름의 상품을 생성할 수 없다.
            * 없는 유저에 상품을 등록할 수 없다.
            * 상품 요약은 2048자를 넘어가면 안된다.
            * 목표 금액과 1회펀딩당 금액은 1이상이어야 한다.
        """

        # 테스트를 위한 default data
        def_username: str = "유저01"
        def_name: str = "상품01"
        def_summary: str = "summary"
        def_end_date: str = datetime.datetime.now()
        def_funding_unit: int = 1000
        def_target_money: int = 1000000

        # 선 유저 생성
        UserQuery.create(def_username)
        def_user_id: str = UserQuery.read("name", def_username)['id']

        # 1.상품 이름이 128자를 초과하면 안된다.
        self.assertEqual(ItemQuery.create(
            ["id", def_user_id], "z" * 129, def_summary,
            def_end_date, def_funding_unit, def_target_money
        ), ItemQueryErrorCode.NAME_NOT_MATCHED)

        # 2. 상품 이름이 비어있으면 안된다.
        self.assertEqual(ItemQuery.create(
            ["id", def_user_id], "", def_summary,
            def_end_date, def_funding_unit, def_target_money
        ), ItemQueryErrorCode.NAME_NOT_MATCHED)

        # 3. 없는 유저에 상품을 등록할 수 없다
        self.assertEqual(ItemQuery.create(
            ["name", "없는 유저"], def_name, def_summary,
            def_end_date, def_funding_unit, def_target_money
        ), ItemQueryErrorCode.USER_NOT_EXISTS)

        # 4. 상품 요약은 2048자를 넘어가면 안된다.
        self.assertEqual(ItemQuery.create(
            ["id", def_user_id], def_name, "*" * 2049,
            def_end_date, def_funding_unit, def_target_money
        ), ItemQueryErrorCode.SUMMARY_MATCHED_FAILED)

        # 5. 목표 금액은 0원이면 안된다.
        self.assertEqual(ItemQuery.create(
            ["id", def_user_id], def_name, def_summary,
            def_end_date, def_funding_unit, 0
        ), ItemQueryErrorCode.TARGET_MONEY_NOT_MATCHED)

        # 6. 1회 펀딩 금액이 1원 이하이면 안된다.
        self.assertEqual(ItemQuery.create(
            ["id", def_user_id], def_name, def_summary,
            def_end_date, 0, def_target_money
        ), ItemQueryErrorCode.FUNDING_UNIT_NOT_MATCHED)

        # 7. 정상적인 추가, 요약은 비어있어도 된다.
        self.assertEqual(ItemQuery.create(
            ["id", def_user_id], def_name, "",
            def_end_date, def_funding_unit, def_target_money
        ), ItemQueryErrorCode.SUCCEED)

        # 8. 같은 상품을 등록할 수 없다.
        self.assertEqual(ItemQuery.create(
            ["id", def_user_id], def_name, "",
            def_end_date, def_funding_unit, def_target_money
        ), ItemQueryErrorCode.ITEM_ALREADY_EXISTS)

    def test_update(self):
        # 테스팅을 위한 유저 생성
        user_name: str = "유저01"
        UserQuery.create(user_name)
        user_id: str = UserQuery.read("name", user_name)['id']

        # 아이템 추가
        item_name: str = "상품1"
        ItemQuery.create(
            ["id", user_id], item_name,
            "아이템입니다.", datetime.datetime.now() + datetime.timedelta(days=3),
            1000, 10000
        )

        # test_create와 비슷한 포맷으로 테스팅
        # 1. 이름이 128자 넘아가면 안된다
        self.assertEqual(ItemQuery.update(
            ["name", item_name], name="*" * 129), ItemQueryErrorCode.NAME_NOT_MATCHED)

        # 2. 상품 요약은 2048자를 넘어가선 안된다.
        self.assertEqual(ItemQuery.update(
            ["name", item_name], summary="*" * 3000), ItemQueryErrorCode.SUMMARY_MATCHED_FAILED)

        # 3. 1회펀딩금액이 0원 이하이면 안된다.
        self.assertEqual(ItemQuery.update(
            ["name", item_name], funding_unit=0), ItemQueryErrorCode.FUNDING_UNIT_NOT_MATCHED)

        # 4. 참여자 수가 0명 이하이면 안된다.
        self.assertEqual(ItemQuery.update(
            ["name", item_name], participant_size=-1), ItemQueryErrorCode.PARTICIPANT_SIZE_NOT_MATCHED)

        # 5. 현재 펀딩된 금액이 음수이면 안된다
        self.assertEqual(ItemQuery.update(
            ["name", item_name], current_money=-1), ItemQueryErrorCode.CURRENT_MONEY_NOT_MATCHED)

        # 정상적인 업데이트, summary가 비어있는 문자열인 경우 None으로 취급 안하고 비어있는 상태로 수정되어야 한다.
        self.assertEqual(ItemQuery.update(
            ["name", item_name], name="변경된 상품", summary="",
            end_date=datetime.datetime.now() + datetime.timedelta(days=10),
            funding_unit=2000
        ), ItemQueryErrorCode.SUCCEED)

        # + 같은 이름의 상품명으로 업데이트 해서는 안된다.
        ItemQuery.create(
            ["id", user_id], item_name,
            "아이템입니다.", datetime.datetime.now() + datetime.timedelta(days=3),
            1000, 10000
        )
        self.assertEqual(ItemQuery.update(
            ["name", item_name], name="변경된 상품"), ItemQueryErrorCode.ITEM_ALREADY_EXISTS)

    def test_read(self):
        """ 아이디 및 상품 이름을 통한 상세 정보 갖고오는 쿼리 """

        # 테스팅을 위한 임의의 유저 생성
        user_name: str = "유저01"
        UserQuery.create(user_name)
        user_id: str = UserQuery.read("name", user_name)['id']

        answer: Dict[str, object] = {
            # 예상 정답
            "name": "상품1",
            "summary": "상품 설명",
            "user_name": user_name,
            "end_date": datetime.datetime.now() + datetime.timedelta(days=3),
            "funding_unit": 1000,  # 1회 펀딩 당 금액
            "target_money": 10000,  # 목표 달성 금액
            "current_money": 6000,  # 현재 달성 금액
            "participant_size": 6,  # 참가자 수
            "funding_gage": 60.0,  # 달성률
        }

        # 아이템 추가
        ItemQuery.create(
            ["id", user_id], answer['name'],
            answer['summary'], answer['end_date'],
            answer['funding_unit'], answer['target_money']
        )
        ItemQuery.update(["name", answer['name']],
                         participant_size=answer['participant_size'],
                         current_money=answer['current_money'],
                         )

        # 검토
        res: Dict[str, object] = ItemQuery.read("name", answer['name'])
        for k, v in answer.items():
            # 데이터가 맞는 지 확인
            self.assertEqual(answer[k], res[k])

        # 존재하지 않는 항목 검색 시 None 리턴
        self.assertIsNone(ItemQuery.read("name", "없음"))

    def test_read_item_list(self):
        """ 아이템 리스트 테스팅 """

        # 테스팅을 위한 임의의 유저 생성
        user_name: str = "유저01"
        UserQuery.create(user_name)
        user_id: str = UserQuery.read("name", user_name)['id']

        # csv 파일을 불러와서 상품들을 생성
        csv_reader = csv_reader_for_test("test/inputs/test_query_item_read_list.csv")
        for data in csv_reader:
            if data['name'] == 'name':
                continue
            ItemQuery.create(
                ["id", user_id],
                data['name'], data['summary'], data['end_date'],
                data['funding_unit'], data['target_money']
            )

        # ..하고 싶다 검색
        regex_str: str = "하고 싶다"
        regex = re.compile(rf"^.*({regex_str}).*")
        res_data: List[Dict[str, object]] = ItemQuery.read_item_list_by_name_regex(regex_str)
        res, ans = [d['name'] for d in res_data], [d['name'] for d in csv_reader if regex.match(d['name'])]
        self.assertListEqual(sorted(res), sorted(ans))

    def test_sort_fundingmoney(self):
        """ 총 펀딩 금액 순으로 나열 """

        # 테스팅을 위한 임의의 유저 생성

        user_name: str = "유저01"
        UserQuery.create(user_name)
        user_id: str = UserQuery.read("name", user_name)['id']

        # csv 파일을 불러와서 상품들을 생성
        csv_reader = csv_reader_for_test("test/inputs/test_query_item_read_list.csv")
        for data in csv_reader:
            if data['name'] == 'name':
                # 맨 상단 표 제목
                continue
            ItemQuery.create(
                ["id", user_id],
                data['name'], data['summary'], data['end_date'],
                data['funding_unit'], data['target_money']
            )
            ItemQuery.update(["name", data['name']], current_money=data['current_money'])

        # 검토
        res_data: List[Dict[str, object]] = ItemQuery.sort_by_fundingmoney()
        res = [d['name'] for d in res_data]
        csv_reader.sort(key=lambda d: -d['current_money'])
        ans = [d['name'] for d in csv_reader]
        self.assertEqual(ans, res)

    def test_delete(self):

        user_name: str = "유저01"
        UserQuery.create(user_name)
        user_id: str = UserQuery.read("name", user_name)['id']

        # csv 파일을 불러와서 상품들을 생성
        csv_reader = csv_reader_for_test("test/inputs/test_query_item_read_list.csv")
        for data in csv_reader:
            if data['name'] == 'name':
                # 맨 상단 표 제목
                continue
            ItemQuery.create(
                ["id", user_id],
                data['name'], data['summary'], data['end_date'],
                data['funding_unit'], data['target_money']
            )
            ItemQuery.update(["name", data['name']], current_money=data['current_money'])

        # 하나 삭제
        delete_item_name = csv_reader[0]['name']
        delete_item_id = ItemQuery.read("name", delete_item_name)['item_id']
        self.assertEqual(ItemQuery.delete("name", delete_item_name), ItemQueryErrorCode.SUCCEED)
        self.assertIsNone(ItemQuery.read("name", delete_item_name))

        # 컨텐츠(설명)도 같이 삭제되어야 한다.
        db = DatabaseConnectionGenerator.get_session()
        self.assertIsNone(db.query(ItemContents).filter(ItemContents.item_id == delete_item_id).scalar())

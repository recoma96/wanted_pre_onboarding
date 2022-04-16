import unittest
import datetime
from typing import List, Dict

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import rdb_create_all, remove_test_db, User, Item
from project.query.item_query import ItemQuery
from project.query.user_query import UserQuery


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
        # 유저만 삭제하면 상품까지 같이 삭제된다.
        DatabaseConnectionGenerator.get_session().query(User).delete()

    def test_create(self):
        """ 상품(만) 생성 (펀딩관련 생성 X)

            * 상품 이름이 128자를 넘어가면 안된다.
            * 상품 설명이 2048자를 넘어가면 안된다.
            * 펀딩 종료일은 과거여도 상관없음
            * 하나의 유저가 동일한 이름의 상품을 생성할 수 없다.
        """

        # 상품을 등록할 유저 생성
        user_name: str = "유저01"
        UserQuery.create(user_name)
        user_id: str = UserQuery.read("name", user_name)['id']

        # 테스팅을 위한 default data
        default_name: str = "펀딩 이벤트"
        default_end_time: datetime.datetime = datetime.datetime.now() + datetime.timedelta(days=7)
        default_summary: str = "펀딩 예시 설명 입니다."

        # 1.1 상품 이름이 비어있으면 안된다.
        self.assertEqual(ItemQuery.create(["id", user_id], "", default_summary, default_end_time),
                         Item.NAME_NOT_MATCHED)

        # 1.2 상품 이름이 128자를 넘어가면 안된다
        self.assertEqual(ItemQuery.create(["id", user_id], "x"*129, default_summary, default_end_time),
                         Item.NAME_NOT_MATCHED)

        # 2. 상품 설명이 2048자를 넘어가면 안된다.
        self.assertEqual(ItemQuery.create(["id", user_id], default_name, "x"*2049, default_end_time),
                         Item.SUMMARY_NOT_MATCHED)

        # 3. 펀딩 종료일이 비어있으면 안된다.
        self.assertEqual(ItemQuery.create(["id", user_id], default_name, default_summary, None),
                         Item.SUMMARY_NOT_MATCHED)

        # 정상적인 입력
        self.assertEqual(ItemQuery.create(["id", user_id], default_name, default_summary, default_end_time),
                         0)

        # 4. 동일한 유전자가 동일한 이름의 상품을 생성할 수 없다
        self.assertEqual(ItemQuery.create(["id", user_id], default_name, default_summary, default_end_time),
                         Item.ITEM_ALREADY_EXISTS)


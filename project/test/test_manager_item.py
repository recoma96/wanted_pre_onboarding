import unittest
from typing import Dict
import datetime

from connection.connection_generator import DatabaseConnectionGenerator
from manager.item_manager import ItemManager
from manager.user_manager import UserManager
from model.model import rdb_create_all, remove_test_db, User, Item, ItemContents


class TestUserManager(unittest.TestCase):
    """ ItemManager 테스트

        validate 테스트 보다는
        Manager가 데이터를 제대로 저장하고 있는 가에 대한 부분을 테스트
    """

    user_manager: UserManager = None
    item_manager: ItemManager = None

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

    def setUp(self) -> None:
        self.user_manager = UserManager()
        self.item_manager = ItemManager()

    def tearDown(self) -> None:
        # 테스트 함수가 끝날 때마다 호출
        # 모든 데이터 전부 삭제
        db_session = DatabaseConnectionGenerator.get_session()
        db_session.query(ItemContents).delete()
        db_session.query(Item).delete()
        db_session.query(User).delete()

    def test_create_and_read(self):
        """ 상품 등록 및 읽기 테스트

            펀딩 버튼 누르기도 같이 테스트 한다.
        """

        user_name: str = "유저01"

        answer_item: Dict[str, object] = {
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

        # 선 유저 생성
        self.user_manager.add_user(user_name)

        # 상품 생성
        self.item_manager.add_item(
            user_name=user_name,
            title=answer_item['name'],
            summary=answer_item['summary'],
            end_date=answer_item['end_date'],
            funding_unit=answer_item['funding_unit'],
            target_money=answer_item['target_money']
        )

        # 펀딩 카운팅
        for _ in range(answer_item['participant_size']):
            self.assertTrue(self.item_manager.donate_funding(item_name=answer_item['name']))

        # 데이터 가져오기
        res: Dict[str, object] = self.item_manager.get_item(item_name=answer_item['name'])

        # 검토
        for k, v in answer_item.items():
            # 데이터가 맞는 지 확인
            self.assertEqual(answer_item[k], res[k])

    def test_update(self):
        """ 상품 수정 """
        user_name: str = "유저01"

        answer_item: Dict[str, object] = {
            # 예상 정답
            "name": "상품1",
            "summary": "상품 설명",
            "user_name": user_name,
            "end_date": datetime.datetime.now() + datetime.timedelta(days=3),
            "funding_unit": 1000,  # 1회 펀딩 당 금액
            "target_money": 10000,  # 목표 달성 금액
            "current_money": 0,  # 현재 달성 금액
            "participant_size": 0,  # 참가자 수
            "funding_gage": 0,  # 달성률
        }

        # 선 유저 생성
        self.user_manager.add_user(user_name)

        # 상품 생성
        self.item_manager.add_item(
            user_name=user_name,
            title=answer_item['name'],
            summary=answer_item['summary'],
            end_date=answer_item['end_date'],
            funding_unit=answer_item['funding_unit'],
            target_money=answer_item['target_money']
        )

        res = self.item_manager.get_item(item_name=answer_item['name'])

        # 일부 데이터 수정
        answer_item['name'] = "수정된 상품"
        answer_item['end_date'] = datetime.datetime.now() + datetime.timedelta(days=30)
        self.item_manager.update_item(item_id=res['item_id'],
                                      title=answer_item['name'],
                                      end_date=answer_item['end_date'])

        # 데이터 가져오기
        res: Dict[str, object] = self.item_manager.get_item(item_name=answer_item['name'])

        # 검토
        for k, v in answer_item.items():
            # 데이터가 맞는 지 확인
            self.assertEqual(answer_item[k], res[k])

    def test_delete(self):
        """ 상품 삭제 """

        user_name: str = "유저01"

        cur_item: Dict[str, object] = {
            # 예상 정답
            "name": "상품1",
            "summary": "상품 설명",
            "user_name": user_name,
            "end_date": datetime.datetime.now() + datetime.timedelta(days=3),
            "funding_unit": 1000,  # 1회 펀딩 당 금액
            "target_money": 10000,  # 목표 달성 금액
        }

        # 선 유저 생성
        self.user_manager.add_user(user_name)

        # 상품 생성
        self.item_manager.add_item(
            user_name=user_name,
            title=cur_item['name'],
            summary=cur_item['summary'],
            end_date=cur_item['end_date'],
            funding_unit=cur_item['funding_unit'],
            target_money=cur_item['target_money']
        )

        # 삭제
        self.item_manager.remove_item(item_name=cur_item['name'])

        # 삭제여부 확인
        self.assertIsNone(self.item_manager.get_item(item_name=cur_item['name']))
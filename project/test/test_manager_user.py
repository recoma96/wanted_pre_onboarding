import unittest

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.manager.user_manager import UserManager
from project.model.model import rdb_create_all, remove_test_db, User, Item
from project.query.err_codes import UserQueryErrorCode


class TestUserManager(unittest.TestCase):
    """ UserManager 테스트
        
        validate 테스트 보다는
        Manager가 데이터를 제대로 저장하고 있는 가에 대한 부분을 테스트
    """

    user_manager: UserManager = None

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

    def tearDown(self) -> None:
        # 테스트 함수가 끝날 때마다 호출
        # 모든 데이터 전부 삭제
        db_session = DatabaseConnectionGenerator.get_session()
        db_session.query(Item).delete()
        db_session.query(User).delete()

    def test_create_and_read(self):
        user_name: str = "유저01"
        self.user_manager.add_user(name=user_name)
        self.assertEqual(self.user_manager.get_user(name=user_name)['name'], user_name)

        # 없는 유저일 경우 None 리턴
        self.assertIsNone(self.user_manager.get_user(name="안녕01"))

        # 이미 있는 이름의 유저 생성 불가
        self.assertEqual(self.user_manager.add_user(user_name), UserQueryErrorCode.NAME_ALREADY_EXIST.value)

    def test_edit_username(self):
        user_names = ['유저01', '유저02']
        for user_name in user_names:
            self.user_manager.add_user(name=user_name)

        # 테스트 대상의 유저 데이터들
        user01 = self.user_manager.get_user(user_names[0])
        user02 = self.user_manager.get_user(user_names[1])

        # 변경 성공
        self.assertTrue(self.user_manager.update_user(user_id=user01['id'], new_name="새로운유저"))
        self.assertEqual(self.user_manager.get_user(user_id=user01['id'])['name'], "새로운유저")

        # 동일 이름 변경 불가능
        self.assertFalse(self.user_manager.update_user(user_name=user01['name'], new_name=user02['name']))

import unittest

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import rdb_create_all, remove_test_db, User


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
            * 펀딩 종료일은 과거여도 상관없음
            * 동일한 이름의 상품을 생성할 수 없다.
            * 없는 유저에 상품을 등록할 수 없다.
        """
        pass

    def test_read(self):
        """ 하나의
        """
        pass

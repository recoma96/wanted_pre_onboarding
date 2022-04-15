import unittest

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import rdb_create_all, remove_test_db, User, DatabaseRegexNotMatched
from project.query.user_query import UserQuery


class TestUserQuery(unittest.TestCase):
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
        DatabaseConnectionGenerator.get_session().query(User).delete()

    def test_create(self):
        """ 유저 생성에 대한 테스트
            유저이름은 영어/숫자/한글로 1자 이상 64자 이하여야 한다.

            테스팅 내역
            1. name이 비어있는 경우
            2. name이 65자
            3. 한글/영어/숫자가 아닌 다른 단어가 들어가는 경우 에러 처리
            4. 정상적인 생성
            5. 같은 이름은 생성 불가
        """

        # 1. 이름이 비어있음
        self.assertEqual(UserQuery.create(""), User.NAME_NOT_MATCHED,
                         msg="생성하고자 하는 유저 이름이 비어있어선 안됩니다.")

        # 2. 65자 이상의 이름이 들어가 있으면 안된다.
        self.assertEqual(UserQuery.create("a" * 65), User.NAME_NOT_MATCHED,
                         msg="이름이 65자 이상이면 안됩니다.")

        # 3. 한글/영어 숫자가 아닌 다른 단어가 들어가면 안됨(1)
        self.assertEqual(UserQuery.create("         "), User.NAME_NOT_MATCHED,
                         msg="이름에는 한글/영어/숫자 만 들어가야 합니다.")

        # 3. 한글/영어 숫자가 아닌 다른 단어가 들어가면 안됨(2)
        self.assertEqual(UserQuery.create("()///)"), User.NAME_NOT_MATCHED,
                         msg="이름에는 한글/영어/숫자 만 들어가야 합니다.")

        # 4. 정상적인 생성

        self.assertEqual(UserQuery.create("하정현96"), 0,
                         msg="유저를 생성하는데 문제가 발생했습니다.")

        # 5.동일 이름 생성 불가
        self.assertEqual(UserQuery.create("하정현96"), User.NAME_ALREADY_EXIST,
                         msg="유저를 생성하는데 문제가 발생했습니다.")

    def test_read(self):
        """ 일부 문자가 포함되어 있는 이름 출력
            해당 과제의 요규사항에는 없으나 CRUD Function을 원칙대로 작성하기 위해
            추가 구현
            
            테스팅 내역
            일부 문자에 대한 검색
        """
        pass

    def test_update(self):
        """ 유저 이름 변경
            테스팅 내역은 create와 동일
        """
        pass

    def test_remove(self):
        """ 해당 이름의 유저를 삭제

            테스팅 내역
            1. 존재하는 이름을 삭제하는 경우.
            2. 존재하지 않는 이름을 삭제하는 경우.
        """
        pass

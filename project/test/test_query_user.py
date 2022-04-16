import unittest
from typing import List, Dict

from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import rdb_create_all, remove_test_db, User
from project.query.err_codes import UserQueryErrorCode
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
        self.assertEqual(UserQuery.create(""), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="생성하고자 하는 유저 이름이 비어있어선 안됩니다.")

        # 2. 65자 이상의 이름이 들어가 있으면 안된다.
        self.assertEqual(UserQuery.create("a" * 65), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="이름이 65자 이상이면 안됩니다.")

        # 3. 한글/영어 숫자가 아닌 다른 단어가 들어가면 안됨(1)
        self.assertEqual(UserQuery.create("         "), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="이름에는 한글/영어/숫자 만 들어가야 합니다.")

        # 3. 한글/영어 숫자가 아닌 다른 단어가 들어가면 안됨(2)
        self.assertEqual(UserQuery.create("()///)"), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="이름에는 한글/영어/숫자 만 들어가야 합니다.")

        # 4. 정상적인 생성

        self.assertEqual(UserQuery.create("하정현96"), UserQueryErrorCode.SUCCEED,
                         msg="유저를 생성하는데 문제가 발생했습니다.")

        # 5.동일 이름 생성 불가
        self.assertEqual(UserQuery.create("하정현96"), UserQueryErrorCode.NAME_ALREADY_EXIST,
                         msg="유저를 생성하는데 문제가 발생했습니다.")

    def test_read(self):
        # 정보를 갖고오는 지에 대한 테스트

        UserQuery.create("안녕하세요")
        self.assertEqual(UserQuery.read("name", "안녕하세요")['name'], "안녕하세요")

        # 존재하지 않는 정보
        self.assertIsNone(UserQuery.read("name", "안녕"))

        # 잘못된 key 이름
        self.assertRaises(TypeError, UserQuery.read, "???", "안녕하세요")

    def test_read_namelist(self):
        """ 일부 문자가 포함되어 있는 이름 출력
            해당 과제의 요규사항에는 없으나 추후 확장 구현을 위해
            추가 구현
            
            테스팅 내역
            일부 문자에 대한 검색
        """
        self.assertEqual(UserQuery.create("안녕하세요"), UserQueryErrorCode.SUCCEED)
        self.assertEqual(UserQuery.create("란녕하세요"), UserQueryErrorCode.SUCCEED)
        self.assertEqual(UserQuery.create("유저이름"), UserQueryErrorCode.SUCCEED)

        output: List[str] = []
        # 검색
        res = UserQuery.search_users("녕하")
        # name List로 변환
        for user in res:
            output.append(user['name'])
        self.assertListEqual(sorted(output), sorted(["안녕하세요", "란녕하세요"]))

    def test_update(self):
        """ 유저 이름 변경
            테스팅 내역은 create와 동일
        """
        UserQuery.create("유저01")
        UserQuery.create("유저02")
        user: Dict[str, str] = UserQuery.read("name", "유저01")
        user_id, user_name = user['id'], user['name']

        # 0: 존재하지 않는 유저의 데이터를 수정하려고 함
        self.assertEqual(UserQuery.update("name", "안녕", "안녕2"), UserQueryErrorCode.USER_NOT_EXIST,
                         msg="이 유저는 없는 유저 입니다.")

        # 1. 이름이 비어있음
        self.assertEqual(UserQuery.update("id", user_id, ""), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="생성하고자 하는 유저 이름이 비어있어선 안됩니다.")

        # 2. 65자 이상의 이름이 들어가 있으면 안된다.
        self.assertEqual(UserQuery.update("name", user_name, "a" * 65), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="이름이 65자 이상이면 안됩니다.")

        # 3. 한글/영어 숫자가 아닌 다른 단어가 들어가면 안됨(1)
        self.assertEqual(UserQuery.update("id", user_id, "         "), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="이름에는 한글/영어/숫자 만 들어가야 합니다.")

        # 3. 한글/영어 숫자가 아닌 다른 단어가 들어가면 안됨(2)
        self.assertEqual(UserQuery.update("id", user_id, "()///)"), UserQueryErrorCode.NAME_NOT_MATCHED,
                         msg="이름에는 한글/영어/숫자 만 들어가야 합니다.")

        # 4. 동일 이름 수정 불가
        self.assertEqual(UserQuery.update("id", user_id, "유저02"), UserQueryErrorCode.NAME_ALREADY_EXIST,
                         msg="유저를 생성하는데 문제가 발생했습니다.")

        # 5. 정상적인 생성
        self.assertEqual(UserQuery.update("id", user_id, "하정현96"), UserQueryErrorCode.SUCCEED,
                         msg="유저를 생성하는데 문제가 발생했습니다.")

        # 6. 맞지 않는 키 사용
        self.assertRaises(TypeError, UserQuery.update, "???", user_id, "하정현97")

    def test_remove(self):
        """ 해당 이름의 유저를 삭제

            테스팅 내역
            1. 존재하는 이름을 삭제하는 경우.
            2. 존재하지 않는 이름을 삭제하는 경우.
        """
        UserQuery.create("유저01")
        self.assertEqual(UserQuery.delete("name", "유저01"), UserQueryErrorCode.SUCCEED)
        self.assertEqual(UserQuery.delete("id", "x"*60), UserQueryErrorCode.USER_NOT_EXIST)
        self.assertEqual(UserQuery.delete("name", "유저01"), UserQueryErrorCode.USER_NOT_EXIST)

import json
import unittest

from project.apis.api_values import API_RES_FAILED
from project.app import app
from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import ItemContents, Item


class TestApi(unittest.TestCase):
    api = app.test_client()

    @classmethod
    def tearDownClass(cls) -> None:
        # 테스트 함수가 끝날 때마다 호출
        # 모든 데이터 전부 삭제
        db_session = DatabaseConnectionGenerator.get_session()
        db_session.query(ItemContents).delete()
        db_session.query(Item).delete()

    def test_user(self):
        """ User API Test """

        # 유저 두개 등록
        user_names = ["user01", "user02"]
        user_info = []

        for user_name in user_names:
            # OK이어야 통과
            res = self.api.post(f"/user/{user_name}")
            self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], 'OK')

        for user_name in user_names:
            # 유저 정보 갖고오기

            res = self.api.get(f"/user/{user_name}")
            data = json.loads(res.data.decode('utf-8'))['data']

            self.assertEqual(data['name'], user_name)
            user_info.append(data['name'])

        new_name = "안녕하세요"

        # 정보 수정하기
        res = self.api.put(f"/user/{user_names[0]}", json={"name": new_name})
        self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], 'OK')

        # 수정된 정보 확인하기
        res = self.api.get(f"/user/{new_name}")
        data = json.loads(res.data.decode('utf-8'))['data']
        self.assertEqual(data['name'], new_name)

        # 기존 이름은 없어져야 한다
        res = self.api.get(f"/user/{user_names[0]}")
        data = json.loads(res.data.decode('utf-8'))['result']
        self.assertEqual(data, API_RES_FAILED)

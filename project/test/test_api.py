import csv
import json
import re
import unittest

from project.apis.api_values import API_RES_FAILED, API_RES_OK
from project.app import app
from project.connection.connection_generator import DatabaseConnectionGenerator
from project.model.model import ItemContents, Item, remove_test_db


class TestApi(unittest.TestCase):
    api = app.test_client()

    def tearDown(self) -> None:
        # 테스트 함수가 끝날 때마다 호출
        # 모든 데이터 전부 삭제
        db_session = DatabaseConnectionGenerator.get_session()
        db_session.query(ItemContents).delete()
        db_session.query(Item).delete()

    @classmethod
    def tearDownClass(cls) -> None:
        # 테스트 클래스 자체 종료
        # DB 자체 제거
        DatabaseConnectionGenerator.get().disconnect()
        remove_test_db()

    def test_user(self):
        """ User API Test """

        # 유저 두개 등록
        user_names = ["user01", "user02"]
        user_info = []

        for user_name in user_names:
            # OK이어야 통과
            res = self.api.post(f"/user/{user_name}")
            self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], API_RES_OK)

        for user_name in user_names:
            # 유저 정보 갖고오기

            res = self.api.get(f"/user/{user_name}")
            data = json.loads(res.data.decode('utf-8'))['data']

            self.assertEqual(data['name'], user_name)
            user_info.append(data['name'])

        new_name = "안녕하세요"

        # 정보 수정하기
        res = self.api.put(f"/user/{user_names[0]}", json={"name": new_name})
        self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], API_RES_OK)

        # 수정된 정보 확인하기
        res = self.api.get(f"/user/{new_name}")
        data = json.loads(res.data.decode('utf-8'))['data']
        self.assertEqual(data['name'], new_name)

        # 기존 이름은 없어져야 한다
        res = self.api.get(f"/user/{user_names[0]}")
        data = json.loads(res.data.decode('utf-8'))['result']
        self.assertEqual(data, API_RES_FAILED)

    def test_item(self):
        # 상품 api 테스트

        user_name = "유저"
        example_item = {
            # 예제 상품
            "item_name": "상품1",
            "summary": "상품 설명",
            "user_name": user_name,
            "end_date": "2022/08/11 18:00:00",
            "funding_unit": 1000,  # 1회 펀딩 당 금액
            "target_money": 10000,  # 목표 달성 금액
            "current_money": 6000,  # 현재 달성 금액
            "participant_size": 6,  # 참가자 수
            "funding_gage": 60.0,  # 달성률
        }

        # 유저 생성
        self.api.post(f"/user/{user_name}")

        # 상품 생성
        input_data = example_item.copy()
        del input_data['item_name']
        del input_data['participant_size']
        del input_data['funding_gage']

        res = self.api.post(f"/item/{example_item['item_name']}", json=input_data)
        self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], API_RES_OK)

        # 펀딩 버튼 누르기
        for _ in range(example_item['participant_size']):
            res = self.api.put(f"/item/{example_item['item_name']}/donate")
            self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], API_RES_OK)

        # 정보 변경해보기
        new_item_name = "바뀐 상품 이름"
        end_date = "2022/08/11 20:00:00"
        res = self.api.put(f"/item/{example_item['item_name']}", json={
            "name": new_item_name,
            "end_date": end_date
        })
        self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], API_RES_OK)
        example_item['item_name'], example_item['end_date'] = new_item_name, end_date

        # 데이터 가져오기
        res = self.api.get(f"/item/{example_item['item_name']}")
        res = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res['result'], API_RES_OK)

        res = res['data']
        # 변경 사항 검토
        for k in example_item:
            self.assertEqual(example_item[k], res[k])

        # 상품 정보 삭제하기
        res = self.api.delete(f"/item/{example_item['item_name']}")
        self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], API_RES_OK)

        # 삭제가 되어있는 지 확인
        res = self.api.get(f"/item/{example_item['item_name']}")
        self.assertEqual(json.loads(res.data.decode('utf-8'))['result'], API_RES_FAILED)

    def test_item_list(self):
        # 상품 리스트 및 정렬 api 구현

        # 유저 생성
        user_name: str = "유저이름"
        inputs = []
        self.api.post(f"/user/{user_name}")

        # 데이터 준비
        with open("test/inputs/api_item_test.csv", "rt") as f:
            reader = csv.reader(f)

            for item_name, summary, end_date, funding_unit, target_money, current_money in reader:

                if item_name == "name":
                    # 맨 상단의 제목 틀은 제외
                    continue

                res = self.api.post(f"/item/{item_name}", json={
                    # 상품 등록 요청
                    "user_name": user_name,
                    "summary": summary,
                    "funding_unit": int(funding_unit),
                    "target_money": int(target_money),
                    "end_date": end_date
                })

                # 제대로 들어가 있는 지 확인
                res = json.loads(res.data.decode('utf-8'))
                self.assertEqual(res['result'], API_RES_OK)

                for _ in range(int(current_money) // int(funding_unit)):
                    # current_money 까지 도네 버튼 누르기
                    self.api.put(f"/item/{item_name}/donate")

                inputs.append({
                    # 곌과 비교를 위한 input 데이터 정리
                    "item_name": item_name,
                    "current_money": int(current_money)
                })

        # 문자열을 이용한 검색
        search_word = "하고 싶다"
        res = self.api.get(f"item/list?search={search_word}")
        res = json.loads(res.data.decode('utf-8'))

        regex = re.compile(rf"^.*({search_word}).*")

        # 문자열 검색 결과 비교
        __answer = [d['item_name'] for d in inputs if regex.match(d['item_name'])]
        __output = [d['item_name'] for d in res['data']]
        self.assertListEqual(sorted(__answer), sorted(__output))

        # 총펀딩금액 기준 리스트 구하기
        res = self.api.get(f"/item/list?order_by=총펀딩금액")
        res = json.loads(res.data.decode('utf-8'))

        __answer = [e['item_name'] for e in sorted(inputs, key=lambda d: -d["current_money"])]
        __output = [d['item_name'] for d in res['data']]
        self.assertListEqual(__answer, __output)

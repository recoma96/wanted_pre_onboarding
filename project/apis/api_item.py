from flask_restx import Resource, Namespace
from flask import request

from apis.api_values import *
from manager.item_manager import ItemManager
import datetime

api_item = Namespace('Item')


@api_item.route('/<string:item_name>')
class APIItem(Resource):
    def post(self, item_name):
        # 새 아이템 생성

        data = request.json
        try:
            res = ItemManager().add_item(
                user_name=data['user_name'],
                title=item_name,
                end_date=datetime.datetime.strptime(data['end_date'], "%Y/%m/%d %H:%M:%S"),
                summary=data['summary'],
                funding_unit=data['funding_unit'],
                target_money=data['target_money'],
            )
        except Exception:
            return {"result": API_RES_ERROR}

        if res == 0:
            # 성공
            return {"result": API_RES_OK}
        else:
            # 실패
            return {"result": API_RES_FAILED}

    def get(self, item_name):
        # 상품 정보 수정하기
        try:
            res = ItemManager().get_item(item_name)
        except Exception:
            return {"result": API_RES_FAILED, "data": None}
        if res:
            # 성공
            # 필요한 정보만 걸러서 출력
            del res['item_id']

            # 헷갈림 방지를 위한 key 변경
            # name을 item name 즉 상품 이름으로 변경
            item_name = res['name']
            del res['name']
            res['item_name'] = item_name

            # datetime은 json으로 포맷이 불가능하므로 string으로 바꾼다.
            res['end_date'] = datetime.datetime.strftime(res['end_date'], "%Y/%m/%d %H:%M:%S")

            return {"result": API_RES_OK, "data": res}
        else:
            # 없음
            return {"result": API_RES_FAILED, "data": None}

    def put(self, item_name):
        # 상세 정보 갖고오기
        data = request.json
        try:
            res = ItemManager().update_item(
                # 수정할 항목이 data 안에 있으면 파라미터에 추가하고
                # 없으면 None처리 -> 해당 항목은 수정을 하지 않는 다는 얘기
                item_name=item_name,
                title=None if 'name' not in data else data['name'],
                summary=None if 'summary' not in data else data['summary'],
                end_date=None if 'end_date' not in data else datetime.datetime.strptime(data['end_date'],
                                                                                        "%Y/%m/%d %H:%M:%S"),
                funding_unit=None if 'funding_unit' not in data else data['funding_unit'],
                participant_size=None if "participant_size" not in data else data['participant_size'],
                current_money=None if "current_money" not in data else data['current_money'],
            )
        except Exception:
            return {"result": API_RES_FAILED}

        if res:
            # 성공
            return {"result": API_RES_OK}
        else:
            # 실패
            return {"result": API_RES_FAILED}

    def delete(self, item_name):
        # 상품 정보 삭제
        try:
            res = ItemManager().remove_item(item_name=item_name)
        except Exception:
            return {"result": API_RES_FAILED}
        if res == 0:
            # 성공
            return {"result": API_RES_OK}
        else:
            # 실패
            return {"result": API_RES_FAILED}


@api_item.route('/<string:item_name>/donate')
class APIItemDonate(Resource):

    def put(self, item_name):
        # 도네 펀딩 버튼
        try:
            res = ItemManager().donate_funding(item_name=item_name)
        except Exception:
            return {"result": API_RES_FAILED}

        if res:
            # 성공
            return {"result": API_RES_OK}
        else:
            # 실패
            return {"result": API_RES_FAILED}


@api_item.route('/list')
class APIItemList(Resource):
    # 아이템 리스트 갖고오기
    def get(self):
        args = dict(request.args)
        res = []

        if 'search' in args:
            # 문자열 패턴을 이용한 검색
            try:
                res = ItemManager().get_list(args['search'])
            except Exception:
                return {"result", API_RES_ERROR}
        elif 'order_by' in args:
            # 순서를 이용한 검색
            try:
                if args['order_by'] == "총펀딩금액":
                    res = ItemManager().sort(sort_type="funding")
                elif args['order_by'] == "생성일":
                    res = ItemManager().sort(sort_type="create_date")
                else:
                    raise ValueError("order by args not matched")
            except Exception:
                return {"result", API_RES_ERROR}

        # result data 가공
        for idx in range(len(res)):
            # 상품 이름을 나타내는 name을 item_name으로 변경
            __item_name = res[idx]['name']
            del res[idx]['name']
            res[idx]['item_name'] = __item_name

            # 달성률에 소수점 제거
            res[idx]["percentage"] = int(res[idx]['percentage'])
            
            # d-day 작성
            # 종료일이 지나지 않으면 음수, 종료일이 지나면 +
            res[idx]["d-day"] = (datetime.datetime.now() - res[idx]['end_date']).days

            # 마감일/시작일은 요구사항에 포함되지 않으므로 전부다 삭제
            del res[idx]['end_date']
            del res[idx]['create_date']

        return {"result": API_RES_OK, "data": res}

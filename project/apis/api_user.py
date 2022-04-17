from flask_restx import Resource, Namespace
from flask import request

from project.apis.api_values import *
from project.manager.user_manager import UserManager

api_user = Namespace('User')


@api_user.route('/<string:username>')
class APIUser(Resource):
    def post(self, username):
        # 새 유저 생성

        try:
            res = UserManager().add_user(username)
        except Exception:
            # 내부 에러 발생 시
            return {"result": API_RES_ERROR}

        if res == 0:
            # 성공
            return {"result": API_RES_OK}
        else:
            # 실패
            return {"result": API_RES_FAILED}

    def get(self, username):
        # 새 유저 정보 가져오기
        try:
            res = UserManager().get_user(name=username)
        except Exception:
            return {"data": None, "result": API_RES_ERROR}

        if not res:
            # 정보가 없음
            return {"data": None, "result": API_RES_FAILED}
        else:
            return {"data": res, "result": API_RES_OK}

    def put(self, username):
        # 유저 이륾 변경

        try:
            new_name: str = request.json['name']
            res = UserManager().update_user(user_name=username, new_name=new_name)
        except Exception:
            # 요구 데이터를 못찾음
            # 혹은 내부에서 에러 발생
            return {"result": API_RES_ERROR}
        if not res:
            # 수정 실패
            return {"result": API_RES_FAILED}
        else:
            # 수정 성공
            return {"result": API_RES_OK}
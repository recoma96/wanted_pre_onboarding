from flask import Flask
from flask_restx import Api

from apis.api_item import api_item
from apis.api_user import api_user
from connection.connection_generator import DatabaseConnectionGenerator
from manager.item_manager import ItemManager
from manager.user_manager import UserManager
from model.model import rdb_create_all

app = Flask(__name__)
api = Api(app)

# res api 등록
api.add_namespace(api_user, '/user')
api.add_namespace(api_item, '/item')

# databsae 생성
# 테스트인지 배포용인지 해당 객체 내에서 알아서 구별해서 DB를 실행 및 생성한다.
# 자세한건 DatabaseConnectionGenerator 클래스 참고


DatabaseConnectionGenerator.get().connect()
rdb_create_all()


user_manager = UserManager()
item_manager = ItemManager()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)

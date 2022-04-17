from project.manager.manager import Manager
import datetime


class ItemManager(Manager):

    def __new__(cls, *args, **kwargs):
        # 하나의 서버에 하나의 객체만 있어야 하기 때문에 Singletone Pattern 도입
        if not hasattr(cls, 'item_manager_instance'):
            cls.user_manager_instance = super(ItemManager, cls).__new__(cls)
        return cls.item_manager_instance

    def add_item(
            self,
            title: str,
            summary: str,
            target_money: int,
            end_date: datetime.datetime,
            funding_unit: int,
            user_id: str = None,
            user_name: str = None,

    ):
        pass

    def update_item(
            self,
            title: str = None,
            summary: str = None,
            end_date: datetime.datetime = None,
            funding_unit: int = None,
            participant_size: int = None,
            current_money: int = None,
            item_name: str = None,
            item_id: str = None,
    ):
        pass

    def get_item(self, item_name: str = None, item_id: str = None):
        pass

    def sort(self, sort_type: str):
        pass

    def donate_funding(
            self,
            item_name: str = None,
            item_id: str = None
    ):
        # 버튼 클릭시 작동
        pass

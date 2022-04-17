from typing import Optional, List

from manager.manager import Manager
import datetime

from query.err_codes import ItemQueryErrorCode
from query.item_query import ItemQuery


class ItemManager(Manager):

    def __new__(cls, *args, **kwargs):
        # 하나의 서버에 하나의 객체만 있어야 하기 때문에 Singletone Pattern 도입
        if not hasattr(cls, 'item_manager_instance'):
            cls.item_manager_instance = super(ItemManager, cls).__new__(cls)
        return cls.item_manager_instance

    def add_item(
            self,
            title: str,
            summary: str,
            target_money: int,
            end_date: datetime.datetime,
            funding_unit: int,
            user_id: Optional[str] = None,
            user_name: Optional[str] = None,

    ):
        """

        :param title: 상품명
        :param summary: 설명
        :param target_money: 목표 금액
        :param end_date: 종료 날짜
        :param funding_unit: 1회펀딩당 금액
        :param user_id: 게시자 아이디 Optional
        :param user_name: 유저 아이디 Optional
        :return:
        """

        user_info: Optional[List] = None
        try:
            if user_id:
                user_info = ["id", user_id]
            elif user_name:
                user_info = ["name", user_name]
            return ItemQuery.create(
                user=user_info,
                name=title,
                summary=summary,
                target_money=target_money,
                end_date=end_date,
                funding_unit=funding_unit
            ).value
        except Exception as e:
            raise e

    def update_item(
            self,
            title: Optional[str] = None,
            summary: Optional[str] = None,
            end_date: Optional[datetime.datetime] = None,
            funding_unit: Optional[int] = None,
            participant_size: Optional[int] = None,
            current_money: Optional[int] = None,
            item_name: Optional[str] = None,
            item_id: Optional[str] = None,
    ):
        """
        :param title:  새 상품명
        :param summary: 새 설명란
        :param end_date: 새 종료시간
        :param funding_unit: 새 1회당 펀딩 금액
        :param participant_size: 새 참가자 수
        :param current_money: 새 현재 펀딩된 금액
        :param item_name: 수정 대상의 상품 이름
        :param item_id: 수정 대상의 상품 고유 아이디
        """
        d = None
        if item_id:
            d = ['id', item_id]
        elif item_name:
            d = ['name', item_name]
        return ItemQuery.update(
            item_code=d,
            name=title,
            summary=summary,
            end_date=end_date,
            funding_unit=funding_unit,
            participant_size=participant_size,
            current_money=current_money
        )

    def get_item(self, item_name: Optional[str] = None, item_id: Optional[str] = None):

        d = None

        if item_id:
            d = ['id', item_id]
        elif item_name:
            d = ['name', item_name]

        return ItemQuery.read(*d)

    def remove_item(self, item_name: Optional[str] = None, item_id: Optional[str] = None):
        if item_id:
            return ItemQuery.delete("id", item_id).value
        elif item_name:
            return ItemQuery.delete("name", item_name).value

    def get_list(self, regex: str):
        return ItemQuery.read_item_list_by_name_regex(regex)

    def sort(self, sort_type: str):
        # 정렬
        if sort_type == "funding":
            return ItemQuery.sort_by_fundingmoney()
        elif sort_type == "create_date":
            return ItemQuery.sort_by_createdate()
        else:
            raise TypeError("Type not matched")

    def donate_funding(
            self,
            item_name: Optional[str] = None,
            item_id: Optional[str] = None
    ) -> bool:

        """ 펀딩 버튼

        :param item_name: 아이템 이름
        :param item_id: 아이템 아이디
        :return: 성공 시 True, 실패 시 False(보통 상품이 없는 경우)
        """

        if item_id:
            d = ['id', item_id]
        else:
            d = ['name', item_name]

        # 상품 가져오기
        item_info = ItemQuery.read(*d)

        if not item_info:
            # 상품 없음
            return False

        # 펀딩 하나 올리기
        item_info["participant_size"] += 1
        item_info['current_money'] += item_info['funding_unit']

        # 상품 업데이트
        res_code = ItemQuery.update(
            d,
            participant_size=item_info['participant_size'],
            current_money=item_info['current_money'])

        if res_code == ItemQueryErrorCode.SUCCEED:
            return True
        else:
            return False

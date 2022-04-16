from enum import Enum


class ItemQueryErrorCode(Enum):
    """ ERROR CODES """
    SUCCEED: int = 0
    USER_ID_NOT_MATCHED: int = 1
    ITEM_ID_NOT_MATCHED: int = 2
    NAME_NOT_MATCHED: int = 3
    END_DATE_NOT_MATCHED: int = 4
    TARGET_MONEY_NOT_MATCHED: int = 5
    FUNDING_UNIT_NOT_MATCHED: int = 6
    USER_NOT_EXISTS: int = 7
    SUMMARY_MATCHED_FAILED: int = 8
    PARTICIPANT_SIZE_NOT_MATCHED: int = 9
    ITEM_ALREADY_EXISTS: int = 10
    CURRENT_MONEY_NOT_MATCHED: int = 11
    ITEM_NOT_EXISTS: int = 12

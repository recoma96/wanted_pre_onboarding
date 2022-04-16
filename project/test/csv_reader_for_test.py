import csv
import datetime
from typing import List, Dict


def csv_reader_for_test(root: str) -> List[Dict[str, object]]:
    """ 테스팅을 하기 위한 아이템 정보를 csv파일로부터 불러오기 """

    res: List[Dict[str, object]] = []

    with open(root, "rt") as f:
        reader = csv.reader(f)

        for idx, data in enumerate(reader):
            if idx == 0:
                continue

            name, summary, str_end_date, funding_unit, target_money, current_money = data

            funding_unit = int(funding_unit)
            target_money = int(target_money)
            current_money = int(current_money)
            end_date = datetime.datetime.strptime(str_end_date, "%Y/%m/%d %H:%M:%S")

            res.append({
                "name": name,
                "summary": summary,
                "funding_unit": funding_unit,
                "target_money": target_money,
                "end_date": end_date,
                "current_money": current_money
            })

    return res

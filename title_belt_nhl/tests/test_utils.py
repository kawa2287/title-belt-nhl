from datetime import date

import pytest

from title_belt_nhl.utils import ExcelDate


@pytest.mark.parametrize(
    "date_obj, expected_serial_date",
    [(date(2024, 10, 5), 45569), (date(2024, 10, 6), 45570), (date(2024, 10, 9), 45573)],
)
def test_excel_date_valid_date_obj(date_obj, expected_serial_date):
    ed = ExcelDate(date_obj=date_obj)
    assert ed.date_obj == date_obj
    assert ed.serial_date == expected_serial_date


@pytest.mark.parametrize(
    "serial_date, expected_date_obj",
    [(45569, date(2024, 10, 5)), (45570, date(2024, 10, 6)), (45573, date(2024, 10, 9))],
)
def test_excel_date_valid_serial_date(serial_date, expected_date_obj):
    ed = ExcelDate(serial_date=serial_date)
    assert ed.serial_date == serial_date
    assert ed.date_obj == expected_date_obj


def test_excel_date_invalid():
    with pytest.raises(
        ValueError,
        match="One of 'date_obj' or 'serial_date' is required to construct ExcelDate",
    ):
        ExcelDate()

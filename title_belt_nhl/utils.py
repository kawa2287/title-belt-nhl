from datetime import date

EXCEL_EPOCH_DATE: date = date(1900, 1, 1)


class ExcelDate:
    date_obj: date
    serial_date: int

    def __init__(self, date_obj: date = None, serial_date: int = None):
        if not date_obj and not serial_date:
            raise ValueError(
                "One of 'date_obj' or 'serial_date' is required to construct ExcelDate"
            )

        if date_obj:
            self.date_obj = date_obj
            self.serial_date = (date_obj - EXCEL_EPOCH_DATE).days + 1
        elif serial_date:
            self.date_obj = date.fromordinal(
                EXCEL_EPOCH_DATE.toordinal() + serial_date - 1
            )
            self.serial_date = serial_date

from pydantic import BaseModel, validator


class InputParameters(BaseModel):
    year: int
    percent: float

    @validator('year')
    def validate_year_value(cls, v):
        if 2020 < v < 2051:
            return v
        raise ValueError('значение отсутствует в диапазоне расчетов')

    @validator('percent')
    def validate_percent_value(cls, v):
        if v <= 0:
            raise ValueError('значение процента меньше 0')
        return v

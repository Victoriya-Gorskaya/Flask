from typing import Optional

from pydantic import BaseModel, validator


class CreateAd(BaseModel):
    title: str
    description: str
    owner: str

    @validator("title")
    def limit_length(cls, value):
        if 65 < len(value) < 1:
            raise ValueError('Title should be from 1 to 65 characters')
        return value
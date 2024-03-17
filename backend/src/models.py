from pydantic import BaseModel


class YTRecord(BaseModel):
    YTHash: str
    langs: list

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    id: int
    type: str
    title: str
    subtitle: str | None = None


class SearchResponse(BaseModel):
    results: list[SearchResultItem]

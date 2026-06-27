from pydantic import BaseModel, ConfigDict

class DropdownItem(BaseModel):
    id: int
    name: str


class VenueFormDataResponse(BaseModel):
    locations: list[DropdownItem]
    categories: list[DropdownItem]
    booking_types: list[DropdownItem]
    amenities: list[DropdownItem]
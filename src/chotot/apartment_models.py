from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .models import Listing


@dataclass
class ApartmentListing(Listing):
    """Extended model for apartment rental listings with apartment-specific fields."""

    # Apartment-specific fields
    rooms: Optional[int] = None  # Number of bedrooms
    bathrooms: Optional[int] = None  # Number of bathrooms
    floor: Optional[int] = None  # Floor number
    furnished: Optional[bool] = None  # Is the apartment furnished?
    furniture_type: Optional[str] = None  # "full", "partial", "none"
    building_name: Optional[str] = None  # Name of the building/complex
    balcony: Optional[bool] = None  # Has balcony?
    parking: Optional[bool] = None  # Has parking space?
    elevator: Optional[bool] = None  # Building has elevator?
    pets_allowed: Optional[bool] = None  # Are pets allowed?
    air_conditioning: Optional[bool] = None  # Has A/C?
    direction: Optional[str] = None  # Orientation (North, South, etc.)
    apartment_type: Optional[str] = None  # "studio", "duplex", "penthouse", etc.

    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including apartment-specific fields."""
        result = super().as_dict()
        # Add apartment-specific fields
        result.update({
            "rooms": self.rooms,
            "bathrooms": self.bathrooms,
            "floor": self.floor,
            "furnished": self.furnished,
            "furniture_type": self.furniture_type,
            "building_name": self.building_name,
            "balcony": self.balcony,
            "parking": self.parking,
            "elevator": self.elevator,
            "pets_allowed": self.pets_allowed,
            "air_conditioning": self.air_conditioning,
            "direction": self.direction,
            "apartment_type": self.apartment_type,
        })
        return result

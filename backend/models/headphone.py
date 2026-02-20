from pydantic import BaseModel, validator
from typing import List, Optional, Union

class Headphone(BaseModel):
    price: Union[float, str]
    battery_life: Optional[Union[float, str]]  # in hours, None for wired
    latency: Union[float, str]  # in ms
    num_mics: Union[int, str]  # number of microphones (0-16)
    device_type: str  # wired, wireless, neckband, earbuds
    water_resistance: Union[float, str]  # score from 0 to 1 or IPX rating
    driver_size: Optional[Union[float, str]] = None  # driver size in mm
    name: Optional[str] = None  # headphone model name
    
    @validator('price', 'battery_life', 'latency', 'driver_size', pre=True)
    def convert_numeric(cls, v):
        if v == '' or v is None:
            return None
        if isinstance(v, str):
            return float(v) if v else None
        return v
    
    @validator('num_mics', pre=True)
    def convert_num_mics(cls, v):
        if v == '' or v is None:
            return 0
        if isinstance(v, str):
            return int(v) if v else 0
        return min(16, max(0, int(v)))
    
    @validator('water_resistance', pre=True)
    def convert_water_resistance(cls, v):
        if isinstance(v, str):
            mapping = {'None': 0.0, 'IPX1': 0.1, 'IPX2': 0.2, 'IPX3': 0.3, 'IPX4': 0.4, 
                      'IPX5': 0.5, 'IPX6': 0.6, 'IPX7': 0.7, 'IPX8': 0.8}
            return mapping.get(v, 0.4)
        return v

class UseCase(BaseModel):
    name: str
    percentage: Union[float, int]  # percentage weight for this use case

class UserRequest(BaseModel):
    headphones: List[Headphone]
    use_cases: List[UseCase]

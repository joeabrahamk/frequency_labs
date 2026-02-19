from pydantic import BaseModel, field_validator
from typing import List, Optional, Union

class Headphone(BaseModel):
    price: Union[float, str]
    battery_life: Optional[Union[float, str]]  # in hours, None for wired
    latency: Union[float, str]  # in ms
    num_mics: Union[int, str]  # number of microphones (0-16)
    anc_strength: Union[float, str]  # score from 0 to 1 or strength label
    comfort_score: Union[float, str]  # score from 0 to 1 or comfort label
    device_type: str  # wired, wireless, neckband, earbuds
    water_resistance: Union[float, str]  # score from 0 to 1 or IPX rating
    driver_size: Optional[Union[float, str]] = None  # driver size in mm
    name: Optional[str] = None  # headphone model name
    
    @field_validator('price', 'battery_life', 'latency', 'driver_size', mode='before')
    def convert_numeric(cls, v):
        if v == '' or v is None:
            return None
        if isinstance(v, str):
            return float(v) if v else None
        return v
    
    @field_validator('num_mics', mode='before')
    def convert_num_mics(cls, v):
        if v == '' or v is None:
            return 0
        if isinstance(v, str):
            return int(v) if v else 0
        return min(16, max(0, int(v)))
    
    @field_validator('anc_strength', mode='before')
    def convert_anc_strength(cls, v):
        if isinstance(v, str):
            mapping = {'None': 0.0, 'Weak': 0.25, 'Medium': 0.5, 'Strong': 0.75, 'Very Strong': 1.0}
            return mapping.get(v, 0.5)
        return v
    
    @field_validator('comfort_score', mode='before')
    def convert_comfort_score(cls, v):
        if isinstance(v, str):
            mapping = {'Poor': 0.2, 'Fair': 0.4, 'Good': 0.6, 'Very Good': 0.8, 'Excellent': 1.0}
            return mapping.get(v, 0.6)
        return v
    
    @field_validator('water_resistance', mode='before')
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

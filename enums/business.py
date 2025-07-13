from enum import Enum

class BusinessType(str, Enum):
    SERVICE = "service"
    PRODUCT = "product"
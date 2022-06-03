'''
structs for msgspec
'''
from typing import Dict, List, Optional

from msgspec import Struct


class Query(Struct):
    """
    Struct for Query
    """
    date: str
    depAirport: str
    arrAirport: str


class Request(Struct):
    """
    Struct for Request
    """
    supplier: str
    tripType: str
    fareClass: str
    adultAmount: int
    childAmount: int
    infantAmount: int
    queries: List[Query]
    timestamp: int


class Segment(Struct):
    """
    Struct for Segment
    """
    fareClass: str
    depDate: str
    depTime: str
    flightNo: str
    carrier: str
    orgAirport: str
    arriveDate: str
    arriveTime: str
    dstAirport: str


class Flight(Struct):
    """
    Struct for Flight
    """
    segments: List[Segment]


class Price(Struct):
    """
    Struct for Price
    """
    price: float
    tax: float
    totalPrice: float
    seatsStatus: Optional[str] = None
    currencyCode: Optional[str] = None


class Trip(Struct):
    """
    Struct for Trip
    """
    flights: List[Flight]
    extended = Dict[str, str]
    prices: Optional[Dict[str, Price]] = None


class PreparedData(Struct):
    """
    Struct of PreparedData
    """
    request_rt: Request
    trip_rt: Trip
    request_ow_dep: Request
    prices_ow_dep: Dict[str, Price]
    request_ow_ret: Request
    prices_ow_ret: Dict[str, Price]
    key: Optional[str] = None


class Result(Struct):
    """
    Struct of Result
    """
    trips: List[Trip]


class CacheInfo(Struct):
    """
    Struct of CacheInfo
    """
    request: Request
    result: Result

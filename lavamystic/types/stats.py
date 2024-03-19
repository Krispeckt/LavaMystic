from typing import TypedDict


class MemoryStats(TypedDict):
    free: int
    used: int
    allocated: int
    reservable: int


class CPUStats(TypedDict):
    cores: int
    systemLoad: float
    lavalinkLoad: float


class FrameStats(TypedDict):
    sent: int
    nulled: int
    deficit: int

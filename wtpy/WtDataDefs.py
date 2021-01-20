import numpy as np
from pandas import DataFrame

class WtKlineData:
    def __init__(self, size:int, bAlloc:bool = True):
        self.size:int = size
        self.count:int = 0

        if bAlloc:
            self.bartimes = np.zeros(self.size, np.int64)
            self.opens = np.zeros(self.size)
            self.highs = np.zeros(self.size)
            self.lows = np.zeros(self.size)
            self.closes = np.zeros(self.size)
            self.volumns = np.zeros(self.size)
        else:
            self.bartimes = None
            self.opens = None
            self.highs = None
            self.lows = None
            self.closes = None
            self.volumns = None

    def append_bar(self, newBar:dict):

        pos = self.count
        if pos == self.size:
            self.bartimes[:-1] = self.bartimes[1:]
            self.opens[:-1] = self.opens[1:]
            self.highs[:-1] = self.highs[1:]
            self.lows[:-1] = self.lows[1:]
            self.closes[:-1] = self.closes[1:]
            self.volumns[:-1] = self.volumns[1:]

            pos = -1
        else:
            self.count += 1
        self.bartimes[pos] = newBar["bartime"]
        self.opens[pos] = newBar["open"]
        self.highs[pos] = newBar["high"]
        self.lows[pos] = newBar["low"]
        self.closes[pos] = newBar["close"]
        self.volumns[pos] = newBar["volumn"]

    def is_empty(self) -> bool:
        return self.count==0

    def clear(self):
        self.count = 0

        self.bartimes:np.ndarray = np.zeros(self.size, np.int64)
        self.opens:np.ndarray = np.zeros(self.size)
        self.highs:np.ndarray = np.zeros(self.size)
        self.lows:np.ndarray = np.zeros(self.size)
        self.closes:np.ndarray = np.zeros(self.size)
        self.volumns:np.ndarray = np.zeros(self.size)

    def get_bar(self, iLoc:int = -1) -> dict:
        if self.is_empty():
            return None

        lastBar = dict()
        lastBar["bartime"] = self.bartimes[iLoc]
        lastBar["open"] = self.opens[iLoc]
        lastBar["high"] = self.highs[iLoc]
        lastBar["low"] = self.lows[iLoc]
        lastBar["close"] = self.closes[iLoc]
        lastBar["volumn"] = self.volumns[iLoc]

        return lastBar

    def slice(self, iStart:int = 0, iEnd:int = -1, bCopy:bool = False):
        if self.is_empty():
            return None

        bartimes = self.bartimes[iStart:iEnd]
        cnt = len(bartimes)
        ret = WtKlineData(cnt, False)
        ret.count = cnt

        if bCopy:
            ret.bartimes = bartimes.copy()
            ret.opens = self.opens[iStart:iEnd].copy()
            ret.highs = self.highs[iStart:iEnd].copy()
            ret.lows = self.lows[iStart:iEnd].copy()
            ret.closes = self.closes[iStart:iEnd].copy()
            ret.volumns = self.volumns[iStart:iEnd].copy()
        else:
            ret.bartimes = bartimes
            ret.opens = self.opens[iStart:iEnd]
            ret.highs = self.highs[iStart:iEnd]
            ret.lows = self.lows[iStart:iEnd]
            ret.closes = self.closes[iStart:iEnd]
            ret.volumns = self.volumns[iStart:iEnd]

        return ret

    def to_df(self) -> DataFrame:
        ret = DataFrame({
            "bartime":self.bartimes,
            "open":self.opens,
            "high":self.highs,
            "low":self.lows,
            "close":self.closes,
            "volumn":self.volumns
        })
        ret.set_index(self.bartimes)
        return ret

class WtTickData:
    def __init__(self, capacity:int):
        self.capacity:int = capacity
        self.size:int = 0

        self.ticks = [None]*capacity

    def append_tick(self, newTick:dict):
        pos = self.size
        if pos == self.capacity:
            self.ticks[:-1] = self.ticks[1:]
            pos = -1
        else:
            self.size += 1

        self.ticks[pos] = newTick

    def is_empty(self) -> bool:
        return self.size==0

    def capacity(self) -> int:
        return self.capacity

    def size(self) -> int:
        return self.size

    def clear(self):
        self.size = 0
        self.ticks = []*self.capacity

    def get_tick(self, iLoc:int=-1) -> dict:
        if self.is_empty():
            return None

        return self.ticks[iLoc]

    def to_df(self) -> DataFrame:
        ret = DataFrame(self.ticks)
        return ret
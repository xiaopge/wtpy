from ctypes import cdll, c_int, c_char_p, c_longlong, c_bool, c_void_p, c_ulong, c_uint, c_uint64, c_double, POINTER
from wtpy.WtCoreDefs import CB_STRATEGY_INIT, CB_STRATEGY_TICK, CB_STRATEGY_CALC, CB_STRATEGY_BAR, CB_STRATEGY_GET_BAR, CB_STRATEGY_GET_TICK, CB_STRATEGY_GET_POSITION
from wtpy.WtCoreDefs import CB_HFTSTRA_CHNL_EVT, CB_HFTSTRA_ENTRUST, CB_HFTSTRA_ORD, CB_HFTSTRA_TRD
from wtpy.WtCoreDefs import CB_HFTSTRA_ORDQUE, CB_HFTSTRA_ORDDTL, CB_HFTSTRA_TRANS, CB_HFTSTRA_GET_ORDQUE, CB_HFTSTRA_GET_ORDDTL, CB_HFTSTRA_GET_TRANS
from wtpy.WtCoreDefs import CHNL_EVENT_READY, CHNL_EVENT_LOST
from wtpy.WtCoreDefs import WTSTickStruct,WTSBarStruct,WTSOrdQueStruct,WTSOrdDtlStruct,WTSTransStruct
import platform
import os
import sys

theEngine = None

def isPythonX64():
    ret = platform.architecture()
    return (ret[0] == "64bit")

def isWindows():
    if "windows" in platform.system().lower():
        return True

    return False

#回调函数
def on_strategy_init(id):
    engine = theEngine
    ctx = engine.get_context()
    if ctx is not None:
        ctx.on_init()
    return

def on_strategy_tick(id, code, newTick:POINTER(WTSTickStruct)):
    code = bytes.decode(code)
    engine = theEngine
    ctx = engine.get_context()

    realTick = newTick.contents
    tick = dict()
    tick["time"] = realTick.action_date * 1000000000 + realTick.action_time
    tick["open"] = realTick.open
    tick["high"] = realTick.high
    tick["low"] = realTick.low
    tick["price"] = realTick.price
    
    tick["bidprice"] = list()
    tick["bidqty"] = list()
    tick["askprice"] = list()
    tick["askqty"] = list()
    
    tick["total_volume"] = realTick.total_volume
    tick["volume"] = realTick.volume
    tick["total_turnover"] = realTick.total_turnover
    tick["turn_over"] = realTick.turn_over
    tick["open_interest"] = realTick.open_interest
    tick["diff_interest"] = realTick.diff_interest

    for i in range(10):
        if realTick.bid_qty[i] != 0:
            tick["bidprice"].append(realTick.bid_prices[i])
            tick["bidqty"].append(realTick.bid_qty[i])

        if realTick.ask_qty[i] != 0:
            tick["askprice"].append(realTick.ask_prices[i])
            tick["askqty"].append(realTick.ask_qty[i])

    if ctx is not None:
        ctx.on_tick(code, tick)
    return

def on_strategy_calc(id):
    engine = theEngine
    ctx = engine.get_context()
    if ctx is not None:
        ctx.on_calculate()
    return

def on_strategy_bar(id, code, period, newBar:POINTER(WTSBarStruct)):
    period = bytes.decode(period)
    engine = theEngine
    ctx = engine.get_context()
    newBar = newBar.contents
    curBar = dict()
    if period[0] == 'd':
        curBar["time"] = newBar.date
    else:
        curBar["time"] = 1990*100000000 + newBar.time
    curBar["bartime"] = curBar["time"]
    curBar["open"] = newBar.open
    curBar["high"] = newBar.high
    curBar["low"] = newBar.low
    curBar["close"] = newBar.close
    curBar["volume"] = newBar.vol
    if ctx is not None:
        ctx.on_bar(bytes.decode(code), period, curBar)
    return


def on_strategy_get_bar(id, code, period, curBar, isLast):
    '''
    获取K线回调，该回调函数因为是python主动发起的，需要同步执行，所以不走事件推送\n
    @id     策略id\n
    @code   合约代码\n
    @period K线周期\n
    @curBar 最新一条K线\n
    @isLast 是否是最后一条
    '''
    engine = theEngine
    ctx = engine.get_context()
    realBar = None
    if curBar:
        realBar = curBar.contents

    period = bytes.decode(period)

    bar = None
    if realBar is not None:
        bar = dict()
        if period[0] == 'd':
            bar["time"] = realBar.date
        else:
            bar["time"] = 1990*100000000 + realBar.time
        bar["bartime"] = bar["time"]
        bar["open"] = realBar.open
        bar["high"] = realBar.high
        bar["low"] = realBar.low
        bar["close"] = realBar.close
        bar["volume"] = realBar.vol

    if ctx is not None:
        ctx.on_getbars(bytes.decode(code), period, bar, isLast)
    return

def on_strategy_get_tick(id, code:str, curTick:POINTER(WTSTickStruct), isLast:bool):
    '''
    获取Tick回调，该回调函数因为是python主动发起的，需要同步执行，所以不走事件推送\n
    @id         策略id\n
    @code       合约代码\n
    @curTick    最新一笔Tick\n
    @isLast     是否是最后一条
    '''

    engine = theEngine
    ctx = engine.get_context()
    realTick = None
    if curTick:
        realTick = curTick.contents

    tick = None
    if realTick is not None:
        tick = dict()
        tick["time"] = realTick.action_date * 1000000000 + realTick.action_time
        tick["open"] = realTick.open
        tick["high"] = realTick.high
        tick["low"] = realTick.low
        tick["price"] = realTick.price

        tick["bidprice"] = list()
        tick["bidqty"] = list()
        tick["askprice"] = list()
        tick["askqty"] = list()
        
        tick["total_volume"] = realTick.total_volume
        tick["volume"] = realTick.volume
        tick["total_turnover"] = realTick.total_turnover
        tick["turn_over"] = realTick.turn_over
        tick["open_interest"] = realTick.open_interest
        tick["diff_interest"] = realTick.diff_interest

        for i in range(10):
            if realTick.bid_qty[i] != 0:
                tick["bidprice"].append(realTick.bid_prices[i])
                tick["bidqty"].append(realTick.bid_qty[i])

            if realTick.ask_qty[i] != 0:
                tick["askprice"].append(realTick.ask_prices[i])
                tick["askqty"].append(realTick.ask_qty[i])

    if ctx is not None:
        ctx.on_getticks(bytes.decode(code), tick, isLast)
    return

def on_stra_get_position(id, stdCode, qty, isLast):
    engine = theEngine
    ctx = engine.get_context()
    if ctx is not None:
        ctx.on_getpositions(bytes.decode(stdCode), qty, isLast)

def on_hftstra_channel_evt(id, trader, evtid):
    engine = theEngine
    ctx = engine.get_context()
    
    if evtid == CHNL_EVENT_READY:
        ctx.on_channel_ready()
    elif evtid == CHNL_EVENT_LOST:
        ctx.on_channel_lost()

def on_hftstra_order(id, localid, stdCode, isBuy, totalQty, leftQty, price, isCanceled, userTag):
    stdCode = bytes.decode(stdCode)
    userTag = bytes.decode(userTag)
    engine = theEngine
    ctx = engine.get_context()
    ctx.on_order(localid, stdCode, isBuy, totalQty, leftQty, price, isCanceled, userTag)

def on_hftstra_trade(id, localid, stdCode, isBuy, qty, price, userTag):
    stdCode = bytes.decode(stdCode)
    userTag = bytes.decode(userTag)
    engine = theEngine
    ctx = engine.get_context()
    ctx.on_trade(localid, stdCode, isBuy, qty, price, userTag)

def on_hftstra_entrust(id, localid, stdCode, bSucc, message, userTag):
    stdCode = bytes.decode(stdCode)
    message = bytes.decode(message, "gbk")
    userTag = bytes.decode(userTag)
    engine = theEngine
    ctx = engine.get_context()
    ctx.on_entrust(localid, stdCode, bSucc, message, userTag)

def on_hftstra_order_queue(id, stdCode:str, newOrdQue:POINTER(WTSOrdQueStruct)):
    stdCode = bytes.decode(stdCode)
    engine = theEngine
    ctx = engine.get_context()
    newOrdQue = newOrdQue.contents
    curOrdQue = dict()
    curOrdQue["time"] = newOrdQue.action_date * 1000000000 + newOrdQue.action_time
    curOrdQue["side"] = newOrdQue.side
    curOrdQue["price"] = newOrdQue.price
    curOrdQue["order_items"] = newOrdQue.order_items
    curOrdQue["qsize"] = newOrdQue.qsize
    curOrdQue["volumes"] = list()

    for i in range(50):
        if newOrdQue.volumes[i] == 0:
            break
        else:
            curOrdQue["volumes"].append(newOrdQue.volumes[i])
    
    if ctx is not None:
        ctx.on_order_queue(stdCode, curOrdQue)
    return

def on_hftstra_get_order_queue(id, stdCode:str, newOrdQue:POINTER(WTSOrdQueStruct), isLast:bool):
    engine = theEngine
    ctx = engine.get_context()
    realOrdQue = None
    if newOrdQue:
        realOrdQue = newOrdQue.contents
    
    if realOrdQue is not None:
        curOrdQue = dict()
        curOrdQue["time"] = realOrdQue.action_date * 1000000000 + realOrdQue.action_time
        curOrdQue["side"] = realOrdQue.side
        curOrdQue["price"] = realOrdQue.price
        curOrdQue["order_items"] = realOrdQue.order_items
        curOrdQue["qsize"] = realOrdQue.qsize
        curOrdQue["volumes"] = list()

        for i in range(50):
            if realOrdQue.volumes[i] == 0:
                break
            else:
                curOrdQue["volumes"].append(realOrdQue.volumes[i])
        
        if ctx is not None:
            ctx.on_get_order_queue(bytes.decode(stdCode), curOrdQue, isLast)

def on_hftstra_order_detail(id, stdCode:str, newOrdDtl:POINTER(WTSOrdDtlStruct)):
    engine = theEngine
    ctx = engine.get_context()
    newOrdDtl = newOrdDtl.contents

    curOrdDtl = dict()
    curOrdDtl["time"] = newOrdDtl.action_date * 1000000000 + newOrdDtl.action_time
    curOrdDtl["index"] = newOrdDtl.index
    curOrdDtl["side"] = newOrdDtl.side
    curOrdDtl["price"] = newOrdDtl.price
    curOrdDtl["volume"] = newOrdDtl.volume
    curOrdDtl["otype"] = newOrdDtl.otype
    
    if ctx is not None:
        ctx.on_order_detail(stdCode, curOrdDtl)

def on_hftstra_get_order_detail(id, stdCode:str, newOrdDtl:POINTER(WTSOrdDtlStruct), isLast:bool):
    engine = theEngine
    ctx = engine.get_context()
    realOrdDtl = None
    if newOrdDtl:
        realOrdDtl = newOrdDtl.contents
    
    if realOrdDtl is not None:
        curOrdDtl = dict()
        curOrdDtl["time"] = realOrdDtl.action_date * 1000000000 + realOrdDtl.action_time
        curOrdDtl["index"] = realOrdDtl.index
        curOrdDtl["side"] = realOrdDtl.side
        curOrdDtl["price"] = realOrdDtl.price
        curOrdDtl["volume"] = realOrdDtl.volume
        curOrdDtl["otype"] = realOrdDtl.otype
        
        if ctx is not None:
            ctx.on_get_order_detail(bytes.decode(stdCode), curOrdDtl, isLast)

def on_hftstra_transaction(id, stdCode, newTrans:POINTER(WTSTransStruct)):
    engine = theEngine
    ctx = engine.get_context()
    newTrans = newTrans.contents

    curTrans = dict()
    curTrans["time"] = newTrans.action_date * 1000000000 + newTrans.action_time
    curTrans["index"] = newTrans.index
    curTrans["ttype"] = newTrans.ttype
    curTrans["side"] = newTrans.side
    curTrans["price"] = newTrans.price
    curTrans["volume"] = newTrans.volume
    curTrans["askorder"] = newTrans.askorder
    curTrans["bidorder"] = newTrans.bidorder
    
    if ctx is not None:
        ctx.on_transaction(stdCode, curTrans)
    
def on_hftstra_get_transaction(id, stdCode:str, newTrans:POINTER(WTSTransStruct), isLast:bool):
    engine = theEngine
    ctx = engine.get_context()
    realTrans = None
    if newTrans:
        realTrans = newTrans.contents
    
    if realTrans is not None:
        curTrans = dict()
        curTrans["time"] = realTrans.action_date * 1000000000 + realTrans.action_time
        curTrans["index"] = realTrans.index
        curTrans["ttype"] = realTrans.ttype
        curTrans["side"] = realTrans.side
        curTrans["price"] = realTrans.price
        curTrans["volume"] = realTrans.volume
        curTrans["askorder"] = realTrans.askorder
        curTrans["bidorder"] = realTrans.bidorder
        
        if ctx is not None:
            ctx.on_get_transaction(bytes.decode(stdCode), curTrans, isLast)

'''
将回调函数转换成C接口识别的函数类型
''' 
cb_strategy_init = CB_STRATEGY_INIT(on_strategy_init)
cb_strategy_tick = CB_STRATEGY_TICK(on_strategy_tick)
cb_strategy_calc = CB_STRATEGY_CALC(on_strategy_calc)
cb_strategy_bar = CB_STRATEGY_BAR(on_strategy_bar)
cb_strategy_get_bar = CB_STRATEGY_GET_BAR(on_strategy_get_bar)
cb_strategy_get_tick = CB_STRATEGY_GET_TICK(on_strategy_get_tick)
cb_stra_get_position = CB_STRATEGY_GET_POSITION(on_stra_get_position)

cb_hftstra_ordque = CB_HFTSTRA_ORDQUE(on_hftstra_order_queue)
cb_hftstra_get_ordque = CB_HFTSTRA_GET_ORDQUE(on_hftstra_order_queue)
cb_hftstra_orddtl = CB_HFTSTRA_ORDDTL(on_hftstra_order_detail)
cb_hftstra_get_orddtl = CB_HFTSTRA_GET_ORDDTL(on_hftstra_order_queue)
cb_hftstra_trans = CB_HFTSTRA_TRANS(on_hftstra_transaction)
cb_hftstra_get_trans = CB_HFTSTRA_GET_TRANS(on_hftstra_order_queue)

cb_hftstra_chnl_evt = CB_HFTSTRA_CHNL_EVT(on_hftstra_channel_evt)
cb_hftstra_order = CB_HFTSTRA_ORD(on_hftstra_order)
cb_hftstra_trade = CB_HFTSTRA_TRD(on_hftstra_trade)
cb_hftstra_entrust = CB_HFTSTRA_ENTRUST(on_hftstra_entrust)

# Python对接C接口的库
class WtBtWrapper:
    '''
    Wt平台C接口底层对接模块
    '''

    # api可以作为公共变量
    api = None
    ver = "Unknown"
    
    # 构造函数，传入动态库名
    def __init__(self):
        paths = os.path.split(__file__)
        if isWindows(): #windows平台
            if isPythonX64():
                dllname = "x64/WtBtPorter.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
            else:
                dllname = "x86/WtBtPorter.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
        else:#Linux平台
            dllname = "linux/libWtBtPorter.so"
            a = (paths[:-1] + (dllname,))
            _path = os.path.join(*a)
            print(_path)
            self.api = cdll.LoadLibrary(_path)
            print(self.api)
        self.api.get_version.restype = c_char_p
        self.api.cta_get_last_entertime.restype = c_uint64
        self.api.cta_get_first_entertime.restype = c_uint64
        self.api.cta_get_detail_entertime.restype = c_uint64
        self.api.cta_enter_long.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_enter_short.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_exit_long.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_exit_short.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_set_position.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.ver = bytes.decode(self.api.get_version())

        self.api.cta_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.cta_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.cta_load_userdata.restype = c_char_p

        self.api.cta_get_position.restype = c_double
        self.api.cta_get_position_profit.restype = c_double
        self.api.cta_get_position_avgpx.restype = c_double
        self.api.cta_get_detail_cost.restype = c_double
        self.api.cta_get_detail_profit.restype = c_double

        self.api.sel_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.sel_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.sel_load_userdata.restype = c_char_p
        self.api.sel_get_position.restype = c_double
        self.api.sel_set_position.argtypes = [c_ulong, c_char_p, c_double, c_char_p]

        self.api.hft_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.hft_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.hft_load_userdata.restype = c_char_p
        self.api.hft_get_position.restype = c_double
        self.api.hft_get_position_profit.restype = c_double
        self.api.hft_get_undone.restype = c_double
        
        self.api.hft_buy.argtypes = [c_ulong, c_char_p, c_double, c_double, c_char_p]
        self.api.hft_buy.restype = c_char_p
        self.api.hft_sell.argtypes = [c_ulong, c_char_p, c_double, c_double, c_char_p]
        self.api.hft_sell.restype = c_char_p

    def run_backtest(self):
        self.api.run_backtest()

    def release_backtest(self):
        self.api.release_backtest()

    def write_log(self, level, message:str, catName:str = ""):
        self.api.write_log(level, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'), bytes(catName, encoding = "utf8"))

    def config_backtest(self, cfgfile:str = 'config.json', isFile:bool = True):
        self.api.config_backtest(bytes(cfgfile, encoding = "utf8"), isFile)

    def initialize_cta(self, engine, logCfg:str = "logcfgbt.json", isFile:bool = True):
        '''
        C接口初始化
        '''
        global theEngine
        theEngine = engine
        try:
            self.api.register_cta_callbacks(cb_strategy_init, cb_strategy_tick, cb_strategy_calc, cb_strategy_bar)
            self.api.init_backtest(bytes(logCfg, encoding = "utf8"), isFile)
        except OSError as oe:
            print(oe)

        self.write_log(102, "Wt回测框架已初始化完成，框架版本号：%s" % (self.ver))

    def initialize_hft(self, engine, logCfg:str = "logcfgbt.json", isFile:bool = True):
        '''
        C接口初始化
        '''
        global theEngine
        theEngine = engine
        try:
            self.api.register_hft_callbacks(cb_strategy_init, cb_strategy_tick, cb_strategy_bar, 
                cb_hftstra_chnl_evt, cb_hftstra_order, cb_hftstra_trade, cb_hftstra_entrust,
                cb_hftstra_orddtl, cb_hftstra_ordque, cb_hftstra_trans)
            self.api.init_backtest(bytes(logCfg, encoding = "utf8"), isFile)
        except OSError as oe:
            print(oe)

        self.write_log(102, "Wt回测框架已初始化完成，框架版本号：%s" % (self.ver))

    def initialize_sel(self, engine, logCfg:str = "logcfgbt.json", isFile:bool = True):
        '''
        C接口初始化
        '''
        global theEngine
        theEngine = engine
        try:
            self.api.register_sel_callbacks(cb_strategy_init, cb_strategy_tick, cb_strategy_calc, cb_strategy_bar)
            self.api.init_backtest(bytes(logCfg, encoding = "utf8"), isFile)
        except OSError as oe:
            print(oe)

        self.write_log(102, "Wt回测框架已初始化完成，框架版本号：%s" % (self.ver))

    def dump_kline(self, stdCode:str, period:str, filename:str):
        self.api.dump_bars(bytes(stdCode, encoding = "utf8"), bytes(period, encoding = "utf8"), bytes(filename, encoding = "utf8"))
        
    def init_cta_mocker(self, name:str):
        '''
        创建策略环境\n
        @name      策略名称
        @return    系统内策略ID 
        '''
        return self.api.init_cta_mocker(bytes(name, encoding = "utf8") )

    def init_hft_mocker(self, name:str):
        '''
        创建策略环境\n
        @name      策略名称
        @return    系统内策略ID 
        '''
        return self.api.init_hft_mocker(bytes(name, encoding = "utf8") )

    def init_sel_mocker(self, name:str, date:int, time:int, period:str, trdtpl:str = "CHINA", session:str = "TRADING"):
        '''
        创建策略环境\n
        @name      策略名称
        @return    系统内策略ID 
        '''
        return self.api.init_sel_mocker(bytes(name, encoding = "utf8"), date, time, 
            bytes(period, encoding = "utf8"), bytes(trdtpl, encoding = "utf8"), bytes(session, encoding = "utf8"))

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''CTA接口'''
    def cta_enter_long(self, id:int, code:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        开多\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_enter_long(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_exit_long(self, id:int, code:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        平多\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_exit_long(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_enter_short(self, id:int, code:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        开空\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_enter_short(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_exit_short(self, id:int, code:str, qty:float, usertag:str, limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        平空\n
        @id     策略id\n
        @code   合约代码\n
        @qty    手数，大于等于0\n
        '''
        self.api.cta_exit_short(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_get_bars(self, id:int, code:str, period:str, count:int, isMain:bool):
        '''
        读取K线\n
        @id     策略id\n
        @code   合约代码\n
        @period 周期，如m1/m3/d1等\n
        @count  条数\n
        @isMain 是否主K线
        '''
        return self.api.cta_get_bars(id, bytes(code, encoding = "utf8"), bytes(period, encoding = "utf8"), count, isMain, cb_strategy_get_bar)

    def cta_get_ticks(self, id:int, code:str, count:int):
        '''
        读取Tick\n
        @id     策略id\n
        @code   合约代码\n
        @count  条数\n
        '''
        return self.api.cta_get_ticks(id, bytes(code, encoding = "utf8"), count, cb_strategy_get_tick)

    def cta_get_position_profit(self, id:int, code:str):
        '''
        获取浮动盈亏\n
        @id     策略id\n
        @code   合约代码\n
        @return 指定合约的浮动盈亏
        '''
        return self.api.cta_get_position_profit(id, bytes(code, encoding = "utf8"))

    def cta_get_position_avgpx(self, id:int, code:str):
        '''
        获取持仓均价\n
        @id     策略id\n
        @code   合约代码\n
        @return 指定合约的持仓均价
        '''
        return self.api.cta_get_position_avgpx(id, bytes(code, encoding = "utf8"))

    def cta_get_all_position(self, id:int):
        '''
        获取全部持仓\n
        @id     策略id
        '''
        return self.api.cta_get_all_position(id, cb_stra_get_position)
    
    def cta_get_position(self, id:int, code:str, usertag:str = ""):
        '''
        获取持仓\n
        @id     策略id\n
        @code   合约代码\n
        @usertag    进场标记，如果为空则获取该合约全部持仓\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.cta_get_position(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8"))

    def cta_get_price(self, code:str):
        '''
        @code   合约代码\n
        @return 指定合约的最新价格 
        '''
        return self.api.cta_get_price(bytes(code, encoding = "utf8"))

    def cta_set_position(self, id:int, code:str, qty:float, usertag:str = "", limitprice:float = 0.0, stopprice:float = 0.0):
        '''
        设置目标仓位\n
        @id     策略id
        @code   合约代码\n
        @qty    目标仓位，正为多，负为空
        '''
        self.api.cta_set_position(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"), limitprice, stopprice)

    def cta_get_date(self):
        '''
        获取当前日期\n
        @return    当前日期 
        '''
        return self.api.cta_get_date()

    def cta_get_time(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.cta_get_time()

    def cta_get_first_entertime(self, id:int, code:str):
        '''
        获取当前持仓的首次进场时间\n
        @code       合约代码\n
        @return     进场时间，格式如201907260932 
        '''
        return self.api.cta_get_first_entertime(id, bytes(code, encoding = "utf8"))

    def cta_get_last_entertime(self, id:int, code:str):
        '''
        获取当前持仓的最后进场时间\n
        @code       合约代码\n
        @return     进场时间，格式如201907260932 
        '''
        return self.api.cta_get_last_entertime(id, bytes(code, encoding = "utf8"))

    def cta_log_text(self, id:int, message:str):
        '''
        日志输出\n
        @id         策略ID\n
        @message    日志内容
        '''
        self.api.cta_log_text(id, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'))

    def cta_get_detail_entertime(self, id:int, code:str, usertag:str):
        '''
        获取指定标记的持仓的进场时间\n
        @id         策略id\n
        @code       合约代码\n
        @usertag    进场标记\n
        @return     进场时间，格式如201907260932 
        '''
        return self.api.cta_get_detail_entertime(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8")) 

    def cta_get_detail_cost(self, id:int, code:str, usertag:str):
        '''
        获取指定标记的持仓的开仓价\n
        @id         策略id\n
        @code       合约代码\n
        @usertag    进场标记\n
        @return     开仓价 
        '''
        return self.api.cta_get_detail_cost(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8")) 

    def cta_get_detail_profit(self, id:int, code:str, usertag:str, flag:int):
        '''
        获取指定标记的持仓的盈亏\n
        @id         策略id\n
        @code       合约代码\n
        @usertag    进场标记\n
        @flag       盈亏记号，0-浮动盈亏，1-最大浮盈，2-最大亏损（负数）
        @return     盈亏 
        '''
        return self.api.cta_get_detail_profit(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8"), flag) 

    def cta_save_user_data(self, id:int, key:str, val:str):
        '''
        保存用户数据\n
        @id         策略id\n
        @key        数据名
        @val        数据值
        '''
        self.api.cta_save_userdata(id, bytes(key, encoding = "utf8"), bytes(val, encoding = "utf8"))

    def cta_load_user_data(self, id:int, key:str, defVal:str  = ""):
        '''
        加载用户数据\n
        @id         策略id\n
        @key        数据名
        @defVal     默认值
        '''
        ret = self.api.cta_load_userdata(id, bytes(key, encoding = "utf8"), bytes(defVal, encoding = "utf8"))
        return bytes.decode(ret)

    def cta_sub_ticks(self, id:int, stdCode:str):
        '''
        订阅行情
        @id         策略id\n
        @stdCode    品种代码
        '''
        self.api.cta_sub_ticks(id, bytes(stdCode, encoding = "utf8"))
    
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''SEL接口'''
    def sel_get_bars(self, id:int, code:str, period:str, count:int):
        '''
        读取K线\n
        @id     策略id\n
        @code   合约代码\n
        @period 周期，如m1/m3/d1等\n
        @count  条数
        '''
        return self.api.sel_get_bars(id, bytes(code, encoding = "utf8"), bytes(period, encoding = "utf8"), count, cb_strategy_get_bar)

    def sel_get_ticks(self, id:int, code:str, count:int):
        '''
        读取Tick\n
        @id     策略id\n
        @code   合约代码\n
        @count  条数\n
        '''
        return self.api.sel_get_ticks(id, bytes(code, encoding = "utf8"), count, cb_strategy_get_tick)

    def sel_save_user_data(self, id:int, key:str, val:str):
        '''
        保存用户数据\n
        @id         策略id\n
        @key        数据名
        @val        数据值
        '''
        self.api.sel_save_userdata(id, bytes(key, encoding = "utf8"), bytes(val, encoding = "utf8"))

    def sel_load_user_data(self, id:int, key:str, defVal:str  = ""):
        '''
        加载用户数据\n
        @id         策略id\n
        @key        数据名
        @defVal     默认值
        '''
        ret = self.api.sel_load_userdata(id, bytes(key, encoding = "utf8"), bytes(defVal, encoding = "utf8"))
        return bytes.decode(ret)

    def sel_get_all_position(self, id:int):
        '''
        获取全部持仓\n
        @id     策略id
        '''
        return self.api.sel_get_all_position(id, cb_stra_get_position)

    def sel_get_position(self, id:int, code:str, usertag:str = ""):
        '''
        获取持仓\n
        @id     策略id\n
        @code   合约代码\n
        @usertag    进场标记，如果为空则获取该合约全部持仓\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.sel_get_position(id, bytes(code, encoding = "utf8"), bytes(usertag, encoding = "utf8"))

    def sel_get_price(self, code:str):
        '''
        @code   合约代码\n
        @return 指定合约的最新价格 
        '''
        return self.api.sel_get_price(bytes(code, encoding = "utf8"))

    def sel_set_position(self, id:int, code:str, qty:float, usertag:str = ""):
        '''
        设置目标仓位\n
        @id     策略id
        @code   合约代码\n
        @qty    目标仓位，正为多，负为空
        '''
        self.api.sel_set_position(id, bytes(code, encoding = "utf8"), qty, bytes(usertag, encoding = "utf8"))

    def sel_get_date(self):
        '''
        获取当前日期\n
        @return    当前日期 
        '''
        return self.api.sel_get_date()

    def sel_get_time(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.sel_get_time()

    def sel_log_text(self, id:int, message:str):
        '''
        日志输出\n
        @id         策略ID\n
        @message    日志内容
        '''
        self.api.sel_log_text(id, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'))

    def sel_sub_ticks(self, id:int, stdCode:str):
        '''
        订阅行情
        @id         策略id\n
        @stdCode    品种代码
        '''
        self.api.sel_sub_ticks(id, bytes(stdCode, encoding = "utf8"))

    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''HFT接口'''
    def hft_get_bars(self, id:int, code:str, period:str, count:int):
        '''
        读取K线\n
        @id     策略id\n
        @code   合约代码\n
        @period 周期，如m1/m3/d1等\n
        @count  条数
        '''
        return self.api.hft_get_bars(id, bytes(code, encoding = "utf8"), bytes(period, encoding = "utf8"), count, cb_strategy_get_bar)

    def hft_get_ticks(self, id:int, code:str, count:int):
        '''
        读取Tick\n
        @id     策略id\n
        @code   合约代码\n
        @count  条数\n
        '''
        return self.api.hft_get_ticks(id, bytes(code, encoding = "utf8"), count, cb_strategy_get_tick)

    def hft_get_ordque(self, id:int, code:str, count:int):
        '''
        读取委托队列\n
        @id     策略id\n
        @code   合约代码\n
        @count  条数\n
        '''
        return self.api.hft_get_ordque(id, bytes(code, encoding = "utf8"), count, cb_hftstra_get_ordque)

    def hft_get_orddtl(self, id:int, code:str, count:int):
        '''
        读取逐笔委托\n
        @id     策略id\n
        @code   合约代码\n
        @count  条数\n
        '''
        return self.api.hft_get_orddtl(id, bytes(code, encoding = "utf8"), count, cb_hftstra_get_orddtl)

    def hft_get_trans(self, id:int, code:str, count:int):
        '''
        读取逐笔成交\n
        @id     策略id\n
        @code   合约代码\n
        @count  条数\n
        '''
        return self.api.hft_get_trans(id, bytes(code, encoding = "utf8"), count, cb_hftstra_get_trans)

    def hft_save_user_data(self, id:int, key:str, val:str):
        '''
        保存用户数据\n
        @id         策略id\n
        @key        数据名
        @val        数据值
        '''
        self.api.hft_save_userdata(id, bytes(key, encoding = "utf8"), bytes(val, encoding = "utf8"))

    def hft_load_user_data(self, id:int, key:str, defVal:str  = ""):
        '''
        加载用户数据\n
        @id         策略id\n
        @key        数据名
        @defVal     默认值
        '''
        ret = self.api.hft_load_userdata(id, bytes(key, encoding = "utf8"), bytes(defVal, encoding = "utf8"))
        return bytes.decode(ret)

    def hft_get_position(self, id:int, code:str):
        '''
        获取持仓\n
        @id     策略id\n
        @code   合约代码\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.hft_get_position(id, bytes(code, encoding = "utf8"))

    def hft_get_position_profit(self, id:int, stdCode:str):
        '''
        获取持仓盈亏\n
        @id     策略id\n
        @stdCode   合约代码\n
        @return 指定持仓的浮动盈亏
        '''
        return self.api.hft_get_position_profit(id, bytes(stdCode, encoding = "utf8"))

    def hft_get_undone(self, id:int, code:str):
        '''
        获取持仓\n
        @id     策略id\n
        @code   合约代码\n
        @return 指定合约的持仓手数，正为多，负为空
        '''
        return self.api.hft_get_undone(id, bytes(code, encoding = "utf8"))

    def hft_get_price(self, code:str):
        '''
        @code   合约代码\n
        @return 指定合约的最新价格 
        '''
        return self.api.hft_get_price(bytes(code, encoding = "utf8"))

    def hft_get_date(self):
        '''
        获取当前日期\n
        @return    当前日期 
        '''
        return self.api.hft_get_date()

    def hft_get_time(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.hft_get_time()

    def hft_get_secs(self):
        '''
        获取当前时间\n
        @return    当前时间 
        '''
        return self.api.hft_get_secs()

    def hft_log_text(self, id:int, message:str):
        '''
        日志输出\n
        @id         策略ID\n
        @message    日志内容
        '''
        self.api.hft_log_text(id, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'))

    def hft_sub_ticks(self, id:int, stdCode:str):
        '''
        订阅实时行情数据\n
        @id         策略ID\n
        @stdCode    品种代码
        '''
        self.api.hft_sub_ticks(id, bytes(stdCode, encoding = "utf8"))

    def hft_sub_order_queue(self, id:int, stdCode:str):
        '''
        订阅实时委托队列数据\n
        @id         策略ID\n
        @stdCode    品种代码
        '''
        self.api.hft_sub_order_queue(id, bytes(stdCode, encoding = "utf8"))

    def hft_sub_order_detail(self, id:int, stdCode:str):
        '''
        订阅逐笔委托数据\n
        @id         策略ID\n
        @stdCode    品种代码
        '''
        self.api.hft_sub_order_detail(id, bytes(stdCode, encoding = "utf8"))

    def hft_sub_transaction(self, id:int, stdCode:str):
        '''
        订阅逐笔成交数据\n
        @id         策略ID\n
        @stdCode    品种代码
        '''
        self.api.hft_sub_transaction(id, bytes(stdCode, encoding = "utf8"))

    def hft_cancel(self, id:int, localid:int):
        '''
        撤销指定订单\n
        @id         策略ID\n
        @localid    下单时返回的本地订单号
        '''
        return self.api.hft_cancel(id, localid)

    def hft_cancel_all(self, id:int, stdCode:str, isBuy:bool):
        '''
        撤销指定品种的全部买入订单or卖出订单\n
        @id         策略ID\n
        @stdCode    品种代码\n
        @isBuy      买入or卖出
        '''
        return self.api.hft_cancel_all(id, bytes(stdCode, encoding = "utf8"), isBuy)

    def hft_buy(self, id:int, stdCode:str, price:float, qty:float, userTag:str):
        '''
        买入指令\n
        @id         策略ID\n
        @stdCode    品种代码\n
        @price      买入价格, 0为市价\n
        @qty        买入数量
        '''
        idstr = self.api.hft_buy(id, bytes(stdCode, encoding = "utf8"), price, qty, bytes(userTag, encoding = "utf8"))
        return bytes.decode(idstr)

    def hft_sell(self, id:int, stdCode:str, price:float, qty:float, userTag:str):
        '''
        卖出指令\n
        @id         策略ID\n
        @stdCode    品种代码\n
        @price      卖出价格, 0为市价\n
        @qty        卖出数量
        '''
        idstr = self.api.hft_sell(id, bytes(stdCode, encoding = "utf8"), price, qty, bytes(userTag, encoding = "utf8"))
        return bytes.decode(idstr)
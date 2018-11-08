Python SDK
====

### 策略编写及接口

- python 策略提供有`gmsdk.Startegy`作为策略基类；
  策略为面向对象的程序结构，其中基类`Strategy`提供了基本的接口方法和数据定义，用户策略可以直接通过继承基类来实现自己需要的方法，在形如`on_XXX`以*`on_`*开头的事件处理函数中实现自己的业务逻辑，比如在`on_bar`中处理收到的K线数据，在`on_exec_rpt`中处理成交回报等。

  启动策略：在初始化动作，比如订阅行情完成后，调用`run()`方法启动。

  如果是用线程或进程方式启动策略，还可以通过策略实例对象调用`stop()`方法来停止相应的策略。

  **注意：**目前不提供历史数据的查询，策略如有需要，可在初始化时通过其他方式准备，例如读取本地文件或数据库。

- **数据定义**：
    - **编码规则**：
      交易所代码 +  分隔符`“.“` + 合约或证券的交易所本地代码， 例如： `SHFE.rb1901`表示上期所的螺纹19年1月份合约。

    - **行情数据**
        - `Tick`
          Tick数据跟交易所的原始快照数据对应，简单概述一下，字段名用小写英文缩写，词之间用下划线连接，基本上可以直接望文生义，除了代码为字串类型，时间相关的为日期时间类型，其他数据都是`double`类型，相应业务字段如下：

        ```
            exchange                # 交易所代码，字串
            sec_id                  # 合约代码， 字串
            update_time             # 更新时间， datetime
            last_price              # 最新成交价，double
            last_volume             # 上次成交量，上一次行情快照到这次行情快照间隔之间的累计成交量
            last_amount             # 上次成交额，上一次行情快照到这次行情快照间隔之间的累计成交额
            pre_settlement_price    # 上次结算价, double
            pre_close               # 昨收盘, double 
            upper_limit             # 涨停板价, double
            lower_limit             # 跌停板价, double
            pre_open_interest       # 昨持仓量 double
            open_interest           # 持仓量 double 
            volume                  # 当天累计成交量 double
            amount                  # 当天累计成交金额 double
            pre_delta               # 前日虚实度 double, 期权合约
            cur_delta;              # 今虚实度  double, 期权合约
            
            ## 以下为一到五档的行情申买申卖价和量，只列了一档和五档
            bid_p1                  # 申买价一 double 
            bid_v1                  # 申买量一 double
            ask_p1                  # 申卖价一 double 
            ask_v1                  # 申卖量一 double
            
            ...
        
            bid_p5                  # 申买价五 double 
            bid_v5                  # 申买量五 double
            ask_p5                  # 申卖价五 double 
            ask_v5                  # 申卖量五 double
        ```

        - `Bar`（分时K线）

          分时K线数据，提供高开低收量额几个主要业务数据，支持任意秒为单位的K线，通过订阅Bar的函数`subscribe`向系统订阅后就可以在`on_bar`中收到。
        ```
            exchange                # 交易所代码，字串
            sec_id                  # 合约代码， 字串
            freq_seconds            # k线频率，只支持整数，单位是秒
            open                    # 开盘价
            high                    # 最高价
            low                     # 最低价
            close                   # 收盘价
            volume                  # 成交量，该时间段内累计
            amount                  # 成交额，该时间段内累计
        
            start_time              # K线开始时间
            end_time                # K线结束时间
        ```

- **主要接口：**
    - **行情接口**
        - 订阅行情 `subscribe`
          订阅实时的Tick快照数据和分时K线数据，其中，代码部分为集合类型，订阅Tick只有代码参数和是否重新订阅参数，订阅Bar时，需要指定频率参数freq_seconds. 可以为任意的整数秒，只计算日内的K线。
          函数原型：

            - 订阅`Tick`

              ```python
              subscribe(syms, resub=False) 
              #syms 代码集合；
              #resub 是否重新订阅，True则退订以前全部已订代码，重新订阅syms。
              ```

          - 订阅`Bar`

            ```python
            subscribe(syms, freq_seconds)
            #syms 代码集合；
            #freq_seconds Bar频率；
            ```

          - 订阅示例和说明：

            - `subscribe({'SHFE.ni1901', 'DCE.i1809'}) `  订阅上期所镍1901合约，连交所铁矿石1809合约的Tick行情。
            - `subscribe({'CZCE.CF901'}, resub=True) `    退订前面的订阅代码，再订阅郑交所棉花1901合约，操作完成后，只有郑棉901合约的Tick行情。
            - `subscribe({'SHFE.ni1901', 'DCE.i1809'}, 30)`用于订阅上期所镍1901合约，连交所铁矿石1809合约的30秒K线。
            - `subscribe({'CZCE.CF901'}, 30)` 补充订阅郑交所棉花1901合约的30秒K线行情。

        - 数据回调函数
            - `on_tick(self, tick)`  tick为订阅的行情
                行情Tick根据订阅的代码，按合约逐个推送
            - `on_bar(self, bar)`  bar为订阅的K线数据
               Bar也是根据订阅情况逐个推送，如果一个合约订阅有多个不同周期，也是按不同周期各自推送，可能会在同一时间点会有多个周期的Bar。

        - 退订行情，取消订阅

           - 退订`Tick`

              ```python
              unsubscribe(syms)
              #syms 代码集合；
              ```

           - 退订`Bar`

              ```python
              unsubscribe(syms, freq_seconds)
              #syms 代码集合；
              #freq_seconds Bar频率；
              ```

        - 订阅询价

           **注**：订阅询价目前只有*`郑商所`*有这个需要，做市商则必须先订阅投资者询价，服务端才会转发询价流。对于`大商所`&`上期所`&`中金所`，服务端在做市商登录交易接口时对其账号进行身份验证，并根据其在交易所的权限，发送对应合约的询价。

           ```python
           subscribe_inquiry(syms) 
           #syms 代码集合；
           ```

        - 退订询价

            ```python
            unsubscribe_inquiry(syms)
            #syms 代码集合；
            ```

        - 询价接口

            ```python
            on_inquiry(inquiry)
            #inquiry 询价信息，Inquiry对象
            
            Inquiry 重要业务字段: 
                inquiry_id 		#询价ID，做市报价应答时需要带上。
                exchange  		#交易所ID
                sec_id 		    #合约ID
                inquiry_time    #询价时间
            ```

    - **交易接口**

        - **委托接口**
          委托接口分三类，一类是基础接口; 一类是特殊单的方便接口，比如市价单，FOK等；一类是按用户交易惯例的方便接口，比如买开、卖平、做市双边报单接口、期权相关行权委托等。

          - 基础接口示例：
              - `place_order(ord)` 用户可通过设置ord中的字段来填入委托参数。
              - `place_order(symbol, side, pe, price_type, price, volume, stop_price, time_condition=TimeCondition.GFD, volume_condition=VolumeCondition.AnyVolume, contingent_condition=ContingentCondition.Immediately) `这是一个展开接口，可以用于下各类委托，并提供了用于普通委托的默认条件参数。

          - 特殊单接口：

              - `market_order(symbol, volume, side, effect)` 市价单
              - `limit_order(symbol, price, volume, side, effect)` 限价单
              - `fok_order(symbol, price, volume, side, effect)`  全成或全撤单(fill or kill)
              - `fak_order(symbol, price, volume, side, effect)` 即成剩撤单(fill and kill)

          - 方便接口：

              - `buy_open(symbol, price_type, price, volume, stop_price)`  买开，可设置止损价
              - `sell_close(symbol, price_type, price, volume, effect=PositionEffec.Close_Today)` 卖平，默认平今
              - `sell_open(symbol, price_type, price, volume, stop_price)` 卖开，可设置止损价
              - `buy_close(symbol, price_type, price, volume, effect=PositionEffect.Close_Today) `买平，默认平今

          - 做市接口

              -  `on_inquiry` 收到询价

              - `query_quote(symbol)`    查询报价，参数为合约代码
              	 `quote_order(mmo)`	 双边报单（做市单），需要填入买卖双边的委托价和量

          - 期权接口

              - `exercise_order(exercise_order)`  请求行权

              - `cancel_exercise_order(exercise_order)`  撤销行权

              - 组合单

                  `combine_action(comb)`  请求创建或拆解持仓组合
                  

        - **撤单接口**：

            - `cancel_order(ord) `  通过ord对象撤单
            - `cancel_order(cl_ord_id) `  通过客户端委托ID撤单
            - `cancel_quote_order(mmo)`  撤做市单, 通过mmo做市单对象撤单

        - **成交事件回调函数**

            - `on_exec_rpt(rpt)`  成交事件回报

        - **订单状态跟踪**
            - `on_order_pendingnew(ord)` 委托发出
            - `on_order_new(ord)` 委托确认
            - `on_order_rejected(ord)` 委托被拒
            - `on_order_partially_filled(ord) `部分成交
            - `on_order_filled(ord)` 完全成交
            - `on_order_cancelled(ord)` 委托已撤  
            - `on_cancel_order_rejected(ord)` 撤单失败
            - `on_cancel_quote_order_rejected(mmo)` 撤双边报单失败
            - `on_quote_order(mmo)` 双边报单状态变化
            - `on_exercise_order(exerc_ord)` 行权单状态变化

    - **账户与持仓相关接口**

        - 账户数据查询结果

            不提供主动查询柜台的接口，仅仅在系统启动登录时从柜台查询账户信息，在策略初始化时如果检查账户情况，可通过实现`on_account(acc) ` 来处理，例如计算策略的交易单位等，其中acc结构如下，所有数据类型均为浮点数：

            ```python
              nav            # 总权益
              position_pnl   # 浮盈
              realized_pnl   # 平仓盈亏
              frozen_cash    # 占用保证金
              order_frozen   # 冻结资金
              available      # 可用资金
              cum_commission # 手续费
            ```

        - 持仓变动事件接口

            持仓结构position业务字段有：

            ```python
              exchange   	# 交易所代码
              sec_id		# 合约代码
              side		    # 多空方向
              volume		# 总仓量
              volume_today  # 今仓量
              price		    # 价格
            ```

            策略持仓如果有变化的话，会通过`on_position_open(pos)`和`on_position_close(pos)` 两个事件通知，如果用户需要做相应处理，需要实现这个函数；

        - 查询持仓

            `list_positions()`  查询当前持仓情况, 返回持仓列表

            `get_position(sym, side)`  查询指定合约及方向的单个持仓情况 

    - **定时器管理**

        - add_timer(datetime, timer_func, interval)  指定到具体时间datetime开始执行timer_func函数，如果interval不为0, 则间隔interval时间(单位：微秒)后重复执行timer_func。
        - add_timer(time_delay, timer_func, interval) 指定从当前时间开始time_delay微秒后开始执行timer_func函数，如果interval不为0, 则间隔interval时间(单位：微秒)后重复执行timer_func。

    - **其他事件接口**

        - `on_quote_ready()`  行情准备好

        - `on_quote_disconnected()`行情断开

        - `on_trade_ready()` 交易准备好

        - `on_trade_disconnected()` 交易断开

- **示例策略：**
  简单示例展示策略继承、初始化、启动过程。
  在策略中逐tick下单，并示范了各类事件的处理接口，其中仅打印相应事件的部分信息。

  ```Python
    #encoding: utf-8
  
    from gmsdk import *
  
    import sys
    import arrow
  
    class Example(Strategy):
    trade_ready = False
  
    def on_quote_ready(self):
        print("quote ready")
      
    def on_quote_disconnected(self):
        print("quote disconnected")
    
    def on_trade_ready(self):
        self.trade_ready = True
        print("trade ready")
  
    def on_trade_disconnected(self):
        print("trade disconnected")
        self.trade_ready = False
    
    def on_tick(self, tick):
        print("tick: ", tick.symbol(), tick.last_price, tick.volume,  tick.last_volume, tick.last_amount, tick.update_time)
        if self.trade_ready:
        	 self.buy_open(tick.symbol(), OrderPriceType.LimitPrice, tick.last_price, 1, 0.0)
  
    def on_bar(self, bar):
        print("bar: ", bar.symbol(), bar.close, bar.volume, bar.amount, bar.end_time)
    
    def on_exec_rpt(self, rpt):
        print("got rpt", rpt.sec_id)
  
    def on_order_pendingnew(self, ord):
        print("pendingnew order:", ord.sec_id, ord.volume, ord.price)
    
    def on_order_new(self, ord):
        print("new order:", ord.sec_id, ord.volume, ord.price)
  
    def on_order_rejected(self, ord):
        print("order rejected:", ord.sec_id, ord.volume, ord.price, ord.reject_reason_detail)
    
    def on_order_partially_filled(self, ord):
        print("order partially filled:", ord.sec_id, ord.volume, ord.price, ord.filled_volume)
    
    def on_order_filled(self, ord):
        print("order filled:", ord.sec_id, ord.volume, ord.price, ord.filled_volume)
  
    def on_order_cancelled(self, ord):
        print("order cancelled:", ord.sec_id, ord.volume, ord.price)
  
    def on_cancel_order_rejected(self, ord):
        print("cancel order rejected:", ord.sec_id, ord.volume, ord.price)
  
    def on_account(self, acc): 
        print("account:", acc.realized_pnl, acc.nav, acc.cum_commission)
  
    def on_position_open(self, pos): 
        print("pos open:", pos.sec_id, pos.volume, pos.side, pos.price)
  
    def on_position_close(self, pos): 
        print("pos close:", pos.sec_id, pos.volume, pos.side, pos.price)
    
    def on_timer(self, timer_id):
        print("on timer", timer_id, arrow.now())
      
  if __name__ == '__main__':
      s= Example()
      s.add_timer(0, s.on_timer, 10*1000*1000) # 10 seconds间隔，立即执行
  
      s.subscribe({'SHFE.ni1901', 'DCE.i1809', 'CFFEX.T1809', 'SHFE.ag1812'}, 5)
      s.subscribe({'CFFEX.TF1809', 'DCE.i1809', 'SHFE.ni1901', 'SHFE.ag1812'})
      #s.subscribe({'CFFEX.T1809'}, 3)
      #s.subscribe({'CFFEX.TF1809', 'DCE.i1809', 'SHFE.ni1901'})
      s.run()
  ```



### 系统枚举量定义

 枚举量定义主要用于限定一些业务参数的输入和类别判断处理，按业务含义定义，具体在编码时可以通过自动完成查找相应值。

- 证券类别 `SecType` 有Stock, Future, Option, Bond, Index, ETF值分别表示股票、期货、期权、债券、指数、ETF基金。

- 订单状态 `OrderStatus` 有委托发出待接受PendingNew, 被接受New, 被拒绝Rejected, 部分成交PartiallyFilled, 全部成交Filled, 撤销Cancelled, 待撤PendingCancel,  未触及NotTouched, 触及Touched, 未知Unknown。

- 订单方向`OrderSide`  买 Buy, 卖 Sell 

- 持仓方向`PositionSide`  多 Long, 空 Short

- 持仓影响`PositionEffect`  开Open, 平Close, 平今Close_Today, 平昨 Close_Yesterday, 强平 Force_Close, 强撤 Force_Off, 本地强平 Local_Force_Close

- 价格类型` OrderPriceType `

  - 任意价（市价）AnyPrice， 

  - 限价 LimitPrice， 

  - 最优价 BestPrice

  - 最新价 LastPrice

    最新价加价，分别加1〜3跳

    - LastPricePlusOneTicks
    - LastPricePlusTwoTicks
    - LastPricePlusThreeTicks

  - 卖一价 AskPrice1

    卖一价加价，分别加1〜3跳

    - AskPrice1PlusOneTicks
    - AskPrice1PlusTwoTicks
    - AskPrice1PlusThreeTicks

  - 买一价 BidPrice1

    买一价加价，分别加1〜3跳

    - BidPrice1PlusOneTicks
    - BidPrice1PlusTwoTicks
    - BidPrice1PlusThreeTicks

- 委托拒绝原因 `OrderRejectReason`

  - Unknown 未知原因
  - BrokerOption 柜台不允许，通常是未登录
  - IllegalSymbol 非法代码
  - NoEnoughPosition 仓位不足
  - NoEnoughCash 资金不够
  - WrongOrder 错误委托
  - FinalOrder 已结委托
  - PendingCancel 已是待撤
  - Invalid 其他不合法

- 执行状态 `ExecType`

  - CancelRejected	撤单拒绝

  - Filled 成交

  - CombineSucceed 组合成功

  - CombineFailed 组合失败

  - UncombineSucceed 拆组合成功

  - UncombineFailed 拆组合失败


### 系统配置文件

- 柜台地址和用户信息 setting.json

  - mdsock中配置的是跟行情服务之间的接口方式，可支持ipc或者tcp socket, 需要与行情服务的配置一致；另外，还有client配置，用于行情服务对策略进行识别。不同策略需要单独配置。
  - md中配置了行情柜台相关信息，只需要在行情服务中配置
    - broker_id: 机构代码
    - user_id: 客户号
    - password: 密码
    - front_uri: 行情服务地址
    - flow_file:  行情服务通讯临时文件名，通常不用修改
  - td中配置了交易柜台相关信息，只需要为策略配置
    - broker_id: 机构代码
    - user_id: 客户号
    - password: 密码
    - front_uri: 交易服务地址
    - flow_file:  交易服务通讯临时文件名，通常不用修改
    - authenticate_required：是否需要认证，如果填true, 则必须在client部分配置产品信息和授权码。
  - bargen中配置合成K线(Bar)服务用参数
    - extra_timeout_ms  合成Bar时额外等待时间，单位是毫秒，根据具体网络延时配置，可以为0, 延迟到达的tick记入下一根K线。
    - require_ongoing_bar 是否推送未完成的Bar, 默认false不推送，如果设置为true，策略中需要注意区分收到的Bar。
    - max_bar_length 为单个合约周期最多缓存Bar的条数，默认1000, 调整时需要注意留意可能超出内存容量，导致性能下降。
  - client中配置用户类别（默认投机）、产品信息和授权码。
    - client_type 用户类别，可填值为 speculation, arbitrage, hedge, market_maker;
    - product_info, auth_code 产品信息和授权码需要通过期货公司取得，在authenticate_required设置为true时，不能为空。

  ```json
  {
      "mdsock": {
          "pub_url": "ipc:///tmp/gm_pubsub.ipc",
          "req_url": "ipc:///tmp/gm_subreq.ipc",
          "client": "str1"
      },
      "md": {
          "broker_id": "9999",
          "user_id": "3934822",
          "password": "123456",
          "front_uri": "tcp://180.168.146.187:10010",
          "flow_file": "./mdflow"
      },
      "td": {
          "front_uri": "tcp://180.168.146.187:10001",
          "broker_id": "9999",
          "user_id": "3934822",
          "password": "123456",
          "authenticate_required": false,
          "settle_confirm": true,
          "flow_file": "./tdflow",
          "error_count_threshold": 200
      },
      "bargen": {
          "extra_timeout_ms": 50,
          "require_ongoing_bar": false,
          "max_bar_length": 1000
      },
      "client": {
          "client_type": "speculation",
          "product_info": "",
          "auth_code": ""
      }
  }
  ```

- 合约信息 contracts.json

  合约代码为关键词，对应的值是合约的信息，包括名称、交易所、合约乘数、以及不同情形下的保证金比例和佣金费率，相应字段均为内部使用，不提供策略使用接口，如有需要接口或想增加其他额外信息，可要求定制。

  注意：

  1. 目前仅提供给内部的持仓管理单元实时更新数据使用，策略可以通过PositionHandler拿到实时的持仓和现金数据，未详细比对，可能与柜台有少许的偏差，差异来源的最大原因可能是设置的费率与柜台实际费率不一致。
  2. 文件中的值不一定准确，默认是当前主力合约的交易所设定值，不包括临近交割合约的特殊设定，每个账户的具体保证金比例和佣金费率是不一样的，如果关注相关数据，需要跟期货公司具体确认后修改。
  3. 不同合约的佣金计费方式不同，有的是按名义金额的比例计算BY_MONEY，有的是按手数计算BY_VOLUME，如有调整，请同时修改相应的费率类型commission_type。

  ```json
   "SC": {
          "name": "原油",
          "exchange": "INE",
          "multiplier": 1000.0,
          "hedge": {
              "margin_type": "BY_MONEY",
              "short_margin_ratio": 0.05,
              "long_margin_ratio": 0.05,
              "commission_type": "BY_VOLUME",
              "open_commission_ratio": 5.0,
              "close_today_commission_ratio": 5.0,
              "close_commission_ratio": 5.0
          },
          "speculation": {
              "short_margin_ratio": 0.05,
              "close_today_commission_ratio": 5.0,
              "commission_type": "BY_VOLUME",
              "close_commission_ratio": 5.0,
              "margin_type": "BY_MONEY",
              "long_margin_ratio": 0.05,
              "open_commission_ratio": 5.0
          },
          "lock": {
              "short_margin_ratio": 0.0,
              "close_today_commission_ratio": 5.0,
              "commission_type": "BY_VOLUME",
              "close_commission_ratio": 5.0,
              "margin_type": "BY_MONEY",
              "long_margin_ratio": 0.0,
              "open_commission_ratio": 5.0
          }
      }
  ```

- 交易时段 sessions.json

  合约代码为关键词，对应的值是交易时段数组，每个时段的起始时间(st)和结束时间(et)。

  注意：

  - 该文件用于实时Bar的自动合成，除非某个合约的交易时段有变，请勿自行修改。
  - 增加新合约时，请参照下面格式增加配置，务必按时间顺序排列。

  ```json
  "SC": [
          {"st": "21:00", "et":"02:30"}, 
          {"st": "09:00", "et":"10:15"},
          {"st": "10:30", "et":"11:30"},
          {"st": "13:30", "et":"15:00"}
      ]
  ```

  *欢迎提出意见和建议，可以通过issue，或者联系QQ：17626852*
## 代码说明:
Forked From：https://github.com/51bitquant/course_codes （by 51bitquant）
- howtrader目录：将原教程代码合并为一份
- vnpy目录：讲合并后的教程代码移植到vnpy3

### 相关教程
- 网易云课堂视频：https://study.163.com/course/courseMain.htm?courseId=1210904816
- Youtube课程视频：https://www.youtube.com/@51bitquant33/videos

- 推荐学习步骤
  - No.06-09 软件安装和准备
  - No.10-12 定投策略和回测
  - No.16-19 网格策略和实盘
  - No.25-28 马丁策略和实盘（可选）

### 安装示例：

- howtrader
```
pip3 install git+https://github.com/51bitquant/howtrader.git
```
- vnpy
```
pip3 install git+https://gitee.com/vnpy/vnpy.git
pip3 install git+https://github.com/vn-crypto/vnpy_crypto.git
pip3 install vnpy_ctastrategy vnpy_ctabacktester vnpy_spreadtrading vnpy_algotrading vnpy_optionmaster vnpy_portfoliostrategy vnpy_scripttrader vnpy_chartwizard vnpy_rpcservice vnpy_excelrtd vnpy_datamanager vnpy_datarecorder vnpy_riskmanager vnpy_webtrader vnpy_portfoliomanager vnpy_paperaccount vnpy_sqlite vnpy_rqdata vnpy_binance vnpy_ctp vnpy_tushare vnpy_ib
```
### Binance测试账户：
- 现货：https://testnet.binance.vision/
- 合约：https://testnet.binancefuture.com/

### 个人学习进展:
- 在mac m1系统上，成功跑通数字货币/IB美股/Tushare A股的回测
- 接下来会先依照视频教程写几个数字货币的策略，在币安模拟盘交易

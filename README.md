# 什么是Kbacktest

Kbacktest是基于Klang的回测框架。

他的数据来自Kdata, 计算来自Klang,回测来自backtrader

Kbacktest会建立一个 websocket server，注册到 kws_manager中

### 安装Klang
```
git clone https://github.com/KlangAlpha/Klang
cd Klang
pip3 install -r requirements.txt 
python3 setup.py install
```

### 安装Kdata
```
git clone https://github.com/KlangAlpha/Kdata
cd Kdata
pip3 install -r requirements.txt 
python3 setup.py install
```

### 更多的Klang使用文档

https://klang.org.cn/docs

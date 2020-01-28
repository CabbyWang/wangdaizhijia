# coding:utf-8
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# class Product(Base):
#     # 表名
#     __tablename__ = 'products'

#     # 表结构
#     plat_id = Column(String(8), primary_key=True)
#     name = Column(String(64))
#     old_name = Column(String(64))
#     pingyin = Column(String(64))  # 全拼
#     pin = Column(String(64))  # 简拼


class PlatData(Base):
    __tablename__ = 'plats_data'

    id = Column(Integer, autoincrement=True, primary_key=True)
    plat_id = Column(String(8))  # wdzjPlatId
    newbackground = Column(String(64))  # 背景 风投系 等等
    amount = Column(String(64))  # 成交量
    incomeRate = Column(String(64))  # 平均参考收益率
    loanPeriod = Column(String(64))  # 平均借款期限
    netInflowOfThirty = Column(String(64))  # 资金净流入
    stayStillOfTotal = Column(String(64))  # 待还余额
    fullloanTime = Column(String(64))  # 满标用时
    regCapital = Column(String(64))  # 注册资金
    timeOperation = Column(String(64))  # 运营时间
    totalLoanNum = Column(String(64))  # 借款标数
    bidderNum = Column(String(64))  # 投资人数
    avgBidMoney = Column(String(64))  # 人均投资金额
    top10DueInProportion = Column(String(64))  # 前十大土豪待收金额占比
    borrowerNum = Column(String(64))  # 借款人数
    avgBorrowMoney = Column(String(64))  # 人均借款金额
    top10StayStillProportion = Column(String(64))  # 前十大借款人待还金额占比
    developZhishu = Column(String(64))  # 发展指数排名
    shuju_date = Column(String(32))  # 时间 (近七天 近30天 2019年12月 等以月份为单位)


class PlatDetail(Base):
    __tablename__ = 'plat_detail'

    id = Column(Integer, autoincrement=True, primary_key=True)
    plat_id = Column(String(8))
    chengjiaojifen = Column(String(64))  # 成交积分
    fensandu = Column(String(64))  # 分散度
    gangganjifen = Column(String(64))  # 杠杆积分
    heguijifen = Column(String(64))  # 合规积分
    jishujifen = Column(String(64))  # 技术积分
    liudongxing = Column(String(64))  # 流动性
    pinpai = Column(String(64))  # 品牌
    renqijifen = Column(String(64))  # 人气积分
    toumingdu = Column(String(64))  # 透明度


class ProblemPlat(Base):
    __tablename__ = 'problem_plats'

    id = Column(Integer, autoincrement=True, primary_key=True)
    plat_id=Column(String(8))  # plat_id
    area=Column(String(64))  # 地区
    oneline_time=Column(String(20))  # 上线时间
    problem_date=Column(String(20))  # 问题时间
    event_type=Column(String(64))  # 事件类型
    people_num=Column(String(8))
    status1=Column(String(8))  # 保留字段status1
    status2=Column(String(8))  # 保留字段status2


class Rate(Base):
    __tablename__ = 'rate'

    id = Column(Integer, autoincrement=True, primary_key=True)
    plat_name = Column(String(64))  # 平台名
    standard = Column(String(64))  # 资金流入率
    month = Column(String(32))  # 月份


# 初始化数据库连接
engine = create_engine('postgresql://wangsiyong@localhost:5432/wangdai')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

if __name__ == '__main__':
    Base.metadata.create_all(engine)

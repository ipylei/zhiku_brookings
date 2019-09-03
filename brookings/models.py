# -*- coding: utf-8 -*-
import time

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from brookings.settings import MYSQL_HOST, MYSQL_DATABASE, MYSQL_PORT, MYSQL_USERNAME, MYSQL_PASSWORD

# 创建连接
# connect_url = "mysql+pymysql://root:123456@localhost:3306/zhiku"
connection_url = "mysql+pymysql://{}:{}@{}:{}/{}".format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST,
                                                         MYSQL_PORT, MYSQL_DATABASE)
engine = create_engine(connection_url, encoding='utf-8', echo=True)

# 生成orm基类
Base = declarative_base()
Session_class = sessionmaker(bind=engine)  # 创建与数据库的会话，class,不是实例
Session = Session_class()  # 生成session实例


class SearchSeed(Base):
    """搜索表"""
    __tablename__ = 'brookings_search'  # 表名

    id = Column(Integer, primary_key=True)
    # 必须有
    url = Column(String(500), unique=True, nullable=False, comment='url')
    title = Column(String(500), nullable=False, comment='标题')
    publish_time = Column(DateTime, default=time.localtime(), comment='发布时间')
    content = Column(LONGTEXT, nullable=False, comment='内容')
    # 可有可无(含多个则都以";"隔开)
    keywords = Column(String(500), default='', comment='关键字')  # 含多个
    description = Column(Text, default='', comment='描述')
    editor = Column(String(500), default='', comment='编辑者')  # 含多个
    author = Column(String(500), default='', comment='作者')  # 含多个
    topic = Column(String(500), default='', comment='主题')  # 含多个
    top_img = Column(String(500), default='', comment='标题图片')
    tag = Column(String(500), default='', comment='标签')  # 含多个
    pdf_file = Column(Text, default='', comment='附件路径')  # 含多个

    category = Column(String(500), default='', comment='栏目')

    def save(self):
        Session.add(self)
        Session.commit()


class ExpertsSeed(Base):
    """专家表"""
    __tablename__ = 'brookings_experts'  # 表名

    id = Column(Integer, primary_key=True)
    # 必须有
    name = Column(String(255), unique=True, nullable=False, comment='姓名')
    # 可有可无
    head_portrait = Column(String(500), default='', comment='头像')
    brief_introd = Column(Text, default='', comment='简介')
    research_field = Column(Text, default='', comment='研究领域')  # 含多个
    job = Column(String(500), default='', comment='职务')  # 含多个
    education = Column(Text, default='', comment='学历')  # 含多个

    # contact = Column(String(500), default='', comment='联系方式')  # 含多个
    reward = Column(Text, default='', comment='获奖')  # 含多个
    active_media = Column(String(500), default='', comment='活跃的媒体')  # 含多个,json格式
    relevant = Column(Text, default='', comment='相关计划')  # 含多个

    pdf_file = Column(Text, default='', comment='附件路径')  # 含多个
    url = Column(String(500), unique=True, nullable=False, comment='url')

    topics = Column(String(500), default='', comment='话题')  # 含多个
    centers = Column(String(500), default='', comment='中心')  # 含多个
    projects = Column(String(500), default='', comment='项目')  # 含多个
    addition_areas = Column(Text, default='', comment='其他专业领域')
    current_positions = Column(Text, default='', comment='目前的职位')  # 含多个
    past_positions = Column(Text, default='', comment='过去的职位')  # 含多个
    languages = Column(String(500), default='', comment='语言')  # 含多个
    research_team = Column(String(500), default='', comment='研究团队')  # 含多个

    def save(self):
        Session.add(self)
        Session.commit()


class ExpertContactSeed(Base):
    __tablename__ = 'brookings_experts_contact'  # 表名
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False, comment='url')
    name = Column(String(255), nullable=False, comment='姓名')
    type = Column(String(255), nullable=False, comment='联系方式对应的类型')
    contact = Column(String(500), default='', comment='联系方式')  # 一条一个

    def save(self):
        Session.add(self)
        Session.commit()


class AbandonSeed(Base):
    """未采集的链接"""
    __tablename__ = 'brookings_abandon'  # 表名
    id = Column(Integer, primary_key=True)

    status_code = Column(Integer, comment='访问站内连接或站外连接时状态码')
    internal_url = Column(String(500), unique=True, default='', comment='遗弃的链接')
    external_url = Column(String(500), unique=True, default='', comment='重定向后的链接')

    def save(self):
        Session.add(self)
        Session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)  # 创建表结构
    pass

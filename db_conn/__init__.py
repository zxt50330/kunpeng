from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import registry

Base = declarative_base()
metadata = MetaData()

# # 创建一个 SQLAlchemy registry 对象，并将所有 models 下的 ORM 类注册到其中
# mapper_registry = registry()
# for name in dir(models):
#     obj = getattr(models, name)
#     if hasattr(obj, '__table__'):
#         mapper_registry.map_imperatively(obj)
#
# # 使用 autoload_with 方法自动加载数据库中的表和索引
# metadata.reflect(bind=engine, autoload_with=engine, only=list(mapper_registry.mappers))
#
# # 将所有 models 下的 ORM 类添加到 metadata 对象中
# for name in dir(models):
#     obj = getattr(models, name)
#     if hasattr(obj, '__table__'):
#         obj.metadata = metadata
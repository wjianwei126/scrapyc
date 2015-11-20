# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
#encoding=utf8
from sqlalchemy.exc import SQLAlchemyError
from scrapy.conf import settings

from .sqlalchemyitem import AlchemyBase,AlchemyItem

class AlchemyPipeline(object):

    def open_spider(self,spider):
        self.settings =  spider.settings
        charset = self.settings.get("SQLALCHEMY_CHARSET","utf8")
        engine = create_engine(settings['SQLALCHEMY_ENGINE_URL'],encoding=charset,convert_unicode=True)
        AlchemyBase.metadata.bind = engine
        self.session = scoped_session(sessionmaker(engine))()
        # TODO: Don't drop all. Find a way to update existing entries.
        #AlchemyBase.metadata.drop_all()
        AlchemyBase.metadata.create_all()

        

    def process_item(self, item, spider):
        if isinstance(item, AlchemyItem):
            self.session.merge(item.model)
            try:
                self.session.commit()
            except SQLAlchemyError, e:
                self.session.rollback()
                raise e

        return item
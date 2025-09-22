from peewee import *
from datetime import datetime

# SQLite 数据库配置
db = SqliteDatabase('game_usage.db')

class BaseModel(Model):
    class Meta:
        database = db

class GameSession(BaseModel):
    """游戏会话记录"""
    player_id = CharField(max_length=100)
    player_name = CharField(max_length=100)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    duration_seconds = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'game_sessions'

def init_db():
    """初始化数据库"""
    db.connect()
    db.create_tables([GameSession], safe=True)
    print("数据库初始化完成")

if __name__ == "__main__":
    init_db()
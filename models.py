from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class AdData(db.Model):
    """投放数据模型"""
    __tablename__ = 'ads'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    pkg = db.Column(db.String(50), nullable=False, index=True)
    group_name = db.Column(db.String(50), nullable=False, index=True)
    panel = db.Column(db.String(50), nullable=False, index=True)
    spend = db.Column(db.Float, default=0.0)
    spend_clean = db.Column(db.Float, default=0.0)
    revenue = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'pkg': self.pkg,
            'group': self.group_name,
            'panel': self.panel,
            'spend': self.spend,
            'spendClean': self.spend_clean,
            'revenue': self.revenue,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @property
    def roi(self):
        return (self.revenue / self.spend * 100) if self.spend > 0 else 0
    
    @property
    def roi_clean(self):
        return (self.revenue / self.spend_clean * 100) if self.spend_clean > 0 else 0


class RevenueData(db.Model):
    """收入数据模型"""
    __tablename__ = 'revenues'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    install_days = db.Column(db.Integer, nullable=False, index=True)
    coin = db.Column(db.Float, default=0.0)
    first_sub = db.Column(db.Float, default=0.0)
    renew_sub = db.Column(db.Float, default=0.0)
    coin_renew = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'installDays': self.install_days,
            'coin': self.coin,
            'firstSub': self.first_sub,
            'renewSub': self.renew_sub,
            'coinRenew': self.coin_renew,
            'total': self.total,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

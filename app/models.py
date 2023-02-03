from inspect import ismethod
from flask import json

from time import time
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.request import Request

#from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

#from flask import current_app#, url_for
from flask_sqlalchemy import SQLAlchemy

from authlib.jose import JsonWebSignature, JsonWebToken
#from authlib.jose import jwt
from itsdangerous import TimedSerializer
#from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
#from itsdangerous import JSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True
    _include_column_ = []

    def to_json(self):
        dic = {}
        for k in self.__class__._include_column_:
            value = getattr(self, k)
            if isinstance(value, list):
                values = []
                for v in value:
                    if isinstance(v, BaseModel):
                        values.append(v.to_json())

                dic[k] = values
            else:
                if isinstance(value, BaseModel):
                    dic[k] = value.to_json()
                elif isinstance(value, datetime):
                    dic[k] = value.strftime('%Y-%m-%d %H:%M')
                else:
                    dic[k] = value

        return dic

class Shoppoint(BaseModel):
    __tablename__ = 'shoppoint'
    _include_column_ = ['code', 'name', 'contact', 'mobile', 'address', 'banner', 'note']

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, index=True)
    name = db.Column(db.String(128))
    contact = db.Column(db.String(128)) # supervisor's name
    phone = db.Column(db.String(12)) # phone number
    mobile = db.Column(db.String(12))
    email = db.Column(db.String(64))
    address = db.Column(db.String(1024))
    banner = db.Column(db.String(256)) # banner in about page
    note = db.Column(db.Text)

    def __repr__(self):
        return self.name

    ## mail section
    #mail = db.Column(db.String(64))
    #mail_server = db.Column(db.String(128))
    #mail_port = db.Column(db.SmallInteger, default=587)
    #mail_use_tls = db.Column(db.Boolean, default=True)
    #mail_login_name = db.Column(db.String(64))
    #mail_login_password = db.Column(db.String(128))
    #mail_subject_prefix = db.Column(db.String(64))
    #mail_sender = db.Column(db.String(64))

# Branches of a Shoppoint (A shoppoint may have many branches)
class Branch(BaseModel):
    __tablename__ = 'branch'
    _include_column_ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32)) # Branch name
    code = db.Column(db.String(32)) # Branch code (may be generate automatically)
    appid = db.Column(db.String(32))
    appsecret = db.Column(db.String(64))
    paysecret = db.Column(db.String(64))
    mchid = db.Column(db.String(16))
    token = db.Column(db.String(64)) # token in server
    aeskey = db.Column(db.String(128)) # EncodingAESKey in server
    secret_key = db.Column(db.String(128)) # secret key different in branches

    access_token = db.Column(db.String(256))
    expires_time = db.Column(db.BigInteger) # timestamp
    jsapi_ticket = db.Column(db.String(256))
    jsapi_expires_time = db.Column(db.BigInteger) # timestamp
    third_party = db.Column(db.SmallInteger) # 1-Google 2-Facebook

    shoppoint_id = db.Column(db.Integer, db.ForeignKey('shoppoint.id'), nullable=True)
    shoppoint = db.relationship('Shoppoint',
                         backref=db.backref('parts', lazy="dynamic"))

    def get_access_token(self):
        if self.access_token and self.expires_time and self.expires_time > int(time()):
            return self.access_token

        print('Get token from weixin or cannot get access token', self.code)

        # get access token
        #params = urllib.parse.urlencode({'grant_type': 'client_credential', 'appid': app_id, 'secret': app_secret})
        #params = params.encode('ascii')
        #with urllib.request.urlopen("https://api.weixin.qq.com/cgi-bin/token?%s", params) as f:
        #    result = f.read().decode('utf-8')
        #    print (result)
        #    j = json.loads(result)
        #info = _access_weixin_api("https://api.weixin.qq.com/cgi-bin/token?%s",
        #                        grant_type='client_credential', appid=self.weixin_appid, secret=self.weixin_appsecret)
        params = {'grant_type':'client_credential', 'appid':self.appid, 'secret':self.appsecret}
        url_param = urlencode(params).encode('utf-8')
        with urlopen("https://api.weixin.qq.com/cgi-bin/token?%s", url_param) as f:
            result = f.read().decode('utf-8')
            info = json.loads(result)

            if 'errcode' in info or 'access_token' not in info or 'expires_in' not in info:
                errcode = info.get('errcode')
                errmsg = info.get('errmsg')
                return ''

            self.access_token = info.get('access_token')
            self.expires_time = int(time()) + info.get('expires_in') - 10
            db.session.commit()

            return self.access_token
        return ''

class Staff(BaseModel):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), primary_key=True) # used in weixin
    nickname = db.Column(db.String(128))
    name = db.Column(db.String(128), index=True)
    gender = db.Column(db.SmallInteger, default=0)
    phone = db.Column(db.String(12), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    privilege = db.Column(db.Integer, default=0) # every bit as a privilege

    shoppoint_id = db.Column(db.Integer, db.ForeignKey('shoppoint.id'), nullable=True)
    shoppoint = db.relationship('Shoppoint',
                         backref=db.backref('staffs', lazy="dynamic"))

    def __repr__(self) -> str:
        return self.name


class Member(BaseModel):
    __tablename__ = 'member'
    _include_column_ = ['openid', 'nickname', 'avatarUrl', 'privilege', 'name', 'phone', 'access_token', 'expires_time']

    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), unique=True) # used in third party institute
    name = db.Column(db.String(128))
    nickname = db.Column(db.String(128))
    phone = db.Column(db.String(12))
    avatarUrl = db.Column(db.String(2048))
    #session_key = db.Column(db.String(64), unique=True) # used in weixin
    #generate_session_key = db.Column(db.String(128), unique=True) # used in weixin
    privilege = db.Column(db.Integer, default=0) # every bit as a privilege

    session_key = db.Column(db.String(256)) # session key from third party
    access_token = db.Column(db.String(256)) # user need this to login
    expires_time = db.Column(db.BigInteger) # timestamp, default is 2 hours

    shoppoint_id = db.Column(db.Integer, db.ForeignKey('shoppoint.id'), nullable=True)
    shoppoint = db.relationship('Shoppoint',
                         backref=db.backref('openids', lazy="dynamic"))

    def __repr__(self):
        return self.nickname

    def generate_auth_token(self, secret_key, expiration=7200):
        s = TimedSerializer(secret_key, expires_in=expiration)

        return s.dumps({'openid': self.openid})

    def generate_access_token(self, secret_key):
        s = Serializer(secret_key)#, expires_in=expiration)
        self.access_token = s.dumps({'session_key': self.session_key}).decode('UTF-8')

    def verify_access_token(self, secret_key):
        s = Serializer(secret_key)
        try:
            data = s.loads(self.access_token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token

        #print('session_keys:', self.session_key, data['session_key'])
        return self.session_key == data['session_key']

    @staticmethod
    def verify_auth_token(token, secret_key):
        s = TimedSerializer(secret_key)
        try:
            data = s.loads(s)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token

        return Memeber.query.get(data['openid'])

class Tag(BaseModel):
    __tablename__ = 'tag'
    _include_column_ = []
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, index=True, nullable=True)
    name = db.Column(db.String(128), index=True)
    display_code = db.Column(db.String(64))
    display_image = db.Column(db.String(1024))

    products = db.relationship("ProductTag", back_populates="tag")

    def __repr__(self):
        return self.name

class ProductTag(BaseModel):
    __tablename__ = 'product_tag'
    _include_column_ = []

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    index = db.Column(db.SmallInteger, default=0) # sequence number in list
    title = db.Column(db.String(256))

    tag = db.relationship("Tag", back_populates="products")
    product = db.relationship("Product", back_populates="tags")

    def __repr__(self) -> str:
        return self.title

class ProductCategory(BaseModel):
    __tablename__ = 'product_category'
    _include_column_ = ['id', 'name', 'extra_info', 'index', 'show_allowed', 'to_point', 'summary', 'note']

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, index=True, nullable=True)
    name = db.Column(db.String(128), index=True)
    extra_info = db.Column(db.String(128))
    piece = db.Column(db.Integer, default=1) # 数量
    price = db.Column(db.Integer, default=100) # 价格，单位分
    index = db.Column(db.SmallInteger, default=0) # sequence number in list
    #promote_allowed = db.Column(db.Boolean, default=True) # 团购允许标志
    status = db.Column(db.Integer, default=0) # status 0x01-deleted
    to_point = db.Column(db.Boolean, default=True) # get some points when bought some product in this category
    summary = db.Column(db.Text)
    note = db.Column(db.Text)

    shoppoint_id = db.Column(db.Integer, db.ForeignKey('shoppoint.id'))
    shoppoint = db.relationship('Shoppoint',
                         backref=db.backref('categories', lazy="dynamic"))

    def __repr__(self):
        return self.name

class Product(BaseModel):
    __tablename__ = 'product'
    _include_column_ = ['id', 'code', 'name', 'price', 'member_price', 'promote_price', 'sold', 'promote_sold', 'stock', 'promote_stock',
                        'promote_type','summary', 'note', 'show_allowed', 'category_id', 'promote_begin_time',
                        'promote_end_time', 'images', 'sizes']
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False, unique=True, index=True)
    name = db.Column(db.String(128), unique=True, index=True)
    piece = db.Column(db.Integer, default=1) # 数量
    price = db.Column(db.Integer, default=999900)
    member_price = db.Column(db.Integer, default=999900) # price for member
    promote_price = db.Column(db.Integer, default=999900) # the price of promote
    tax = db.Column(db.Integer, default=5) # need to divide by 100
    sold = db.Column(db.Integer, default=0) # the amount of total sold
    promote_sold = db.Column(db.Integer, default=0) # the amount of total sold in promote price
    stock = db.Column(db.Integer, default=0) # the amount in stock
    promote_stock = db.Column(db.Integer, default=0) # the amount of product in stock must be less than stock
    index = db.Column(db.Integer, default=0) # the sequece in list
    to_point = db.Column(db.Boolean, default=False) # get some points when bought this item
    status = db.Column(db.Integer, default=0)
    summary = db.Column(db.Text)
    note = db.Column(db.Text)

    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    category = db.relationship('ProductCategory',
                         backref=db.backref('products', lazy="dynamic"))

    shoppoint_id = db.Column(db.Integer, db.ForeignKey('shoppoint.id'))
    shoppoint = db.relationship('Shoppoint',
                         backref=db.backref('products', lazy="dynamic"))

    promote_begin_time = db.Column(db.DateTime) # the begin time of promote
    promote_end_time = db.Column(db.DateTime) # the end of time of promote

    images = db.relationship('ProductImage', back_populates='product', order_by="asc(ProductImage.index)")
    orders = db.relationship('OrderProduct', back_populates='product')

    tags = db.relationship('ProductTag', back_populates='product')

    def __repr__(self):
        return self.name


class Image(BaseModel):
    __tablename__ = 'image'
    _include_column_ = ['id', 'name', 'title', 'type']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True) # the name of image in harddisk
    hash_value = db.Column(db.String(128), index=True) # MD5 value
    status = db.Column(db.Integer, default=0)

    shoppoint_id = db.Column(db.Integer, db.ForeignKey('shoppoint.id'), nullable=True)
    shoppoint = db.relationship('Shoppoint', backref=db.backref('images', lazy="dynamic"))

    products = db.relationship('ProductImage', back_populates='image')

    def __repr__(self):
        return self.name

class ProductImage(BaseModel):
    __tablename__ = 'product_image'
    _include_column_ = ['product_id', 'index', 'type', 'image', 'note']

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), primary_key=True)
    index = db.Column(db.Integer, default=1) # 1 when it is a banner, otherwise 1 or bigger than 1
    status = db.Column(db.Integer, default=0)

    kind = db.Column(db.Integer, default=1) # 1-banner 2-detail 4-ad
    title = db.Column(db.String(128)) # the title of image
    note = db.Column(db.Text) # description of image

    product = db.relationship("Product", back_populates="images")
    image = db.relationship('Image', back_populates='products')

class Order(BaseModel):
    __tablename__ = 'order'
    _include_column_ = ['code', 'payment_code', 'index', 'cost', 'delivery_way', 'delivery_fee', 'refund', 'mode', 'payment', 'order_time', 'pay_time', 'note', 'openid', 'products', 'address', 'status']

    code = db.Column(db.String(32), primary_key=True, index=True) # order coder
    payment_code = db.Column(db.String(128), nullable=True) # code from third party
    #cashier = models.ForeignKey(Staff)
    original_cost = db.Column(db.Integer, default=0) # original cost of order
    cost = db.Column(db.Integer, default=0) # cost at present
    delivery_fee = db.Column(db.Integer, default=0)
    refund = db.Column(db.Integer, default=0)
    refund_delivery_fee = db.Column(db.Integer, default=0)

    mode = db.Column(db.SmallInteger, default=0) # 0-buy, 1-recharge, 2-return goods, 4-cannel account
    payment = db.Column(db.Integer, default=0) # payment method
    bonus_balance = db.Column(db.Integer, default=0) # amount of balance in recharging member card

    prepay_id = db.Column(db.String(128), nullable=True) # usually used in wechat
    prepay_id_expires = db.Column(db.BigInteger) # usually used in wechat

    order_time = db.Column(db.DateTime, default=datetime.now) # order generate time
    pay_time = db.Column(db.DateTime) # order paid time
    delivery_way = db.Column(db.SmallInteger, default=0) # the method of deleivery 
    delivery_time = db.Column(db.DateTime, default=datetime.now) # delivery time
    finished_time = db.Column(db.DateTime)

    notify_time = db.Column(db.DateTime) # need to notify admin
    status = db.Column(db.Integer, default=1) # 1-not pay 2-paid, wait for get/delivery  4-deliverid 8-complete 16-notified admin 32-notified customer
    note = db.Column(db.Text)

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    member = db.relationship("Member", backref=db.backref("orders", lazy="dynamic"))

    products = db.relationship('OrderProduct', back_populates='order')

    # the address of the order
    address = db.relationship('OrderAddress', uselist=False, back_populates='order')
    #payments = db.relationship('OrderPayment', back_populates='order')

    shoppoint_id = db.Column(db.Integer, db.ForeignKey('shoppoint.id'), nullable=True)
    shoppoint = db.relationship('Shoppoint',
                         backref=db.backref('orders', lazy="dynamic"))

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=True)
    branch = db.relationship('Branch',
                         backref=db.backref('orders', lazy="dynamic"))

    def next_index(self):
        next_index = db.session.query(db.func.max(Order.index)).filter_by(promotion_id=self.promotion_id).scalar()
        if next_index:
            next_index += 1
        else:
            next_index = 1

        if next_index == 250:
            next_index += 1

        self.index = next_index

    # 订单成功后，修改已售和库存
    def commit_amount(self):
        if not self.promotion:
            return

        for pp in self.promotion.products:
            for op in self.products:
                if pp.product_id == op.product_id:
                    pp.sold += op.amount
                    pp.stock -= op.amount
                    pp.product.promote_sold = op.amount if not pp.product.promote_sold else pp.product.promote_sold + op.amount
                    pp.product.sold = op.amount if not pp.product.sold else pp.product.sold + op.amount
                    pp.product.promote_stock = -op.amount if not pp.product.promote_stock else pp.product.promote_stock - op.amount
                    pp.product.stock = -op.amount if not pp.product.stock else pp.product.stock - op.amount

    # 订单取消后，恢复已售和库存
    def rollback_amount(self):
        if not self.promotion:
            return

        for pp in self.promotion.products:
            for op in self.products:
                if pp.product_id == op.product_id:
                    pp.sold -= op.amount
                    pp.stock += op.amount
                    pp.product.promote_sold -= op.amount
                    pp.product.sold -= op.amount
                    pp.product.promote_stock += op.amount
                    pp.product.stock += op.amount


class OrderProduct(BaseModel):
    __tablename__ = 'order_product'
    _include_column_ = ['product', 'amount', 'price']

    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(32), db.ForeignKey('order.code'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    price = db.Column(db.Integer, default=0) # 商品在该订单中实际支付的价格
    amount = db.Column(db.Integer, default=0) # 该订单中产品的数量
    refund = db.Column(db.Integer, default=0) # 该商品退款金额

    order = db.relationship("Order", back_populates="products")
    product = db.relationship("Product", back_populates="orders")

class OrderAddress(BaseModel):
    __tablename__ = 'order_address'
    _include_column_ = ['name', 'phone', 'province', 'city', 'district', 'address']

    order_code = db.Column(db.String(32), db.ForeignKey('order.code'), primary_key=True)

    name = db.Column(db.String(128))
    phone = db.Column(db.String(12))
    province = db.Column(db.String(32))
    city = db.Column(db.String(32))
    district = db.Column(db.String(32))
    address = db.Column(db.String(512))

    order = db.relationship("Order", back_populates="address")

    def full_address(self):
        full_addr = ''
        if self.province is not None:
            full_addr += self.province
        if self.city is not None:
            full_addr += self.city
        if self.district is not None:
            full_addr += self.district
        if self.address is not None:
            full_addr += self.address
        return full_addr

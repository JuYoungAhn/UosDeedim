#-*- coding: utf-8 -*- 

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
import cgi
import logging
import datetime
from google.appengine.api import images
import logging
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users
import locale
from google.appengine.api import users
import webapp2
from webapp2_extras import sessions

try:
    import json
except ImportError:
    import simplejson as json

class User(db.Model):
 id = db.StringProperty()
 password = db.StringProperty()
 name = db.StringProperty()
 postcode = db.StringProperty()
 address = db.StringProperty()
 detail_address = db.StringProperty()
 phone = db.StringProperty()
 gender = db.StringProperty()
 birthday_year = db.IntegerProperty()
 birthday_month = db.IntegerProperty()
 birthday_day = db.IntegerProperty()
 date = db.DateTimeProperty(auto_now_add=True)
 
class RepairOrder(db.Model):
 id = db.StringProperty()
 address = db.StringProperty()
 detail_address = db.StringProperty()
 phone = db.StringProperty()
 repair_name = db.StringProperty()
 repair_type = db.IntegerProperty()
 price = db.IntegerProperty()
 final_price = db.IntegerProperty()
 state = db.IntegerProperty()
 date = db.DateTimeProperty(auto_now_add=True)
 
class ShareEvent(db.Model):
 name = db.StringProperty()
 story = db.StringProperty()
 address = db.StringProperty()
 amount = db.StringProperty()
 phone = db.IntegerProperty()
 image = db.BlobProperty()
 date = db.DateTimeProperty(auto_now_add=True)
 
class RepairCategory(db.Model):
 name = db.StringProperty()
 before_price = db.IntegerProperty()
 after_price = db.IntegerProperty()
 des = db.StringProperty()
 image = db.BlobProperty()
 type = db.IntegerProperty()

class Product(db.Model):
 name = db.StringProperty()
 company = db.StringProperty()
 price = db.IntegerProperty()
 image = db.BlobProperty()
 repre_img = db.BlobProperty()
 detail_img1 = db.BlobProperty()
 detail_img2 = db.BlobProperty()
 detail_img3 = db.BlobProperty()
 size = db.IntegerProperty()
 description = db.StringProperty()
 date = db.DateTimeProperty(auto_now_add=True)

productCount = 8

class BaseHandler(webapp2.RequestHandler):
    title = 'Deedim'
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class BasePage(webapp.RequestHandler):
    title = 'Deedim'
    def intWithCommas(self, x):
        if type(x) not in [type(0), type(0L)]:
            raise TypeError("Parameter must be an integer.")
        if x < 0:
            return '-' + self.intWithCommas(-x)
        result = ''
        while x >= 1000:
            x, r = divmod(x, 1000)
            result = ",%03d%s" % (r, result)
        return "%d%s" % (x, result)
  
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
  
class MainPage(BaseHandler):
    def get(self):
        q = Product.all().order("-date")
        result = q.fetch(5)
       
        user = self.session.get('user')
        
        for r in result :
            r.price_str = BasePage().intWithCommas(r.price)
                
        template_values = {'title': self.title, 'result':result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'start.html')
        
        self.response.out.write(template.render(path, template_values))
        
class BoardList(BaseHandler):
    def get(self):
        user = self.session.get('user')
        menu_id = int(self.request.get('menu_id'))
        template_values = {'title': self.title, 'menu_id' : int(menu_id), 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        
        if (menu_id == 1) :
            path = os.path.join(path, 'list.html')
        elif(menu_id == 2) :
            path = os.path.join(path, 'usecase.html')
        elif(menu_id == 3) :
            path = os.path.join(path, 'review.html')
        elif(menu_id == 4) :
            path = os.path.join(path, 'share_list.html')
            
        self.response.out.write(template.render(path, template_values))

class Sales(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = Product.all().order("-date")[0:productCount]
        count = len(result)
        
        moreProduct = True
        if (count < productCount ):
            moreProduct = False
        
        for r in result :
            r.price_str =  r.price_str = BasePage().intWithCommas(r.price)
                              
        template_values = {'title': self.title, 'result' : result, 'offset' : productCount, 'moreProduct' : moreProduct, 'count': count, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'sales.html')
        self.response.out.write(template.render(path, template_values))

class Description(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'description.html')
        self.response.out.write(template.render(path, template_values))
        
class AboutUs(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'aboutus.html')
        self.response.out.write(template.render(path, template_values))

class ImgHandler():
    def transform(self, file):
        img = images.Image(file)
        img.im_feeling_lucky()
        img.resize(600, 600)
        png_data = img.execute_transforms(output_encoding=images.PNG)
        
        return png_data
    
    def original(self, file):
        img = images.Image(file)
        img.im_feeling_lucky()
        png_data = img.execute_transforms(output_encoding=images.PNG)
        
        return png_data
    
    def thumbnailTransform(self, file):   
        img = images.Image(file)
        img.im_feeling_lucky()
        img.resize(300, 300)
        png_data = img.execute_transforms(output_encoding=images.PNG)
        
        return png_data

class ProductList(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = Product.all().order("-date")
        
        template_values = {'title': self.title, 'result':result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'product_list.html')
        self.response.out.write(template.render(path, template_values))
     
class ProductWrite(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'product_write.html')
        
        self.response.out.write(template.render(path, template_values))

    def post(self):
        name = cgi.escape(self.request.get('name'))
        price = int(cgi.escape(self.request.get('price')))
        company = cgi.escape(self.request.get('company'))
        description = cgi.escape(self.request.get('description'))
        size = int(cgi.escape(self.request.get('size')))
        
        # Get the actual data for the picture and Transform
        imgHandlerIns = ImgHandler();
        thumbnail_img = None
        repre_img = None
        
        if(self.request.get("image")) :
            repre_img = imgHandlerIns.transform(self.request.get("image"))
            thumbnail_img = imgHandlerIns.transform(self.request.get("image"))
            
        obj = Product(name=name, price=price, company=company, image=thumbnail_img, description=description,
                      size = size, repre_img=repre_img).put()
         
        self.redirect('/sales')

class ProductDelete(BaseHandler):
    def post(self):
        db.delete(cgi.escape(self.request.get('key')));
        self.redirect('/productList')    

class ProductUpdate(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = db.get(self.request.get("key"))
        
        template_values = {'result' : result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'product_update.html')
        self.response.out.write(template.render(path, template_values))  
    def post(self):
        obj = db.get(self.request.get("key"))
        
        obj.name = cgi.escape(self.request.get('name'))
        obj.price = int(cgi.escape(self.request.get('price')))
        obj.company = cgi.escape(self.request.get('company'))
        obj.description = cgi.escape(self.request.get('description'))
        obj.size = int(cgi.escape(self.request.get('size')))
        
        imgHandlerIns = ImgHandler();
        
        thumbnail_img = None
        repre_img = None
          
        if(self.request.get("image")) :
            repre_img = imgHandlerIns.transform(self.request.get("image"))
            thumbnail_img = imgHandlerIns.transform(self.request.get("image"))
        
        obj.thumbnail_img = db.Blob(thumbnail_img)
        obj.repre_img = db.Blob(repre_img)
        obj.put()    
            
        self.redirect('/productList')    
            
class Image(BaseHandler):
  def get(self, key):
    product = db.get(key)
    self.response.headers['Content-Type'] = 'image/png'
    self.response.out.write(product.image)
    
class Image2(BaseHandler):
  def get(self, key):
    product = db.get(key)
    self.response.headers['Content-Type'] = 'image/png'
    self.response.out.write(product.image)
    

class ShowDetailImg1(BaseHandler):
    def get(self, key):
        product = db.get(key)
    
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(product.detail_img1)
            
class ShowDetailImg2(BaseHandler):
    def get(self, key):
        product = db.get(key)
    
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(product.detail_img2)
        
class ShowDetailImg3(BaseHandler):
    def get(self, key):
        product = db.get(key)
    
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(product.detail_img3)        
 
class GetProducts(BaseHandler):
    def post(self):
        logging.info(self.request.body)
        data = json.loads(self.request.body)
        offset = data['offset']
        limit = offset+productCount
        
        result = Product.all().order("-date")[offset:limit]
        count = len(result)
        
        for r in result :
            r.price_str =  r.price_str = BasePage.intWithCommas(self, r.price)
        
        moreProduct = True
        if (count < productCount ):
            moreProduct = False
        
        template_values = {'result' : result, 'offset' : limit, 'moreProduct' : moreProduct}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'product.html')
        self.response.out.write(template.render(path, template_values))  

class Event(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'event.html')
        self.response.out.write(template.render(path, template_values))
            
class Faq(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'faq.html')
        self.response.out.write(template.render(path, template_values)) 
    
class Repair(BaseHandler):
    def get(self):
        user = self.session.get('user')
        type = int(self.request.get('type'))
        type_name = None
        
        if(type == 1) :
            type_name = "남성구두"
        elif(type == 2) :
            type_name = "여성구두"
        elif(type == 3) :
            type_name = "워커 "
        elif(type == 4) :
            type_name = "운동화"
                    
        result = RepairCategory.all()
        result.filter('type', type) 
        count = result.count()
        
        template_values = {'title': self.title, 'result' : result, 'count' : count, 'type' : type, 'user':user, 'type_name':type_name}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'repair.html')
        self.response.out.write(template.render(path, template_values))    
        
class Order(BaseHandler):
    def get(self):
        user = self.session.get('user')
        
        key = self.request.get("key")
        repair = db.get(key)
        template_values = {'title': self.title, 'repair':repair, 'key':key, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'order.html')
        self.response.out.write(template.render(path, template_values))        
                 
    def post(self):
        user = self.session.get('user')
        id = user['id']
        phone = cgi.escape(self.request.get('phone'))
        address = cgi.escape(self.request.get('address'))
        detail_address = cgi.escape(self.request.get('detail_address'))
        repair_type = int(cgi.escape(self.request.get('repair_type')))
        repair_name = cgi.escape(self.request.get('repair_name'))
        price = int(cgi.escape(self.request.get('price')))
        state = 1
            
        """
        state 1 : order complete
        state 2 : money wait
        state 3 : money complete
        state 4 : shipping
        """
            
        obj = RepairOrder(id=id, phone=phone, address=address, detail_address=detail_address,
                          repair_type=repair_type,repair_name=repair_name,price=price,state=state).put()

        self.redirect('/userOrderList?order_complete=1') 

class OrderList(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = RepairOrder.all().order("-date")
        template_values = {'title': self.title, 'result':result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'order_list.html')
        self.response.out.write(template.render(path, template_values))       
        
class OrderDelete(BaseHandler):
    def post(self):
        key = self.request.get("key")
        db.delete(key)    
        self.redirect('/orderList')               
        
class Sample(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'slider_example.html')
        self.response.out.write(template.render(path, template_values))
        
class EventWrite(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'event_write.html')
        self.response.out.write(template.render(path, template_values))        
    def post(self):
        name = cgi.escape(self.request.get('name'))
        phone = int(cgi.escape(self.request.get('phone')))
        address = cgi.escape(self.request.get('address'))
        story = cgi.escape(self.request.get('story'))
        amount = cgi.escape(self.request.get('amount'))
        
        # Get the actual data for the picture and Transform
        imgHandlerIns = ImgHandler();
        thumbnail_img = None
        
        if(self.request.get("image")) :
            thumbnail_img = imgHandlerIns.transform(self.request.get("image"))
            
        obj = ShareEvent(name=name, phone=phone, address=address, image=thumbnail_img, story=story, amount=amount).put()

        self.redirect('/event') 
        
class EventList(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = ShareEvent.all().order("-date")
        
        template_values = {'title': self.title, 'result' : result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'event_list.html')
        self.response.out.write(template.render(path, template_values))   
        
class EventContent(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = db.get(self.request.get("key"))
        
        template_values = {'title': self.title, 'result' : result, 'user':user}
        
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'event_content.html')
        self.response.out.write(template.render(path, template_values))  

class EventDelete(BaseHandler):
    def post(self):
        key = self.request.get("key")
        db.delete(key)    
        self.redirect('/eventList')    
                
class OrderContent(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = db.get(self.request.get("key"))
        template_values = {'title': self.title, 'result' : result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'order_content.html')
        self.response.out.write(template.render(path, template_values))          
    def post(self):
        key = self.request.get("key")
        obj = db.get(self.request.get("key"))
        obj.state = int(cgi.escape(self.request.get('state')))
        obj.final_price = int(cgi.escape(self.request.get('final_price')))
        obj.put()    
            
        self.redirect('/orderContent?key='+key)        
        
class Join(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'join.html')
        self.response.out.write(template.render(path, template_values))    
   
    def post(self):
        id = cgi.escape(self.request.get('id'))
        password = cgi.escape(self.request.get('password'))
        name = cgi.escape(self.request.get('name'))
        birthday_year = int(cgi.escape(self.request.get('birthday_year')))
        birthday_month = int(cgi.escape(self.request.get('birthday_month')))
        birthday_day = int(cgi.escape(self.request.get('birthday_day')))
        postcode = cgi.escape(self.request.get('postcode'))
        address = cgi.escape(self.request.get('address'))
        detail_address = cgi.escape(self.request.get('detail_address'))
        gender = cgi.escape(self.request.get('gender'))
        phone = cgi.escape(self.request.get('phone'))
        
        obj = User(name=name, id=id, password=password, birthday_day=birthday_day,birthday_year=birthday_year,
                       birthday_month=birthday_month,postcode=postcode,address=address,detail_address=detail_address,
                       gender=gender,phone=phone)
                       
        result = User.all()
        result.filter('id', id)
        
        if(result.count() >= 1) :
            template_values = {'title': self.title, 'message':'The ID is duplicated.', 'user': obj}
            path = os.path.join(os.path.dirname(__file__), 'templates')
            path = os.path.join(path, 'join.html')
            self.response.out.write(template.render(path, template_values))
        
        else :     
            id = cgi.escape(self.request.get('id'))
            password = cgi.escape(self.request.get('password'))
            name = cgi.escape(self.request.get('name'))
            birthday_year = int(cgi.escape(self.request.get('birthday_year')))
            birthday_month = int(cgi.escape(self.request.get('birthday_month')))
            birthday_day = int(cgi.escape(self.request.get('birthday_day')))
            postcode = cgi.escape(self.request.get('postcode'))
            address = cgi.escape(self.request.get('address'))
            detail_address = cgi.escape(self.request.get('detail_address'))
            gender = cgi.escape(self.request.get('gender'))
            phone = cgi.escape(self.request.get('phone'))
            
            obj = User(name=name, id=id, password=password, birthday_day=birthday_day,birthday_year=birthday_year,
                       birthday_month=birthday_month,postcode=postcode,address=address,detail_address=detail_address,
                       gender=gender,phone=phone).put()
             
            self.redirect('/login')  
        
class OrderWrite(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'order_write.html')
        self.response.out.write(template.render(path, template_values))    
        
    def post(self):
        name = cgi.escape(self.request.get('name'))
        before_price = int(cgi.escape(self.request.get('before_price')))
        after_price = int(cgi.escape(self.request.get('after_price')))
        des = cgi.escape(self.request.get('des'))
        type = int(cgi.escape(self.request.get('type')))
        
        # Get the actual data for the picture and Transform
        imgHandlerIns = ImgHandler();
        img = None
        
        if(self.request.get("image")) :
            img = imgHandlerIns.original(self.request.get("image"))
            
        obj = RepairCategory(name=name, before_price=before_price, after_price=after_price, 
                             image=img, des=des, type=type).put()
         
        self.redirect('/repair?type=1')  
  
class MyOrder(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'my_order.html')
        self.response.out.write(template.render(path, template_values))      

    def post(self):
        name = cgi.escape(self.request.get('name'))
        password = cgi.escape(self.request.get('password'))
        result = RepairOrder.all()
        result.filter('name', name)
        result.filter('password', password)
        result = result.get()
        
        template_values = {'title': self.title, 'result' : result}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'my_order_content.html')
        self.response.out.write(template.render(path, template_values))        
              
class AdminMenu(BaseHandler):
    def get(self):
        user = self.session.get('user')
        answer = cgi.escape(self.request.get('answer'))
        
        if(answer == "박성주") :
            template_values = {'title': self.title, 'user':user}
            path = os.path.join(os.path.dirname(__file__), 'templates')
            path = os.path.join(path, 'admin_menu.html')
            self.response.out.write(template.render(path, template_values))  
        else :
            self.redirect('/adminPassword')
            
    def post(self):
        user = self.session.get('user')
        answer = cgi.escape(self.request.get('answer'))
        answer = answer.encode('utf-8')
        
        if(answer == "박성주") :
            template_values = {'title': self.title, 'user':user}
            path = os.path.join(os.path.dirname(__file__), 'templates')
            path = os.path.join(path, 'admin_menu.html')
            self.response.out.write(template.render(path, template_values))  
        else :
            self.redirect('/adminPassword')

class Login(BaseHandler):
    def get(self):
        user = self.session.get('user')
        
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'login.html')
        self.response.out.write(template.render(path, template_values)) 
    
    def post(self):
        id = cgi.escape(self.request.get('id'))
        password = cgi.escape(self.request.get('password'))
        
        user = None
        
        result = User.all()
        result.filter('id', id)
        user = result.get()
        
        #login success
        if((result.count() >= 1) and (user.password == password)) :
            user = result.get()
            self.session['user'] = {'name':user.name, 'id':user.id, 'phone':user.phone, 'address':user.address,
                                    'detail_address' : user.detail_address, 'postcode' :user.postcode}
            
            user = self.session.get('user')
            template_values = {'title': self.title, 'user':user}
            path = os.path.join(os.path.dirname(__file__), 'templates')
            path = os.path.join(path, 'start.html')
            self.response.out.write(template.render(path, template_values))
        
        #login fail    
        else :
            template_values = {'title': self.title, 'message' : 'Login failed'}
            path = os.path.join(os.path.dirname(__file__), 'templates')
            path = os.path.join(path, 'login.html')
            self.response.out.write(template.render(path, template_values))
            
class Logout(BaseHandler):
    def get(self):
        self.session['user'] = None
        template_values = {'title': self.title}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'start.html')
        self.response.out.write(template.render(path, template_values)) 
    
class UserManage(BaseHandler):
    def get(self):
        user = self.session.get('user')
        
        result = User.all().order("-date")
        template_values = {'title': self.title, 'result' : result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'user_manage.html')
        self.response.out.write(template.render(path, template_values))                     

class UserDelete(BaseHandler):
    def post(self):
        key = self.request.get("key")
        db.delete(key)    
        self.redirect('/userManage')    
        
class Mypage(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'mypage.html')
        self.response.out.write(template.render(path, template_values))                         
       
    def post(self):
        user = User.all()
        user.filter('id', self.session.get('user')['id'])
        user = user.get()
        
        user.phone = cgi.escape(self.request.get('phone'))
        user.postcode = cgi.escape(self.request.get('postcode'))
        user.address = cgi.escape(self.request.get('address'))
        user.detail_address = cgi.escape(self.request.get('detail_address'))
        
        # password not change
        if(cgi.escape(self.request.get('password')) == "") :
            user.put()
            self.session['user'] = {'name':user.name, 'id':user.id, 'phone':user.phone, 'address':user.address,
                                    'detail_address' : user.detail_address, 'postcode' :user.postcode}
        
            self.redirect('/mypage')
        
        # password change    
        elif(cgi.escape(self.request.get('password')) != "" and user.password == cgi.escape(self.request.get('password'))) :
            user.password = cgi.escape(self.request.get('password2'))
            user.put()      
            self.session['user'] = {'name':user.name, 'id':user.id, 'phone':user.phone, 'address':user.address,
                                    'detail_address' : user.detail_address, 'postcode' :user.postcode}
        
            self.redirect('/mypage')       
            
        # current password failed
        else :
            user = self.session.get('user')
            template_values = {'title': self.title, 'user':user, 'message' : '1'}
            path = os.path.join(os.path.dirname(__file__), 'templates')
            path = os.path.join(path, 'mypage.html')
            self.response.out.write(template.render(path, template_values))    
              
        
class UserOrderList(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = RepairOrder.all()
        result.filter("id", user['id'])
        order_complete = cgi.escape(self.request.get('order_complete'))
        
        template_values = {'title': self.title, 'user':user, 'result':result, 'order_complete':order_complete}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'user_order_list.html')
        self.response.out.write(template.render(path, template_values))      
        
class UserOrderContent(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = db.get(self.request.get("key"))
        template_values = {'title': self.title, 'result' : result, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'user_order_content.html')
        self.response.out.write(template.render(path, template_values)) 
        
class UserOrderDelete(BaseHandler):
    def post(self):
        db.delete(cgi.escape(self.request.get('key')));
        self.redirect('/userOrderList')              
                
class RepairBest(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'repairbest.html')
        self.response.out.write(template.render(path, template_values))         
        
class AdminPassword(BaseHandler):
    def get(self):
        user = self.session.get('user')
        template_values = {'title': self.title, 'user':user}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'admin_password.html')
        self.response.out.write(template.render(path, template_values))         

class OrderItemList(BaseHandler):
    def get(self):
        user = self.session.get('user')
        
        result = RepairCategory.all()
        
        template_values = {'title': self.title, 'user':user, 'result' : result}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'order_item_list.html')
        self.response.out.write(template.render(path, template_values))       
                   
class OrderItemContent(BaseHandler):
    def get(self):
        user = self.session.get('user')
        result = db.get(self.request.get("key"))
        template_values = {'title': self.title, 'result' : result, 'user':user}
        
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'order_item_content.html')
        self.response.out.write(template.render(path, template_values))  
    def post(self):
        key = self.request.get("key")
        obj = db.get(self.request.get("key"))
        obj.name = cgi.escape(self.request.get('name'))
        obj.before_price = int(cgi.escape(self.request.get('before_price')))
        obj.after_price = int(cgi.escape(self.request.get('after_price')))
        obj.des = cgi.escape(self.request.get('des'))
        obj.type = int(cgi.escape(self.request.get('type')))
        obj.put()    
            
        self.redirect('/orderItemContent?key='+key)    
        
class OrderItemDelete(BaseHandler):
    def post(self):
        key = self.request.get("key")
        db.delete(key)    
        self.redirect('/orderItemList')    
            
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}
                            
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/aboutUs', AboutUs),
                                      ('/boardList', BoardList),
                                      ('/description', Description),
                                      ('/sales', Sales),
                                      ('/show_image/([-\w]+)', Image),
                                      ('/show_image2/([-\w]+)', Image2),
                                      ('/show_detail1/([-\w]+)', ShowDetailImg1),
                                      ('/show_detail2/([-\w]+)', ShowDetailImg2),
                                      ('/show_detail3/([-\w]+)', ShowDetailImg2),
                                      ('/productWrite', ProductWrite),
                                      ('/getProducts', GetProducts),
                                      ('/productList', ProductList),
                                      ('/productDelete', ProductDelete),
                                      ('/productUpdate', ProductUpdate),
                                      ('/sample', Sample),
                                      ('/event', Event),
                                      ('/join', Join),
                                      ('/eventWrite', EventWrite),
                                      ('/eventList', EventList),
                                      ('/eventContent', EventContent),
                                      ('/eventDelete', EventDelete),
                                      ('/orderList', OrderList),
                                      ('/orderContent', OrderContent),
                                      ('/orderDelete', OrderDelete),
                                      ('/myOrder', MyOrder),
                                      ('/repair', Repair),
                                      ('/order', Order),
                                      ('/login', Login),
                                      ('/orderWrite', OrderWrite),
                                      ('/adminMenu', AdminMenu),
                                      ('/userManage', UserManage),
                                      ('/userDelete', UserDelete),
                                      ('/logout', Logout),
                                      ('/mypage', Mypage),
                                      ('/userOrderList', UserOrderList),
                                      ('/repairBest', RepairBest),
                                      ('/userOrderContent', UserOrderContent),
                                      ('/userOrderDelete', UserOrderDelete),
                                      ('/adminPassword', AdminPassword),
                                      ('/orderItemList', OrderItemList),
                                      ('/orderItemContent', OrderItemContent),
                                      ('/orderItemDelete', OrderItemDelete),
                                      ('/faq', Faq)], 
                                     config=config,
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

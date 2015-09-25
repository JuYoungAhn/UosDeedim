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

try:
    import json
except ImportError:
    import simplejson as json


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

class ProductDetailImage(db.Model):
    product_idx = db.IntegerProperty()
    detail_img1 = db.BlobProperty()
    detail_img2 = db.BlobProperty()
    detail_img3 = db.BlobProperty()

productCount = 8

class BasePage(webapp.RequestHandler):
    title = 'DeedimWork'
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
  
class MainPage(BasePage):
    def get(self):
        q = Product.all().order("-date")
        result = q.fetch(5)
        
        for r in result :
            r.price_str = BasePage.intWithCommas(self, r.price)
                
        template_values = {'title': self.title, 'result':result}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'start.html')
        
        self.response.out.write(template.render(path, template_values))
        
class BoardList(BasePage):
    def get(self):
        menu_id = int(self.request.get('menu_id'))
        template_values = {'title': self.title, 'menu_id' : int(menu_id)}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        
        if (menu_id == 1) :
            path = os.path.join(path, 'list.html')
        elif(menu_id == 2) :
            path = os.path.join(path, 'review.html')
        elif(menu_id == 3) :
            path = os.path.join(path, 'faq.html')
        self.response.out.write(template.render(path, template_values))

class Sales(BasePage):
    def get(self):
        result = Product.all().order("-date")[0:productCount]
        count = len(result)
        
        moreProduct = True
        if (count < productCount ):
            moreProduct = False
        
        for r in result :
            r.price_str =  r.price_str = BasePage.intWithCommas(self, r.price)
                              
        template_values = {'title': self.title, 'result' : result, 'offset' : productCount, 'moreProduct' : moreProduct, 'count': count}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'sales.html')
        self.response.out.write(template.render(path, template_values))

class Description(BasePage):
    def get(self):
        template_values = {'title': self.title}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'description.html')
        self.response.out.write(template.render(path, template_values))
        
class AboutUs(BasePage):
    def get(self):
        template_values = {'title': self.title}
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
    
    def thumbnailTransform(self, file):   
        img = images.Image(file)
        img.im_feeling_lucky()
        img.resize(300, 300)
        png_data = img.execute_transforms(output_encoding=images.PNG)
        
        return png_data

class ProductList(BasePage):
    def get(self):
        result = Product.all().order("-date")
        
        template_values = {'title': self.title, 'result':result}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'product_list.html')
        self.response.out.write(template.render(path, template_values))
     
class ProductWrite(BasePage):
    def get(self):
        template_values = {'title': self.title}
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
        detail_img1 = None
        detail_img2 = None
        detail_img3 = None
        
        if(self.request.get("image")) :
            repre_img = imgHandlerIns.transform(self.request.get("image"))
            thumbnail_img = imgHandlerIns.transform(self.request.get("image"))
        if(self.request.get("detail_img1")) :
            detail_img1 = imgHandlerIns.transform(self.request.get("detail_img1"))
        if(self.request.get("detail_img2")) : 
            detail_img2 = imgHandlerIns.transform(self.request.get("detail_img2"))
        if(self.request.get("detail_img3")) : 
            detail_img3 = imgHandlerIns.transform(self.request.get("detail_img3"))
            
        obj = Product(name=name, price=price, company=company, image=thumbnail_img, description=description,
                      size = size, repre_img=repre_img).put()
         
        obj2 = db.get(obj)              
        obj2.detail_img1 = db.Blob(detail_img1)
        obj2.put()
        
        obj3 = db.get(obj)
        obj3.detail_img2 = detail_img2
        obj3.put()
        
        obj4 = db.get(obj)
        obj4.detail_img3 = detail_img3
        obj4.put()

        self.redirect('/sales')

class ProductDelete(BasePage):
    def post(self):
        db.delete(cgi.escape(self.request.get('key')));
        self.redirect('/productList')    

class ProductUpdate(BasePage):
    def get(self):
        
        result = db.get(self.request.get("key"))
        
        template_values = {'result' : result}
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
        detail_img1 = None
        detail_img2 = None
        detail_img3 = None
          
        if(self.request.get("image")) :
            repre_img = imgHandlerIns.transform(self.request.get("image"))
            thumbnail_img = imgHandlerIns.transform(self.request.get("image"))
        if(self.request.get("detail_img1")) :
            detail_img1 = imgHandlerIns.transform(self.request.get("detail_img1"))
        if(self.request.get("detail_img2")) : 
            detail_img2 = imgHandlerIns.transform(self.request.get("detail_img2"))
        if(self.request.get("detail_img3")) : 
            detail_img3 = imgHandlerIns.transform(self.request.get("detail_img3"))
        
        obj.thumbnail_img = db.Blob(thumbnail_img)
        obj.repre_img = db.Blob(repre_img)
        obj.detail_img1 = detail_img1
        obj.detail_img2 = detail_img2
        obj.detail_img3 = detail_img3
        
        obj.put()    
            
        self.redirect('/productList')    
            
class Image(BasePage):
  def get(self, key):
    product = db.get(key)
    self.response.headers['Content-Type'] = 'image/png'
    self.response.out.write(product.image)
    
class Image2(BasePage):
  def get(self, key):
    product = db.get(key)
    self.response.headers['Content-Type'] = 'image/png'
    self.response.out.write(product.image)
    

class ShowDetailImg1(BasePage):
    def get(self, key):
        product = db.get(key)
    
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(product.detail_img1)
            
class ShowDetailImg2(BasePage):
    def get(self, key):
        product = db.get(key)
    
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(product.detail_img2)
        
class ShowDetailImg3(BasePage):
    def get(self, key):
        product = db.get(key)
    
        self.response.headers['Content-Type'] = 'image/png'
        self.response.out.write(product.detail_img3)        
 
class GetProducts(BasePage):
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
            
class Sample(BasePage):
    def get(self):
        template_values = {'title': self.title}
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'sample.html')
        self.response.out.write(template.render(path, template_values))
                    
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
                                      ('/sample', Sample)], 
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

import random,os,string
from flask import render_template,request,abort,redirect,flash,make_response,url_for,session
#redirect only works when secret key is set
#Local Imports
from bookapp import app, csrf
from bookapp.models import db, Admin, Book, Category
from bookapp.forms import *

def generate_string(howmany): #cal this function 
   x = random.sample(string.ascii_lowercase,howmany)
   return ''.join(x)

@app.route("/admin/edit/book/<id>",methods=["POST","GET"])
def edit_book(id):
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return redirect(url_for("admin_login"))
   else:
      if request.method =="GET":
         deets = db.session.query(Book).filter(Book.book_id==id).first_or_404()
         cats = db.session.query(Category).all()
         return render_template("admin/editbook.html",deets=deets,cats=cats)
      else:
         #retrieving the form data
         book_2update = Book.query.get(id)
         book_2update.book_title = request.form.get('title')
         book_2update.book_catid = request.form.get('category')
         book_2update.book_status = request.form.get('status')
         
         book_2update.book_desc = request.form.get('description')
         book_2update.book_publication = request.form.get('yearpub')

         cover = request.files.get('cover')
         #check if file was selected for upload
         if cover.filename !="":
         #let thefilename remain the same on the database
      
           name,ext = os.path.splitext(cover.filename)
           if ext.lower() in ['.jpg','.png','.jpeg']:
              newfilename = generate_string(10) + ext
              cover.save("bookapp/static/uploads/"+ newfilename)
              book_2update.book_cover = newfilename
           else:
              flash("The extension of the book cover was not included")
         db.session.commit()
         flash("Book details was added")
         return redirect('/admin/books')
         


@app.route("/admin/delete/<id>/")
def book_delete(id):
   book = db.session.query(Book).get_or_404(id)
   #Lets get the name of the file attached to this book
   filename = book.book_cover
   #First delete the file before deleting the book from db
   if filename != None and filename !='default.png' and os.path.isfile("bookapp/static/uploads/"+filename):
      os.remove("bookapp/static/uploads/"+filename)
   db.session.delete(book)
   db.session.commit()
   flash("Book has been deleted!")
   return redirect(url_for("all_books"))


@app.route('/admin/addbook/',methods=["POST","GET"])
def addbook():
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return redirect(url_for("admin_login"))
   else:
      if request.method =="GET":
         cats = db.session.query(Category).all()
         return render_template('admin/addbook.html',cats=cats)
      else:
         #retrieve file
         allowed = ['jpg','png']
         fileobj = request.files['cover']
         filename = fileobj.filename
         newname = "default.png" #default cover
         if filename =='': #No file was uploaded
            flash("Book cover not included",category='error')
         else: #file was selected # To make sure it is random
            newname =str(int(random.random()*1000000000))+filename
            pieces = filename.split('.')
            ext = pieces[-1]#.lower()
            if ext.lower() in allowed:
               fileobj.save("bookapp/static/uploads/" + newname)
            else:
               flash("File extension not allowed, file was not upoaded",category='error')

        
         
         #retrieve all the form data
         title = request.form.get('title')
         category = request.form.get('category')
         status = request.form.get('status')
         description = request.form.get('description')
         yearpub = request.form.get('yearpub')
         #Insert into db
         bk = Book(book_title=title,book_desc=description,book_publication=yearpub,book_catid=category,book_status=status,book_cover=newname)
         db.session.add(bk)
         db.session.commit()
         if bk.book_id:
            flash("Book has been added")
         else:
            flash("Please try again")
         return redirect(url_for('all_books'))

@app.route("/admin/logout")
def admin_logout():
   if session.get("adminuser") != None:
      session.pop("adminuser",None)
      session.pop("role",None)
      flash("You are logged out",category="info")
      return redirect(url_for("admin_login"))
   else:
      return redirect(url_for('admin_login'))
      



@app.route("/admin/dashboard/")
def admin_dashboard():
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return redirect(url_for("admin_login"))
   else:
      return render_template('admin/dashboard.html')

@app.route("/admin/books")
def all_books():
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return redirect(url_for("admin_login"))
   else:
      books = db.session.query(Book).all()
      return render_template("admin/allbooks.html",books=books)

@app.route("/admin/")
def admin_page():
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return render_template("admin/login.html")
   else:
      return redirect(url_for('admin_dashboard'))


@app.route("/admin/login/",methods=["GET","POST"])
def admin_login():
   if request.method =='GET':
      return render_template('admin/login.html')
   else:
      #retrieve form data
      username = request.form.get("username")
      pwd = request.form.get("pwd")
      #check if it is in the database
      check = db.session.query(Admin).filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first()
      #if it is in the db, save in session and redirect to dashboard
      if check: #It is indb, save session
         session['adminuser']=check.admin_id
         session['role']='admin'
         return redirect(url_for('admin_dashboard'))
      else: #if not, save message in flash, redirect to login again
         flash('Invalid Login',category='error')
         return redirect(url_for('login'))


      



@app.after_request
def after_request(response):
   #To solve the problem
   response.headers["Cache-Control"]="no-cache, no-store, must-revalidate"
   return response
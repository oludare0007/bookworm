import json, requests, random, string
from functools import wraps
from flask import render_template,request,abort,redirect,flash,make_response,url_for,session 

from werkzeug.security import generate_password_hash, check_password_hash
#redirect only works when secret key is set
#Local Imports
from bookapp import app, csrf, mail, Message
from bookapp.models import db, Book, User, Category, State, Lga, Reviews, Donation

from bookapp.forms import *

def login_required(f):
   @wraps(f) #This ensures that details(meta data) about the original function f, that is being decorated is still available
   def login_check(*args,**kwargs):
      if session.get("userloggedin") !=None:
         return f(*args,**kwargs)
      else:
         flash("Access Denied")
         return redirect('/login')
   return login_check
#To use login_required, place the route decorator over any route that needs authentication


def generate_string(howmany): #call this function 
   x = random.sample(string.digits,howmany)
   return ''.join(x)

@app.route("/donate/",methods=["POST","GET"])
@login_required
def donation():
   donform = DonForm()
   if request.method =="GET":
      deets = db.session.query(User).get(session['userloggedin'])
      return render_template("user/donation.html",donform=donform,deets=deets)
   else:
      if donform.validate_on_submit():
         #retrieve form data
         amt = float(donform.amt.data) * 100
         donor = donform.fullname.data
         email = donform.email.data
         #generate a traansaction reference number
         ref = 'BW' +str(generate_string(8))
         #insert into database
         donation = Donation(don_amt=amt,don_userid=session['userloggedin'],don_email=email,don_fullname=donor,don_status='pending',don_refno=ref)
         db.session.add(donation)
         db.session.commit()
         #save the reference number in session
         session['trxno'] = ref
        
         #redirect to a confirmation page
         return redirect("/confirm_donation")
      else:
         deets = db.session.query(User).get(session['userloggedin'])
         return render_template("user/donation.html",donform=donform,deets=deets)

@app.route("/confirm_donation/")
@login_required
def confirm_donation():
   """We want to display the details of the transaction saved from the previous page"""
   deets = db.session.query(User).get(session['userloggedin'])
   if session.get('trxno') == None: #means they are visiting directly
      flash("Please complete this form", category="error")
      return redirect("/donate")
   else:
      donation_deets = Donation.query.filter(Donation.don_refno==session['trxno']).first()
      return render_template("user/donation_confirmation.html",donation_deets=donation_deets)


@app.route('/sendmail/')
def send_email():
   file = open('requirements.txt')
   msg = Message(subject="Adding Heading to Email From Bookworm",sender="From BookWorm Website",recipients=["olaniyanjoshua@gmail.com"])
   msg.html="""<h1>Welcome Home!</h1>
            <img src='https://images.pexels.com/photos/18386361/pexels-photo-18386361/free-photo-of-fashion-love-people-woman.jpeg?auto=compress&cs=tinysrgb&w=1600&lazy=load'> <hr>"""
   msg.attach("saved_as.txt", "application/text", file.read())
   mail.send(msg)

   return "Done"
   
@app.route("/ajaxopt/",methods=["POST","GET"])
def ajax_options():
   cform = ContactForm()
   if request.method=="GET":
      return render_template("user/ajax_options.html",cform=cform)
   else:
      
      email = request.form.get('email') 
      return f"Thank you, your email has been added {email}"

@app.route("/dependent/")
def dependent_dropdown():
   #write a query to fetch all the states from state table
   states = db.session.query(State).all()
   return render_template('user/show_states.html',states=states)

@app.route("/lga/<stateid>/")
def load_lgas(stateid):
   records = db.session.query(Lga).filter(Lga.state_id==stateid).all()
   str2return = "<select>"
   for r in records:
      optstr = f"<option value='{r.lga_id}'>"+r.lga_name+"</option>"
      str2return = str2return + optstr 

   str2return = str2return + "</select>"

   return str2return 



@app.route("/contact/")
def ajax_contact():
   data = "I am a string coming from the server"
   return render_template("user/ajax_test.html",data=data)

@app.route('/submission/',methods=['POST','GET'])
def ajax_submission():
   """This route will be visited by ajax silently"""
   user = request.form.get('fullname')
   if user !="" and user !=None:
      return f"Thank you {user} for completing the form"
   else:
      return "Please complete the form"

@app.route('/checkusername/',methods=["POST","GET"])
def checkusername():
      email = request.args.get('username')
      query = db.session.query(User).filter(User.user_email==email).first()
      if query:
         return "The email has been taken"
      else:
         flash("Email has been accepted")
         return "Email is okay" 



@app.route("/favourite/")
def favourite_topics():
   bootcamp = {'name':'Joshua','topics':['html','css','python']}
   category =[]
   cats = db.session.query(Category).all()
   # for c in cats:
   #    category.append(c.cat_name)

   category= [c.cat_name for c in cats]
   return json.dumps(category,indent=3)



@app.route("/profile/",methods=["GET","POST"])
@login_required
def edit_profile():
   id = session.get('userloggedin')
   userdeets = db.session.query(User).get(id)
   pform = ProfileForm()
   if request.method =="GET":
      return render_template('user/edit_profile.html',pform=pform,userdeets=userdeets)
   else:
      if pform.validate_on_submit():
         fullname = request.form.get("fullname") #pform.fullname.data
         userdeets.user_fullname = fullname
         db.session.commit()
         flash("Your profile has been edited")
         return redirect ("/dashboard")
      else:
         return render_template("user/edit_profile.html",pform=pform,userdeets=userdeets)
      


@app.route("/changedp/",methods=["POST","GET"])
@login_required
def changedp():
   id = session.get("userloggedin")
   userdeets = db.session.query(User).get(id)
   dpform = DpForm()
   if request.method =="GET":
      return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)
   else:
      if dpform.validate_on_submit():
         pix = request.files.get('dp')
         filename = pix.filename
         pix.save(app.config['USER_PROFILE_PATH']+filename)
         userdeets.user_pix = filename
         db.session.commit()
         flash("Profile picture updated")
         return redirect(url_for('dashboard'))
      else:
         return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)


@app.route("/viewall/")
def viewall():
   #books = db.session.query(Book).all()
   books = db.session.query(Book).filter(Book.book_status=="1").all()
   return render_template("user/viewall.html",books=books)

@app.route("/logout")
def logout():
   if session.get('userloggedin') !=None:
      session.pop('userloggedin',None)
   return redirect('/')



@app.route("/dashboard")
def dashboard():
   if session.get('userloggedin') !=None:
      id = session.get('userloggedin')
      userdeets = User.query.get(id)
      return render_template("user/dashboard.html",userdeets=userdeets)
   else:
      flash("You need to login to access this page")
      return redirect("/login")

@app.route('/login',methods=["POST","GET"])
def login():
   if request.method =='GET':
      return render_template('user/loginpage.html')
   else:
      email = request.form.get('email')
      pwd = request.form.get('pwd')
      deets = db.session.query(User).filter(User.user_email==email).first()
      if deets !=None:
         hashed_pwd = deets.user_pwd
         if check_password_hash(hashed_pwd,pwd) == True:
            session['userloggedin'] = deets.user_id
            return redirect("/dashboard")
         else:
            flash("Invalid Credentials, try again")
            return redirect("/login")
      else:
            flash("Invalid Credentials, try again")
            return redirect("/login")

@app.route("/register/",methods=["GET","POST"])
def register():
   regform=RegForm()
   if request.method =='GET':
      return render_template("user/signup.html",regform=regform)
   else:
      if regform.validate_on_submit():
         fullname = request.form.get("fullname")
         email = request.form.get("email")
         pwd = request.form.get("pwd")
         hashed_pwd = generate_password_hash(pwd)
         u = User(user_fullname=fullname,user_email=email,user_pwd=hashed_pwd)
         db.session.add(u)
         db.session.commit()
         flash("An account has been created for you. Please login.")
         return redirect('/login')
      else:
         return render_template("user/signup.html",regform=regform)

@app.route("/submit_review/",methods=["POST"])
def submit_review():
   title = request.form.get('title') 
   content = request.form.get('content')
   book = request.form.get('book')
   userid = session['userloggedin']
   br = Reviews(rev_title=title,rev_text=content,rev_userid=userid,rev_bookid=book)
   db.session.add(br) 
   db.session.commit() 

   restr = f"""<article class="blog-post">
      
      <h5 class="blog-post-title">{ title }</h5>
      <p class="blog-post-meta">Reviwed just now by <a href="#">{ br.reviewby.user_fullname }</a></p>

      <p>{ content }</p>
      <hr> 
    </article>"""
   return restr




@app.route("/")
def homepage():
   books =db.session.query(Book).filter(Book.book_status=="1").limit(4).all()
   #connect to the endpoint http://127.0.0.1:8000/api/v1.0/listall to collect data of books
   #pass it to the template and display it on it
   try:
      response = requests.get("http://127.0.0.1:5000/api/v1.0/listall/")
      rsp = json.loads(response.txt)
   except:
      rsp = None #If the server is unreachable
   return render_template("user/home_page.html",books=books,rsp=rsp) 

@app.route("/myreviews/")
@login_required
def myreviews(): 
   id = session['userloggedin']
   userdeets = db.session.query(User).get(id)
   return render_template("user/myreviews.html",userdeets=userdeets) 
 
@app.route("/books/details/<id>")
def book_details(id):
   book = Book.query.get_or_404(id)
   return render_template("user/reviews.html",book=book)

@app.after_request
def after_request(response):
   #To solve the problem
   response.headers["Cache-Control"]="no-cache, no-store, must-revalidate"
   return response
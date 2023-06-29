from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from flask_mysqldb import MySQL
from model import *
from auto_delete import *
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from flask_paginate import Pagination, get_page_parameter, get_page_args
import math
import plotly.graph_objs as go
from flask_mail import Mail, Message
from mail import *
from datetime import date
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="thunhotel"
)
mycursor = mydb.cursor()

#connection to database
app.secret_key = 'freeanything'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'thunhotel'
mysql = MySQL(app)


@app.route("/")
@app.route("/home")
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT room_config.*, facility_config.* FROM room_config LEFT JOIN facility_config ON room_config.fac_id = facility_config.f_id ORDER BY room_config.roomid ASC LIMIT 5")
    datashow = cur.fetchall()
    cur.close()

    return render_template('pages/index.html', orderdata=datashow)

    # if 'loggedin' in session:
    #     return render_template('pages/index.html', orderdata=datashow)
    # flash('Please Login first','danger')
    # return redirect(url_for('login'))

#bill
@app.route("/bill" ,methods=["GET"])
def bill():     
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pay ORDER BY id ASC")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('/pages/admin/bill.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))

@app.route("/setting", methods=('GET','POST'))
def setting():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user ORDER BY id ASC LIMIT 1")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('pages/setting.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))

@app.route('/settingupdate', methods=['POST'])
def settingupdate():
    
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        email = request.form['email']
        level = request.form['level']
        gender = request.form['gender']
        address = request.form['address']
        phone = request.form['phone']
        
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE user SET username=%s, email=%s, level=%s, gender=%s, address=%s, phone=%s WHERE id=%s", 
        (username, email, level, gender, address, phone, id))
        mysql.connection.commit()
        flash("Data successfully Updated")
        return redirect(url_for('home'))

@app.route("/contacts", methods=('GET','POST'))
def contacts():
    return render_template('pages/contacts.html')

#insert contact
@app.route('/insertcontact', methods=['POST'])
def insertcontact():
    if request.method == 'POST':
        f_name      = request.form['f_name']
        l_name      = request.form['l_name']
        email       = request.form['email']
        phone       = request.form['phone']
        message    = request.form['message']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contact (f_name, l_name, email, phone, message ) VALUES (%s, %s, %s, %s, %s)", (f_name, l_name, email, phone, message))
        mysql.connection.commit()

    if request.method == 'POST':
        email = request.form['email']
        
        #check data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM contact WHERE email=%s',(email, ))
        account = cursor.fetchone()
        if account is None:
            flash('Login Failed, Wrong Email','danger')
        else:
            msg = Message("Feedback In Contact Us", sender='thuanmai362001@gmail.com',
                            recipients=[email])
            msg.body = "Thank You " + account[1] + " Thank you for your comments to help us improve our service "
            mail.send(msg)
    return redirect(url_for('contacts'))


# doanh thu
@app.route("/doanhthu" ,methods=["GET"])
def doanhthu():     
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM doanhthu ORDER BY id ASC")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('/pages/admin/chart.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))


@app.route("/booking-home")
def booking_home():
    # Get today's date
    today = date.today()

    # Format today's date as a string in the format "YYYY-mm-dd"
    today_str = today.strftime('%Y-%m-%d')

    return render_template('pages/booking.html',date=datetime.date.today(),today=today,today_str=today_str)

@app.route("/room_detail/<int:id>", methods=["GET"])
def room_detail(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM room_config WHERE roomid=%s", (id,))
    datashow = cur.fetchall()
    mysql.connection.commit()

    if 'loggedin' in session:
        return render_template('pages/details.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))
    

@app.route('/payment/<int:id>', methods=['GET'])
def payment(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM room_config WHERE roomid=%s", (id,))
    datashow = cur.fetchall()
    mysql.connection.commit()

    if 'loggedin' in session:
        return render_template('pages/payment.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))
    

@app.route('/paymentupdate', methods=['POST'])
def paymentupdate():
    if request.method == 'POST':
        roomid   = request.form['roomid']
        night   = request.form['night']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE room_config SET night=%s WHERE roomid=%s", 
        (night,roomid))
        mysql.connection.commit()
        return redirect(url_for('payment_step2', id=roomid))

@app.route('/payment-step2/<int:id>', methods=('GET','POST'))
def payment_step2(id):
    # Get today's date
    today = date.today()

    # Format today's date as a string in the format "YYYY-mm-dd"
    today_str = today.strftime('%Y-%m-%d')

    cur = mysql.connection.cursor()
    cur.execute("SELECT room_config.roomid, pay.customer, pay.payed, pay.night, pay.tax, pay.room_type, pay.user_id, user.email, room_config.tax, room_config.night, room_config.roomprice, room_config.roomtype, user.id, room_config.userr_id FROM room_config LEFT JOIN user ON room_config.userr_id = user.id LEFT JOIN pay ON user.id = pay.user_id WHERE roomid=%s LIMIT 1", (id,))
    datashow = cur.fetchall()
    mysql.connection.commit()

    if 'loggedin' in session:
        return render_template('pages/payment_step2.html', orderdata=datashow,date=datetime.date.today(),today=today,today_str=today_str)
    flash('Please Login first','danger')
    return redirect(url_for('login'))

@app.route('/insertpayment-step2', methods=('GET','POST'))
def insertpayment_step2():
    if request.method == 'POST':
        customer = request.form['customer']
        payed = request.form['payed']
        night = request.form['night']
        room_type	 = request.form['room_type']
        tax = request.form['tax']
        user_id = request.form['user_id']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO pay (customer, payed, night, room_type, tax, user_id) VALUES (%s, %s, %s, %s, %s, %s)", (customer, payed, night, room_type, tax, user_id))
        mysql.connection.commit()


    if request.method == 'POST':
        roomid      = request.form['roomid']
        night       = request.form['night']
        checkin     = request.form['checkin'] 
        checkout    = request.form['checkout']
        userr_id    = request.form['userr_id']

        curso = mysql.connection.cursor()
        curso.execute("UPDATE room_config SET night=%s, checkin=%s, checkout=%s,userr_id=%s WHERE roomid=%s", (night, checkin, checkout, userr_id, roomid))
        mysql.connection.commit()

    if request.method == 'POST':
        email = request.form['email']
        

        #check data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email=%s',(email, ))
        account = cursor.fetchone()
        if account is None:
            flash('Login Failed, Wrong Email','danger')
        else:
            msg = Message("Booking Hotel Config", sender='thuanmai362001@gmail.com',
                            recipients=[email])
            msg.body = "Thank you for using our services" 
            mail.send(msg)
        return redirect(url_for('bookingdone',id=roomid))      

@app.route('/bookingdone/<int:id>', methods=['GET'])
def bookingdone(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM room_config WHERE roomid=%s", (id,))
    datashow = cur.fetchall()
    mysql.connection.commit()

    if 'loggedin' in session:
        return render_template('pages/bookingdone.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))

#mail booking done
# @app.route('/bookingdonemail', methods=('GET','POST'))
# def bookingdonemail():
        
#         #check data username
#         cursor = mysql.connection.cursor()
#         cursor.execute('SELECT * FROM user WHERE email=%s',(email, ))
#         account = cursor.fetchone()
#         msg = Message("Change Password Config", sender='thuanmai362001@gmail.com',
#                             recipients=[email])
#         msg.body = "Wellcome " + account[1] + " We have accept your request. Here is your password: " + account[3]
#         mail.send(msg)
#         return redirect(url_for('login'))
    # return render_template('pages/bookingdone.html')

@app.route("/gallery", defaults={"page":1})
@app.route("/gallery/<int:page>", methods=["GET"])
def gallery(page):

    limit = 8 
    offset = page*limit - limit 

    my_cur = mysql.connection.cursor()
    my_cur.execute("SELECT * FROM room_config where roomid")
    total_row = my_cur.rowcount
    total_page = math.ceil(total_row / limit)

    next = page+1
    prev = page-1

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM room_config ORDER BY roomid DESC LIMIT %s OFFSET %s",(limit,offset))
    datashow = cur.fetchall()
    cur.close()
    
    return render_template('pages/gallery.html', page=total_page, next=next, prev=prev, orderdata=datashow)

@app.route("/about")
def about():
    return render_template('pages/about.html')

@app.route("/details")
def details():

    return render_template('pages/details.html')

@app.route("/staff")
def staff():
    return render_template('pages/staff.html')

@app.route("/error")
def error():
    return render_template('pages/error.html')

@app.route("/new", methods=["GET"])
def new():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tintuc ORDER BY id DESC LIMIT 9")
    datashow = cur.fetchall()
    cur.close()
    return render_template('pages/new.html', orderdata=datashow)

@app.route("/addnew")
def addnew():
    return render_template('pages/addnew.html')

#insert news
@app.route('/newinsert', methods=['POST'])
def newinsert():
    if request.method == 'POST':
        title = request.form['tieude']
        Content = request.form['noidung']
        Describe = request.form['mota']
        Picture = request.form['hinhanh']
        Author = request.form['nguoi']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tintuc (tieude, noidung, mota, hinhanh, nguoi ) VALUES (%s, %s, %s, %s, %s)", (title, Content, Describe, Picture, Author))
        mysql.connection.commit()
        flash("Data sent successfully")
        return redirect(url_for('addnew'))



@app.route("/login",methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        #check data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email=%s',(email, ))
        account = cursor.fetchone()
        if account is None:
            flash('Login Failed, Wrong Email','danger')
        elif not account[3]:
            flash('Login failed, Check Your Password', 'danger')
        else:
            session['loggedin'] = True
            session['username'] = account[1]
            session['level'] = account[4]
            return redirect(url_for('check_login'))
    return render_template('pages/login_register/login.html')

#logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('level', None)
    return redirect(url_for('login'))

@app.route('/check_login')
def check_login():
    if 'loggedin' in session:
        return redirect(url_for('home'))
    flash('Please Login first','danger')
    return redirect(url_for('login'))
#register
@app.route("/register", methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        level = request.form['level']
        gender = request.form['gender']
        address = request.form['address']
        phone = request.form['phone']

        #check username or email
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE username=%s OR email=%s',(username, email, ))
        account = cursor.fetchone()

        if account is None:
            cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)', (username, email, password, level, gender, address, phone))
            mysql.connection.commit()
            flash('Successful Registration','success')
        else :
            flash('Username or email already exists','danger')

    if request.method == 'POST':
        email = request.form['email']
        

        #check data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email=%s',(email, ))
        account = cursor.fetchone()
        if account is None:
            flash('Login Failed, Wrong Email','danger')
        else:
            msg = Message("Wellcome To Hotel", sender='thuanmai362001@gmail.com',
                            recipients=[email])
            msg.body = "Wellcome " + account[1] + " You have successfully registration ! "
            mail.send(msg)
        return redirect(url_for('login'))    
    return render_template('pages/login_register/register.html')

#forgot pass
@app.route("/forgot-password", methods=('GET','POST'))
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        

        #check data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email=%s',(email, ))
        account = cursor.fetchone()
        if account is None:
            flash('Login Failed, Wrong Email','danger')
        else:
            msg = Message("Change Password Config", sender='thuanmai362001@gmail.com',
                            recipients=[email])
            msg.body = "Wellcome " + account[1] + " We have accept your request. Here is your password: " + account[3]
            mail.send(msg)
            return redirect(url_for('login'))
    return render_template('pages/login_register/forgot_password.html')

@app.route("/reset-password", methods=('GET','POST'))
def resetpassword(): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user ORDER BY id ASC LIMIT 1")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('pages/login_register/reset_password.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))  
@app.route('/resetpasswordupdate', methods=['POST'])
def resetpasswordupdate():
    
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE user SET password=%s  WHERE id=%s", 
        (password,id))
        mysql.connection.commit()
        flash("Data successfully Updated")
        return redirect(url_for('setting'))

#insert customers data
@app.route('/booking', methods=['POST'])
def customerinsert():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        type = request.form['type']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        nor = request.form['nor']
        info = request.form['info']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO customer (name, email, phone, type, checkin, checkout, nor, info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (name, email, phone, type, checkin, checkout, nor, info))
        mysql.connection.commit()
        flash("Data sent successfully")
        return redirect(url_for('booking_home'))

# admin
@app.route("/admin/account")
def account():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer ORDER BY id DESC")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('pages/admin/account.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))

#update data
@app.route('/accountupdate', methods=['POST'])
def accountupdate():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        type = request.form['type']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        nor = request.form['nor']
        status = request.form['status']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE customer SET name=%s, email=%s, phone=%s, type=%s, checkin=%s, checkout=%s, nor=%s, status=%s WHERE id=%s", 
        (name, email, phone, type, checkin, checkout, nor, status, id))
        mysql.connection.commit()
        flash("Data Successfully Updated")
        return redirect(url_for('account'))

# delete user data
@app.route('/accountdelete/<int:id>', methods=["GET"])
def accountdelete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customer WHERE id=%s", (id,))
    mysql.connection.commit()
    flash("Data Successfully Deleted")
    return redirect( url_for('account'))

#add staff
@app.route('/admin/addstaff')
def addstaff():
    if 'loggedin' in session:
        return render_template('pages/admin/addstaff.html')
    flash('Please Login first','danger')
    return redirect(url_for('login'))

#insert staff data
@app.route('/admin/staffinsert', methods=['POST'])
def staffinsert():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        address = request.form['address']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO staff (name, email, phone, dob, address) VALUES (%s, %s, %s, %s, %s)", (name, email, phone, dob, address))
        mysql.connection.commit()
        flash("Data sent successfully")
        return redirect(url_for('addstaff'))

#show staff data
@app.route('/staffdata')
def staffdata():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM staff ORDER BY staff_id DESC")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('pages/admin/staffdata.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))

#update Staff data
@app.route('/staffupdate', methods=['POST'])
def staffupdate():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        address = request.form['address']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE staff SET name=%s, email=%s, phone=%s, dob=%s, address=%s WHERE staff_id=%s", 
        (name, email, phone, dob, address, staff_id))
        mysql.connection.commit()
        flash("Data successfully Updated")
        return redirect(url_for('staffdata'))

#addroom
@app.route('/admin/addroom')
def addroom():
    if 'loggedin' in session:
        return render_template('pages/admin/addroom.html')
    flash('Please Login first','danger')
    return redirect(url_for('login'))
    

#insert room data
@app.route('/admin/roominsert', methods=['POST'])
def roominsert():
    if request.method == 'POST':
        nor = request.form['nor']
        roomtype = request.form['roomtype']
        roomprice = request.form['roomprice']
        roomconfig = request.form['roomconfig']
        img = request.form['img']
        img_detail = request.form['img_detail']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO room_config (nor, roomtype, roomprice, roomconfig, img, img_detail ) VALUES (%s, %s, %s, %s, %s, %s)", (nor, roomtype, roomprice, roomconfig, img, img_detail))
        mysql.connection.commit()
        flash("Data sent successfully")
        return redirect(url_for('addroom'))


#show room data
@app.route('/roomdata')
def roomdata():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM room_config ORDER BY roomid DESC")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('pages/admin/roomdata.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))

#update room data
@app.route('/roomupdate', methods=['POST'])
def roomupdate():
    if request.method == 'POST':
        roomid = request.form['roomid']
        nor = request.form['nor']
        roomtype = request.form['roomtype']
        roomprice = request.form['roomprice']
        roomconfig = request.form['roomconfig']
        img = request.form['img']
        img_detail = request.form['img_detail']
        status = request.form['status']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE room_config SET nor=%s, roomtype=%s, roomprice=%s, roomconfig=%s, img=%s, img_detail=%s, status=%s WHERE roomid=%s", 
        (nor, roomtype, roomprice, roomconfig, img, img_detail, status, roomid))
        mysql.connection.commit()
        flash("Data successfully Updated")
        return redirect(url_for('roomdata'))

#delete room data
@app.route('/roomdelete/<int:id>', methods=["GET"])
def roomdelete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM room_config WHERE roomid=%s", (id,))
    mysql.connection.commit()
    flash("Data Successfully Deleted")
    return redirect( url_for('roomdata'))

#add facility
@app.route('/addfacility')
def addfacility():
    if 'loggedin' in session:
        return render_template('pages/admin/addfacility.html')
    flash('Please Login first','danger')
    return redirect(url_for('login'))
    

#insert facility data
@app.route('/facilityinsert', methods=['POST'])
def facilityinsert():
    if request.method == 'POST':
        f_name = request.form['f_name']
        f_info = request.form['f_info']
        f_price = request.form['f_price']
        f_img = request.form['f_img']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO facility_config (f_name, f_info, f_price, f_img) VALUES (%s, %s, %s, %s)", (f_name, f_info, f_price, f_img))
        mysql.connection.commit()
        flash("Data sent successfully")
        return redirect(url_for('addfacility'))

#show facility data
@app.route('/facilitydata')
def facilitydata():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM facility_config ORDER BY f_id DESC")
    datashow = cur.fetchall()
    cur.close()
    if 'loggedin' in session:
        return render_template('pages/admin/facilitydata.html', orderdata=datashow)
    flash('Please Login first','danger')
    return redirect(url_for('login'))
    

#update facility data
@app.route('/facilityupdate', methods=['POST'])
def facilityupdate():
    if request.method == 'POST':
        f_id = request.form['f_id']
        f_name = request.form['f_name']
        f_info = request.form['f_info']
        f_price = request.form['f_price']
        f_img = request.form['f_img']
        f_status = request.form['f_status']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE facility_config SET f_name=%s, f_info=%s, f_price=%s, f_img=%s, f_status=%s WHERE f_id=%s", 
        (f_name, f_info, f_price, f_img, f_status, f_id))
        mysql.connection.commit()
        flash("Data successfully Updated")
        return redirect(url_for('facilitydata'))

#delete facility data
@app.route('/facilitydelete/<int:id>', methods=["GET"])
def facilitydelete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM facility_config WHERE f_id=%s", (id,))
    mysql.connection.commit()
    flash("Data Successfully Deleted")
    return redirect( url_for('facilitydata'))


# ---
@app.route('/face-recon-home')
def facereconhome():
    cur = mysql.connection.cursor()
    cur.execute("select prs_nbr, prs_name, prs_skill, prs_active, prs_added, status from prs_mstr")
    data = cur.fetchall()
    cur.close()
    
    return render_template('pages/model/index_face.html', data=data)

@app.route('/addprsn')
def addprsn():
    mycursor.execute("select ifnull(max(prs_nbr) + 1, 101) from prs_mstr")
    row = mycursor.fetchone()
    nbr = row[0]
    # print(int(nbr))
    return render_template('pages/model/addprsn.html', newnbr=int(nbr))

@app.route('/addprsn_submit', methods=['POST'])
def addprsn_submit():
    prsnbr = request.form.get('txtnbr')
    prsname = request.form.get('txtname')
    prsskill = request.form.get('optskill')
 
    mycursor.execute("""INSERT INTO `prs_mstr` (`prs_nbr`, `prs_name`, `prs_skill`) VALUES
                    ('{}', '{}', '{}')""".format(prsnbr, prsname, prsskill))
    mydb.commit()
 
    # return redirect(url_for('home'))
    return redirect(url_for('vfdataset_page', prs=prsnbr))


@app.route('/vidfeed_dataset/<nbr>')
def vidfeed_dataset(nbr):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(generate_dataset(nbr), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(face_recognition(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/fr_page')
def fr_page():
    return render_template('pages/model/fr_page.html')

#------------------

# temp face
@app.route('/face-recon-temp-home')
def facerecontemphome():
    mycursor.execute("select prs_nbr, prs_name, prs_skill, prs_active, prs_added from prs_mstr_temp")
    data = mycursor.fetchall()
 
    return render_template('pages/model/index_face_temp.html', data=data)

@app.route('/addprsn_temp')
def addprsn_temp():
    mycursor.execute("select ifnull(max(prs_mstr_temp.prs_nbr) + 1, FLOOR(1 + (RAND() * 800))) from prs_mstr_temp ORDER BY prs_mstr_temp.prs_nbr DESC LIMIT 1")
    row = mycursor.fetchone()
    nbr = row[0]
    # print(int(nbr))
        
    return render_template('pages/model/addprsn_temp.html', newnbr=int(nbr))

@app.route('/addprsn_temp_submit', methods=['POST'])
def addprsn_temp_submit():
    prsnbr = request.form.get('txtnbr')
    prsname = request.form.get('txtname')
    prsskill = request.form.get('optskill')
 
    mycursor.execute("""INSERT INTO `prs_mstr_temp` (`prs_nbr`, `prs_name`, `prs_skill`) VALUES
                    ('{}', '{}', '{}')""".format(prsnbr, prsname, prsskill))

    mycursor.execute("""INSERT INTO `prs_mstr` (`prs_nbr`, `prs_name`, `prs_skill`) VALUES
                    ('{}', '{}', '{}')""".format(prsnbr, prsname, prsskill))
    
    

    mydb.commit()
 
    # return redirect(url_for('home'))
    return redirect(url_for('vfdataset_temp_page', prs=prsnbr))

@app.route('/vfdataset_temp_page/<prs>')
def vfdataset_temp_page(prs):
    return render_template('pages/model/gendataset_temp.html', prs=prs)

@app.route('/vidfeed_temp_dataset/<nbr>')
def vidfeed_temp_dataset(nbr):
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(generate_temp_dataset(nbr), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_temp')
def video_feed_temp():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(face_recognition_temp(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/fr_page_temp')
def fr_page_temp():
    return render_template('pages/model/fr_page_temp.html')


@app.route('/homwait')
def homewait():
    mycursor.execute("select prs_nbr, prs_name, prs_skill, prs_active, prs_added from prs_mstr_temp")
    data = mycursor.fetchall()
 
    return render_template('pages/model/homewait.html', data=data)

@app.route('/waitting_page')
def waitting_page():
    

    # auto_copy()
    auto_delete() 

    while True:
        schedule.run_pending()
        time.sleep(1)
        
    
    return render_template('addprsn_temp.html', newnbr=int(nbr))

#delete facility data
@app.route('/f_recon_user_del/<int:id>', methods=["GET"])
def f_recon_user_del(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM prs_mstr WHERE prs_nbr=%s", (id,))
    mysql.connection.commit()
    flash("Data Successfully Deleted")
    return redirect( url_for('facereconhome'))

#update face recon checkout
@app.route('/update_checkout', methods=['POST'])
def update_checkout():
    if request.method == 'POST':
        prs_nbr = request.form['prs_nbr']
        nprs_name = request.form['prs_name']
        status = request.form['status']     
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE prs_mstr SET prs_name=%s, status=%s WHERE prs_nbr=%s", 
        (nprs_name, status, prs_nbr))
        mysql.connection.commit()
        flash("Data successfully Updated")
        return redirect( url_for('facereconhome'))

#delete face recon data
@app.route('/facerecon_delete/<int:id>', methods=["GET"])
def facerecon_delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM room_config WHERE 	prs_nbr=%s", (id,))
    mysql.connection.commit()
    flash("Data Successfully Deleted")
    return redirect( url_for('facereconhome'))

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Train Classifier >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route('/train_classifier/<nbr>')
def train_classifier(nbr):
    dataset_dir = "dataset"
 
    path = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir)]
    faces = []
    ids = []
 
    for image in path:
        img = Image.open(image).convert('L');
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])
 
        faces.append(imageNp)
        ids.append(id)
    ids = np.array(ids)
 
    # Train the classifier and save
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("classifier.xml")
 
    return redirect('/face-recon-home')

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Train Classifier 2>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
@app.route('/train_classifier_temp/<nbr>')
def train_temp_classifier(nbr):
    dataset_dir = "dataset_temp"
 
    path = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir)]
    faces = []
    ids = []
 
    for image in path:
        img = Image.open(image).convert('L');
        imageNp = np.array(img, 'uint8')
        id = int(os.path.split(image)[1].split(".")[1])
 
        faces.append(imageNp)
        ids.append(id)
    ids = np.array(ids)
 
    # Train the classifier and save
    clf = cv2.face.LBPHFaceRecognizer_create()
    clf.train(faces, ids)
    clf.write("classifier_temp.xml")
 
    return redirect('/face-recon-temp-home')

if __name__ == '__main__':
    app.run(debug=True)
from flask_mail import Mail, Message
from flask import Flask

app = Flask(__name__)
mail = Mail(app)
app.config['MAIL_SERVER']   =   'smtp.gmail.com'
app.config['MAIL_PORT']     =   465
app.config['MAIL_USERNAME'] =   'thuanmai362001@gmail.com'
app.config['MAIL_PASSWORD'] =   'mdyzeiqsbnikeaiu' 
app.config['MAIL_USE_TLS']  =   False
app.config['MAIL_USE_SSL']  =   True
mail = Mail(app)
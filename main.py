# ---------------- CONFIG ----------------

from flask import Flask, render_template, redirect, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import py_functions, os, ast, json, calendar, schedule, time, threading
from datetime import date, datetime
import database

app = Flask(__name__)

app.config.update(DEBUG=True, SECRET_KEY=os.environ['flask_secret'])




# ---------------- LOGIN / LOGOUT ----------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# Login Page
@app.route("/login/", methods=["GET", "POST"])
def page_login():
    if current_user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        response = py_functions.get_user_data(username, password)
        if response != False:
            if response == 'PARENT':
                if request.user_agent.platform == 'iphone' or request.user_agent.platform == 'android':
                    return render_template('login.html', mobile=True, msg='Parents are not allowed to access the site')
                return render_template('login.html', msg='Parents are not allowed to access the site')
            user = User(id)
            login_user(user)
            name = response[0]
            user_name = response[1]
            response = str(json.dumps(response[2], ensure_ascii=False))
            session['name'] = name
            session['classes'] = response
            session['user_name'] = user_name
            return redirect('/dashboard/')
        else:
            if request.user_agent.platform == 'iphone' or request.user_agent.platform == 'android':
                return render_template('login.html', mobile=True, msg='Invalid Username or Password!')
            return render_template('login.html', msg='Invalid Username or Password!')
    else:
        if request.user_agent.platform == 'iphone' or request.user_agent.platform == 'android':
            return render_template('login.html', mobile=True)
        return render_template('login.html')


# Log Out
@app.route("/logout/")
def page_logout():
    if not current_user.is_authenticated:
        return redirect('/login')
    logout_user()
    try:
        session.pop('name')
    except:
        ...
    try:
        session.pop('classes')
    except:
        ...
    try:
        session.pop('user_name')
    except:
        ...
    return redirect('/login')

@app.route("/session/", methods=["GET", "POST"])
def page_temp_session():
    return session


# Login Manager Loader
@login_manager.user_loader
def load_user(userid):
    return User(userid)


# ---------------- PAGES----------------


# Survey
@app.route("/survey/", methods=["GET", "POST"])
def page_survey():
    if not current_user.is_authenticated:
        return redirect('/login')
    name = session.get('user_name')
    if database.check_user_survey(name) is False:
        return redirect('/takensurvey/')
    if request.method == 'POST':
        rq_form = dict(request.form)  # Retrieve form data
        s = ast.literal_eval(session.get('classes'))  # Retrieve cookie data
        t_f = list(rq_form.keys())
        for i in range(len(t_f)):
            t_f[i] = t_f[i][:-1]
        t_f = list(dict.fromkeys(t_f))
        t_s = []
        for i in s:
            t_s.append(i[1].replace(' ', ''))
        if t_f == t_s:  # Check if submitted form teachers == cookie classes
            database.addToDatabase(rq_form, session.get("user_name"))
            ml = database.createResults()
            return render_template('results.html', ratings=ml)
    else:
        ml = session.get('classes')
        name = session.get('name')
        ml = ast.literal_eval(ml)
        return render_template('survey.html', user_fullname=name, classes=ml)


# Dashboard
@app.route("/dashboard/")
def page_dashboard():
    if not current_user.is_authenticated:
        return redirect('/login')
    name = session['name']
    classes_output = session['classes']
    classes_output = ast.literal_eval(classes_output)
    platform = request.user_agent.platform
    if platform == 'iphone' or platform == 'android':
        return render_template('dashboard.html', user_fullname=name, classes=classes_output, mobile=True)
    return render_template('dashboard.html', user_fullname=name, classes=classes_output, c_css='login')


# Results Page
@app.route("/results/", methods=["GET", "POST"])
def page_result():
  ml = database.createResults()
  return render_template('results.html', ratings=ml)
        


# Main page - redirects
@app.route("/")
def page_home():
    if current_user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return redirect('/login/')

@app.route("/takensurvey/")
def page_takensurvey():
    curr_date = date.today()
    today = calendar.day_name[curr_date.weekday()]
    until_monday = 8 - datetime.today().isoweekday()
    return render_template('takenSurvey.html', a = today, until_monday = until_monday)


# 404 Not Found Page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


# SCHEDULING -------------------------


def recal_average(): 
    database.redefAverages()

def reset_survey():
    database.clearUsernames()



schedule.every(1).minutes.do(recal_average)
schedule.every().monday.at("08:00").do(reset_survey)


@app.before_first_request
def light_thread():
    def run():
        while True:
            schedule.run_pending()
            time.sleep(1)
    thread = threading.Thread(target=run)
    thread.start()


app.run(host='0.0.0.0', port=8080, threaded=True)
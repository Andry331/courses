import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = 'static\img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = 'ssss'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'

db = SQLAlchemy(app)

class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, unique=True, nullable=False)
    start_data = db.Column(db.Date,  nullable=False)
    finish_data = db.Column(db.Date, nullable=False)
    photo_src = db.Column(db.String(100))

    def __init__(self, **kwargs):
        super(Course, self).__init__(**kwargs)

    def __repr__(self):
        return '<Course %r>' % self.course_name    



@app.route('/', methods=['GET'])
def courses():
    all_courses = Course.query.all()
    search = request.args.get('search')
    if search:
        course_for_template = []
        search_list = search.split(' ')
        for course in all_courses:
            for word in search_list:
                if str(course.course_name).find(word) != -1 or str(course.description).find(word) != -1 or str(course.start_data).find(word) != -1 or str(course.finish_data).find(word) != -1:
                    if course in course_for_template:
                        continue
                    course_for_template.append(course)
        if bool(course_for_template) is False:
            flash('За вашим пошуковим запитом нічого не знайдено')
        else:
            flash('За ваши пошуковим запитом '+str(search)+ ' знайдено курсів '+str(len(course_for_template)))
        return render_template('courses.html', x=course_for_template)

    return render_template('courses.html', x=all_courses)


@app.route('/add_courses', methods=['POST', 'GET'])
def add_courses():
    if request.method == 'POST':
        if request.form['course_name']=='' or request.form['description']=='' or request.form['start_data']=='' or request.form['finish_data']=='' :
            flash('Заповніть всі поля')
            return render_template('add_courses.html')

        if 'file' not in request.files:
            flash('Помилка завантаження фото')
            return render_template('add_courses.html')

        file = request.files['file']
        
        if file.filename == '':
            flash('Виберіть фото')
            return render_template('add_courses.html')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        

        course_name_in_db = Course.query.filter_by(course_name = request.form['course_name']).first()
        description_in_db = Course.query.filter_by(course_name = request.form['description']).first()
        if course_name_in_db is None and description_in_db is None:
            added_course = Course(course_name = request.form['course_name'], description = request.form['description'], start_data = datetime.datetime.strptime(request.form['start_data'], '%Y-%m-%d').date(), finish_data = datetime.datetime.strptime(request.form['finish_data'], '%Y-%m-%d').date(),  photo_src = os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.session.add(added_course)  
            db.session.commit()
            return redirect(url_for('courses'))
        flash('Курс із такою назва або описом вже існує')
        return render_template('add_courses.html')

    else:
        return render_template('add_courses.html')


@app.route('/course/<course_id>')
def single_course(course_id = None):
    single_course = Course.query.get(course_id)
    return render_template('single_course.html', course = single_course)


@app.route('/course/<course_id>/delate')
def delate(course_id = None):

    course_for_delating = Course.query.get(course_id)
    db.session.delete(course_for_delating)
    db.session.commit()
    return  redirect(url_for('courses'))


@app.route('/course/<course_id>/red', methods=['POST', 'GET'])
def red(course_id = None):
    course_for_red = Course.query.get(course_id)
    if request.method == 'POST':
        if request.form['course_name']=='' or request.form['description']=='' or request.form['start_data']=='' or request.form['finish_data']=='' :
            flash('Заповніть всі поля')
            return render_template('single_course_red.html', course = course_for_red)
        course_for_red.course_name = request.form['course_name']
        course_for_red.description = request.form['description']
        course_for_red.start_data = datetime.datetime.strptime(request.form['start_data'], '%Y-%m-%d').date()
        course_for_red.finish_data = datetime.datetime.strptime(request.form['finish_data'], '%Y-%m-%d').date()
        db.session.commit()
       
        return redirect(url_for('single_course', course_id=course_id))
    
    return render_template('single_course_red.html', course = course_for_red)


if __name__ == '__main__':
    app.run()
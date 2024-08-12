from flask import Flask, render_template, request
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plates.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    db.init_app(app)

    # Define the plates model
    class Plate(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        plate_text = db.Column(db.String(100))

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Flask-Admin views
    class SearchView(BaseView):
        @expose('/')
        def index(self):
            return self.render('admin/search.html')

    class PlateModelView(ModelView):
        column_list = ('id', 'plate_text')

    admin = Admin(app, name='Admin', template_mode='bootstrap3')
    admin.add_view(PlateModelView(Plate, db.session))
    admin.add_view(SearchView(name='Search', endpoint='search'))

    @app.route('/')
    def query():
        return render_template('query.html')

    @app.route('/search', methods=['POST'])
    def search():
        plate_text = request.form['plate_text']
        results = Plate.query.filter(Plate.plate_text.like(f'{plate_text}%')).all()
        return render_template('results.html', results=results)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

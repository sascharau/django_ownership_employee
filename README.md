Example App with auth, owners, employees, permissions and api's. Try the demo, maybe the code can help you to get a quick start for your project.

Login with `john.doe@example.app` and `try3000` or you create you own account. 
https://example.ideal3000.de/

# Install
~~~~
git clone https://github.com/sascharau/django_ownership_employee.git
cd django_ownership_employee
virtualenv -p python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
cd ownership_employee
~~~~
now create ".env" file: (django_ownership_employee/ownership_employee/.env)
~~~~
SECRET_KEY="fsdfsdfsdf"
ALLOWED_HOSTS=['*']
DEBUG=True
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.email.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'my@email.com'
EMAIL_HOST_PASSWORD = 'password'
ADMINS=[('admin', admin@email.com')]
DJANGO_SETTINGS_MODULE=conf.settings
~~~~


# Start Django
~~~~
./manage.py migrate
./manage.py runserver
~~~~


# Create 100 User
~~~~
./manage.py user_generator
~~~~
Owner login: john.doe@example.app and try3000

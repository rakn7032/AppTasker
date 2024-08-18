# AppTasker

# Setup Instructions

1. Clone the Repository:
  git clone https://github.com/rakn7032/AppTasker.git

2. Create and Activate Virtual Environment:
  python -m venv venv

  # On Mac use:       source venv/bin/activate 
  # On Windows use:   venv\Scripts\activate

3. Install Dependencies:
  pip install -r requirements.txt

4. Create the PostgreSQL Database:
  ```plaintext
    DATABASES = {
      'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': <db name>,
        'USER': <db user>,
        'PASSWORD': <password>,
        'HOST': '127.0.0.1',
        'PORT': '5432',
      }
    }
  
5. Email Configuration:
  ```plaintext
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = 'smtp.gmail.com'
    DEFAULT_FROM_EMAIL = # your mail
    EMAIL_HOST_USER = # your mail
    EMAIL_HOST_PASSWORD = # your App password
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

7. Apply Migrations:

  • python manage.py makemigrations
  • python manage.py migrate


# Api Endpoints

Access all API endpoints through the Postman collection link below. This collection provides comprehensive API documentation, including details on requests, responses, exceptions, and additional notes for each endpoint.

Postman Collection Link: https://documenter.getpostman.com/view/37485860/2sA3s9CneA

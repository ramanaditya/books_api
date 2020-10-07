Books API
=========

API for the books on Amazon and Google

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style


:License: MIT


Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Your Users
^^^^^^^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ python3 -m pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html


Sentry
^^^^^^

Sentry is an error logging aggregator service. You can sign up for a free account at  https://sentry.io/signup/?code=cookiecutter  or download and host it yourself.
The system is setup with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.


Deployment
----------

The following details how to deploy this application.


API Endpoints
^^^^^^^^^^^^^^

Requests
---------
+-------------------+-----------+-------------------------------+-----------+
| endpoint          | methods   | parameters                    | Required  |
+===================+===========+===============================+===========+
| ``/amazonbooks``  | ``GET``   | q=<Book Title>                | True      |
|                   |           +-------------------------------+-----------+
|                   |           | pages=<No of pages to scrap>  | False     |
|                   |           +-------------------------------+-----------+
|                   |           | count=<Count of result>       | False     |
+-------------------+-----------+-------------------------------+-----------+
| ``/googlebooks``  | ``GET``   | q=<Book Title>                | True      |
+-------------------+-----------+-------------------------------+-----------+

Response
----------

``/amazonbooks``
-----------------

.. code-block:: json

    {
        "status_code": 200,
        "body":
        [
            {
                "title": "The Alchemist, 25th Anniversary: A Fable About Following Your Dream",
                "url": "/Alchemist-Paulo-Coelho/dp/0062315005/ref=sr_1_1?dchild=1&keywords=The+Alchemist&qid=1602088322&sr=8-1",
                "ISBN_10": "0062315005",
                "ISBN_13": "978-0062315007"
            },
        ]
    }


``/googlebooks``
------------------

.. code-block:: json

    {
        "status_code": 200,
        "body":
        [
            {
                "title": "The Alchemist",
                "ISBN_13": "9780062416216",
                "ISBN_10": "0062416219"
            },
        ]
    }


Invoking API endpoints
^^^^^^^^^^^^^^^^^^^^^^^

``curl``
----------

.. code-block:: bash

    curl -X GET http://127.0.0.1:8000/api/googlebooks/?q=The%20Alchemist -H 'Authorization: Token <Token>'

``http``
---------

.. code-block:: bash

    http GET http://127.0.0.1:8000/api/googlebooks/?q=The%20Alchemist 'Authorization: Token <Token>'

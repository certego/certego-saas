Welcome to ``certego-saas`` !
================================

Directory Structure
---------------------

.. code-block:: console
  :emphasize-lines: 1, 12

   apps/                             optional/extra apps
   |- auth/                          "certego_saas.apps.auth" app (optional)
   |  |- backend.py                  authentication backend
   |- feedback/                      "certego_saas.apps.feedback" app (optional)
   |- notifications/                 "certego_saas.apps.notifications" app (optional)
   |- organization/                  "certego_saas.apps.organization" app (not exactly optional)
   |  |- mixins.py                   viewset mixin classes
   |  |- permissions.py              viewset permission classes
   |- payments/                      "certego_saas.apps.payments" app (optional)
   |  |- consts.py                   stripe related constant values
   |  |- utils.py                    utility functions to fetch products data from stripe
   ext/                              extensions to django/django-rest-framework
   |- upload/                        slack, twitter, etc. clients
   migrations/                       migrations for "certego_saas" app
   templates/
   |- certego_saas/                  E-mail templates
   |- context_processors.py          custom context processor
   user/                             User model, UserAccessSerializer serializer, etc.
   apps.py                           "certego_saas" app
   models.py                         default models
   settings.py                       default settings/configurations
   urls.py                           default url patterns
   version.py                        package version


.. toctree::
   :maxdepth: 2
   :glob:
   :caption: apps

   apps/index.rst
   user

.. toctree::
   :maxdepth: 2
   :glob:
   :caption: ext

   ext/index.rst


Indices and tables
================================

* :ref:`genindex`
* :ref:`modindex`
# -*- encoding: utf-8 -*-

import sys
from datetime import datetime

VERSION = (2, 5, 5)

default_app_config = "dbmail.apps.DBMailConfig"


def get_version():
    return ".".join(map(str, VERSION))


def app_installed(app):
    from django.conf import settings

    return app in settings.INSTALLED_APPS


def celery_supported():
    try:
        import celery

        return True
    except ImportError:
        return False


def db_sender(slug, recipient, *args, **kwargs):
    from dbmail.defaults import (
        BACKEND,
        CELERY_QUEUE,
        DEBUG,
        ENABLE_CELERY,
        SEND_MAX_TIME,
    )
    from dbmail.models import MailTemplate

    args = (slug, recipient) + args
    send_after = kwargs.pop("send_after", None)
    send_at_date = kwargs.pop("send_at_date", None)
    _use_celery = kwargs.pop("use_celery", ENABLE_CELERY)
    use_celery = ENABLE_CELERY and _use_celery
    backend = kwargs.get("backend", BACKEND["mail"])

    if celery_supported() and use_celery is True:
        import dbmail.tasks

        template = MailTemplate.get_template(slug=slug)
        max_retries = kwargs.get("max_retries", None)
        send_after = send_after if send_after else template.interval
        if max_retries is None and template.num_of_retries:
            kwargs["max_retries"] = template.num_of_retries

        options = {
            "args": args,
            "kwargs": kwargs,
            "queue": kwargs.pop("queue", CELERY_QUEUE),
            "time_limit": kwargs.get("time_limit", SEND_MAX_TIME),
            "priority": template.priority,
        }

        if send_at_date is not None and isinstance(send_at_date, datetime):
            options.update({"eta": send_at_date})
        if send_after is not None:
            options.update({"countdown": send_after})
        if template.is_active:
            return dbmail.tasks.db_sender.apply_async(**options)
    else:
        module = import_module(backend)
        if DEBUG is True:
            return module.SenderDebug(*args, **kwargs).send(is_celery=False)
        return module.Sender(*args, **kwargs).send(is_celery=False)


def send_db_mail(*args, **kwargs):
    from dbmail.defaults import BACKEND

    kwargs["backend"] = kwargs.pop("backend", BACKEND["mail"])
    return db_sender(*args, **kwargs)


def send_db_sms(*args, **kwargs):
    from dbmail.defaults import BACKEND, SMS_QUEUE

    kwargs["backend"] = kwargs.pop("backend", BACKEND["sms"])
    kwargs["queue"] = kwargs.pop("queue", SMS_QUEUE)
    return db_sender(*args, **kwargs)


def send_db_tts(*args, **kwargs):
    from dbmail.defaults import BACKEND, TTS_QUEUE

    kwargs["backend"] = kwargs.pop("backend", BACKEND["tts"])
    kwargs["queue"] = kwargs.pop("queue", TTS_QUEUE)
    return db_sender(*args, **kwargs)


def send_db_push(*args, **kwargs):
    from dbmail.defaults import BACKEND, PUSH_QUEUE

    kwargs["backend"] = kwargs.pop("backend", BACKEND["push"])
    kwargs["queue"] = kwargs.pop("queue", PUSH_QUEUE)
    return db_sender(*args, **kwargs)


def send_db_bot(*args, **kwargs):
    from dbmail.defaults import BACKEND, BOT_QUEUE

    kwargs["backend"] = kwargs.pop("backend", BACKEND["bot"])
    kwargs["queue"] = kwargs.pop("queue", BOT_QUEUE)
    return db_sender(*args, **kwargs)


def send_db_subscription(*args, **kwargs):
    from dbmail.defaults import (
        ENABLE_CELERY,
        MAIL_SUBSCRIPTION_MODEL,
        SEND_MAX_TIME,
        SUBSCRIPTION_QUEUE,
    )

    MailSubscription = import_by_string(MAIL_SUBSCRIPTION_MODEL)

    use_celery = ENABLE_CELERY and kwargs.pop("use_celery", ENABLE_CELERY)
    options = {
        "time_limit": kwargs.pop("time_limit", SEND_MAX_TIME),
        "queue": kwargs.pop("queue", SUBSCRIPTION_QUEUE),
        "args": args,
        "kwargs": kwargs,
    }

    if celery_supported() and use_celery is True:
        from dbmail.tasks import db_subscription

        return db_subscription.apply_async(**options)
    else:
        kwargs["use_celery"] = use_celery
        return MailSubscription.notify(*args, **kwargs)


def initial_signals():
    from django.db.utils import DatabaseError, IntegrityError

    for cmd in [
        "schemamigration",
        "migrate",
        "test",
        "createsuperuser",
        "makemigrations",
        "collectstatic",
        "compilemessages",
    ]:
        if cmd in sys.argv:
            break
    else:
        try:
            from dbmail.signals import initial_signals as init_signals

            init_signals()
        except (ImportError, DatabaseError, IntegrityError):
            pass


##
# Compatibility section
##

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.
    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if PY2:
        if "__str__" not in klass.__dict__:
            raise ValueError(
                "@python_2_unicode_compatible cannot be applied "
                "to %s because it doesn't define __str__()." % klass.__name__
            )
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode("utf-8")
    return klass


def import_by_string(dotted_path):
    """Import class by his full module path.

    Args:
        dotted_path - string, full import path for class.

    """
    from django.utils.module_loading import import_string

    return import_string(dotted_path)


def import_module(*args, **kwargs):
    try:
        from django.utils.importlib import import_module
    except ImportError:
        from importlib import import_module
    return import_module(*args, **kwargs)


def get_model(*args, **kwargs):
    from django.apps import apps

    return apps.get_model(*args, **kwargs)

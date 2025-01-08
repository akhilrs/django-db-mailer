from setuptools import find_packages, setup

from dbmail import get_version

setup(
    name="django-db-mailer",
    version=get_version(),
    description="Django module to easily send emails using django templates stored in a database.",
    keywords="django db mail email html text tts sms push templates mailer",
    long_description=open("README.rst", encoding="utf-8", errors="ignore").read(),
    long_description_content_type="text/x-rst",
    author="0x1235",
    author_email="other@ars.vg",
    url="http://github.com/akhilrs/django-db-mailer/",
    packages=find_packages(exclude=["demo"]),
    package_data={
        "dbmail": [
            "locale/*/LC_MESSAGES/django.*",
            "static/dbmail/admin/js/*.js",
            "fixtures/*.json",
        ]
    },
    include_package_data=True,
    python_requires=">=3.8",  # Specify minimum Python version
    install_requires=[
        "django>=3.2",  # Specify minimum Django version
        "setuptools",
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

from setuptools import setup, find_namespace_packages
from update_cache.version import Version


setup(name='django-update-cache',
     version=Version('1.0.2').number,
     description='Lazy cache updates for Django',
     long_description=open('README.md').read().strip(),
     long_description_content_type="text/markdown",
     author='Bram Boogaard',
     author_email='padawan@hetnet.nl',
     url='https://github.com/bboogaard/django-update-cache',
     packages=find_namespace_packages(
         include=[
             'update_cache',
             'update_cache.cache',
             'update_cache.migrations'
         ]
     ),
     include_package_data=True,
     install_requires=[
         'django~=4.2.7',
         'django-rq~=2.8.1',
     ],
     license='MIT License',
     zip_safe=False,
     keywords='Django Update cache',
     classifiers=['Development Status :: 3 - Alpha'])

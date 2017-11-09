from setuptools import setup, find_packages

requires = [
]

setup(
    name='injectpy',
    version='0.0.1',
    description='dependency injection utilities and service container',
    url='https://github.com/edudobay/injectpy',
    author='Eduardo Dobay',
    author_email='edudobay@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=requires,
    packages=find_packages(exclude=['*.tests']),
)

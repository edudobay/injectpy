from setuptools import setup, find_packages
from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)

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
    setup_requires=[
        'pipenv',
    ],
    install_requires=requirements,
    tests_require=test_requirements,
    packages=find_packages(exclude=['*.tests']),
)

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='tictactoe',
    version='0.1.0',
    description='TicTacToe challenge',
    long_description=readme,
    author='Aleksandr Krymer',
    author_email='akrymer@gmail.com',
    packages=find_packages(exclude=('tests', 'docs'))
)


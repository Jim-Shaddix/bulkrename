from setuptools import setup
"""
    install using: pip install --editable .
"""

setup(
    name="bulkrename",
    version='1.0',
    py_modules=['bulkrename','Valid_Path'],
    install_requires=['Click'],
    entry_points = '''
        [console_scripts]
        bulkrename=bulkrename:cli
    ''',
)
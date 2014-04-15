from distutils.core import setup
setup(
    name='ground_control',
    version='0.1',
    author='Shane Gianelli',
    author_email='shanejgianelli@gmail.com',
    packages=['ground_control', 'ground_control.major_tom'],
    install_requires=[
        'psycopg2>=2.5.2,<3.0',
        'msgpack-python==0.4.2',
        'pyzmq>=14.0.01,<15'
    ]
)

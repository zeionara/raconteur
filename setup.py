from setuptools import setup


def get_readme():
    with open('README.md', 'r', encoding = 'utf-8') as file:
        return file.read()


setup(
    name = 'raconteur',
    packages = ['rr'],
    version = '0.1',
    license = 'Apache 2.0',
    description = 'An auxiliary app for simplifying speech synthesis on arbitrary texts',
    long_description = get_readme(),
    author = 'Zeio Nara',
    author_email = 'zeionara@gmail.com',
    url = 'https://github.com/zeionara/raconteur',
    keywords = ['speech', 'synthesis'],
    install_requires = [
        'ipython', 'scipy', 'pydub', 'music-tag', 'numpy', 'git+https://github.com/suno-ai/bark.git'
    ],
    classifiers = [
        'Programming Language :: Python :: 3.11'
    ]
)

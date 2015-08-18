import setuptools

setuptools.setup(
    name="builddiff",
    version="0.1.0",
    url="https://github.com/andriykohut/builddiff",

    author="Andriy Kogut",
    author_email="kogut.andriy@gmail.com",

    description="Compate console output of Jenkins builds",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=['PyYAML', 'colorama', 'requests'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    entry_points={
        'console_scripts': [
            'bdiff=builddiff.cli:main',
        ],
    },
)

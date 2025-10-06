from setuptools import setup, find_packages

setup(
    name='journal-abbreviation-gui',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyperclip',
        'pyyaml',
        'tkinter',  # Assuming tkinter is used for the GUI
    ],
    entry_points={
        'console_scripts': [
            'journal-abbreviation-gui=main:main',  # Adjust according to the main function in main.py
        ],
    },
)
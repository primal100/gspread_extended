from distutils.core import setup

setup(
        name='gspread_extended',
        version='0.1',
        packages=['example'],
        url='https://github.com/primal100/gspread_extended',
        license='MIT',
        author='Paul Martin',
        author_email='paul_martin100@hotmial.com',
        keywords=['gspread', 'spreadsheets', 'google-spreadsheets'],
        description='Extra methods for GSpread: Google Spreadsheets Python API',
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Science/Research",
            "Topic :: Office/Business :: Financial :: Spreadsheet",
            "Topic :: Software Development :: Libraries :: Python Modules"
            ],
        install_requires=['gspread', 'oauth2client'],
)

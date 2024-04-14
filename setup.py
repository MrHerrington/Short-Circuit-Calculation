from setuptools import setup, find_packages

setup(
    name='short',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'get_db = ShortCircuitCalc.install: installer',
            'get_res = ShortCircuitCalc.run: main',
        ],
    },
)

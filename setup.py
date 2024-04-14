from setuptools import setup

setup(
    name='shortcircuitcalc',
    version='1.0',
    entry_points={
        'console_scripts': [
            'get_db = ShortCircuitCalc.install: installer',
            'get_res = ShortCircuitCalc.run: main',
        ],
    },
)

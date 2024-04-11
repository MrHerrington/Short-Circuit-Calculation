from setuptools import setup

setup(
    name='shortcircuitcalc',
    version='1.0',
    entry_points={
        'console_scripts': [
            'get_shortcircuit = ShortCircuitCalc.tools.elements:Calculator',
        ],
    },
)

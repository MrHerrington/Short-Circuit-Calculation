from setuptools import setup

setup(
    name='shortcircuitcalc',
    version='1.0',
    include_package_data=True,
    exclude_package_data={'': ['*.json']},
    entry_points={
        'console_scripts': [
            'get_install = ShortCircuitCalc.install: installer',
            'get_res = ShortCircuitCalc.run: main',
        ],
    },
)

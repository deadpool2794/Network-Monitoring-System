from setuptools import setup, find_packages

setup(
    name="web-activity-tracker",
    version="0.1",
    packages=find_packages(),      # picks up browser_history
    install_requires=[
        "requests",                # add any other PyPI libs you use
    ],
    entry_points={
        "console_scripts": [
            # this lets users run `web-activity-tracker` on the command line
            "web-activity-tracker = web_activity_tracker:main",
        ],
    },
)
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='spotled-bleak',
    version='1.0.0',
    author="Praful Mathur",
    author_email="praful@sarama.app",
    description="Allows control of SPOTLED bluetooth led displays via Python bleak library for Mac OS. (Fork of iwalton3/python-spotled)",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iwalton3/python-spotled",
    packages=find_packages(),  # Automatically find packages
    extras_require={
        'bleak': [
            'bleak',
        ],
        'gattlib': [
            'gattlib',
        ],
        'all': [
            'bleak',
            'gattlib',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=['bleak'],
    include_package_data=True,
    package_data={
        "spotled_bleak": ["fonts/*.yaff"],
    },
)


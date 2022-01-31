import setuptools

with open('requirements.txt', 'r') as rf:
    requirements = rf.read().splitlines()

setuptools.setup(
    name="ana",
    version="0.0.3",
    author="Rendered AI, Inc",
    author_email="info@rendered.ai",
    description="Ana Synthetic Data Generator",
    url="https://rendered.ai",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX",
    ],
    python_requires='>=3.7'
)

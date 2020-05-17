import setuptools

with open("README.md") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.readlines()

setuptools.setup(
    name="yukari",
    version="0.0.1",
    author="kat witch",
    author_email="kat@kittywit.ch",
    description="The upload API component of the Yakumo Chat System.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kittywitch/yakumo",
    packages=setuptools.find_packages(),
    package_dir={'yukari': 'yukari'},
    package_data={
        'chen': ['files/*']
    },
    entry_points={
        'console_scripts': [
            'yukari = yukari.app:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Communications :: Chat",
        "Development Status :: 4 - Beta",
        "Framework :: Twisted"
    ],
    install_requires=requirements,
    zip_safe=False,
    python_requires='>=3.8'
)

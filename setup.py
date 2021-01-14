from setuptools import setup


setup(
    name='ubercoordinator',
    version='0.1',
    install_requires=open('requirements.txt').readlines(),
    package_dir={"":"src"},
    packages=["ubercoordinator"],
    python_requires='>=3.7',
    url='',
    license='',
    author='glyn',
    author_email='glynwebster9@gmail.com',
    description="Tools to manage the Big Book of Key and produce static "
                "websites, ebooks and print books. This is the successor "
                "to 'Grease Pencil'."
)

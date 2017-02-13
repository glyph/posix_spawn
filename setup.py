from setuptools import find_packages, setup

setup(
    name="posix_spawn",
    version="0.1",
    description="CFFI bindings to posix_spawn.",
    license="MIT",

    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["src/_cffi_src/_build.py:maker"],

    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,

    install_requires=["cffi>=1.0.0"],

    zip_safe=False,
)

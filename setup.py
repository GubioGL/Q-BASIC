from setuptools import setup, find_packages

setup(
    name='Q-Basic',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'tqdm==4.67.1',
        'sympy==1.13.1',
        'torch==2.5.1+cu118',
        'scipy==1.14.1'
    ],
    author='Gubio Gomes de lima',
    author_email='gubiofisikal@gmail.com',
    description='Q-BASIC (Quantum Brazilian Algorithms, Simulations, and Computational tools)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/GubioGL/Q-Basic',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10.16',
)
from distutils.core import setup
import treepace.__version__

setup(name='Treepace',
      version=treepace.__version__,
      description='Tree Transformation Language',
      author='Matúš Sulír',
      url='https://github.com/sulir/treepace',
      packages=['treepace']
     )
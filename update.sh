echo "clearing the build dist and egg-info directory ... "
rm -rf .eggs build dist src/*.egg-info

echo "generating the whl file ... "
python setup.py bdist_wheel

echo "uninstalling old version ... "
pip uninstall -y DART

echo "installing new version ... "
pip install dist/*.whl

echo "clearing the build dist and egg-info directory ... "
rm -rf .eggs build dist src/*.egg-info

echo "showing the information of kis ... "
pip show DART

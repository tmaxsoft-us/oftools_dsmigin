#================================================================#
#                   INITIALIZATION                               #
#================================================================#
init:
	pip3 install -r requirements.txt

init_user:
	pip3 install -r requirements.txt --user

#================================================================#
#                   BUILD AND REMOVE                             #
#================================================================#
build:
	python3 setup.py sdist

remove:
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info

#================================================================#
#                   INSTALLATION                                 #
#================================================================#

# Default
install:
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl
uninstall:
	pip3 uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
reinstall:
	pip3 uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl

# User
install_user:
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl --user
uninstall_user:
	pip3 uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
reinstall_user:
	pip3 uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl --user

# Other Python command
install_diff:
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl
uninstall_diff:
	python3 -m pip uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
reinstall_diff:
	python3 -m pip uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl

# User & other Python command
install_user_diff:
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl --user
uninstall_user_diff:
	python3 -m pip uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
reinstall_user_diff:
	python3 -m pip uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl --user

#================================================================#
#                   TESTING                                      #
#================================================================#
test_func:
	pytest --color=yes --durations=5 -v -c tests/pytest.ini tests/functional/

test_unit:
	pytest --color=yes --durations=5 -v -c tests/pytest.ini tests/unit/
# Optional arguments:
# --maxfail = <num> : Stop test suite after n test failures

coverage:
	coverage run --source=oftools_compile -m pytest --color=yes -v -s
	coverage report --show-missing

#================================================================#
#                   PyPI UPLOADING                               #
#================================================================#
upload:
	python3 setup.py sdist upload -r pypi

upload_test:
	python3 setup.py sdist upload -r testpypi

remove_pypi:
	curl --form ":action=remove_pkg" --form "name=oftools-dsmigin" --form "version=0.0.1" URL -u id:pass

#================================================================#
#                   FORMATTING                                   #
#================================================================#
yapf:
	yapf3 --style='{ based_on_style: google }' *.py -ir
	
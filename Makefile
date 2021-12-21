init:
	pip3 install -r requirements.txt

init_user:
	pip3 install -r requirements.txt --user

build:
	python3 setup.py sdist

remove:
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info

install:
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl

install_user:
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl --user

install_diff:
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl

install_user_diff:
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl --user

uninstall:
	pip3 uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info

uninstall_diff:
	python3 -m pip uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info

reinstall:
	pip3 uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl

reinstall_diff:
	python3 -m pip uninstall -y oftools-dsmigin
	rm -r AUTHORS build ChangeLog dist oftools_dsmigin.egg-info
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl

upload:
	python3 setup.py sdist upload -r pypi

upload_test:
	python3 setup.py sdist upload -r testpypi

remove_pypi:
	curl --form ":action=remove_pkg" --form "name=oftools-dsmigin" --form "version=0.0.1" URL -u id:pass

yapf:
	yapf3 --style='{ based_on_style: google }' *.py -ir

test:
	pytest --color=yes -v -c tests/pytest.ini tests/unit/
# Optional arguments:
# --maxfail = <num> : Stop test suite after n test failures

coverage:
	coverage run --source=oftools_dsmigin -m pytest --color=yes -v -s
	coverage report
	
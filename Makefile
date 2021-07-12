init:
	pip3 install -r requirements.txt

build:
	python3 setup.py sdist

install:
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl

install_user:
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl --user

uninstall:
	rm -r build dist oftools_dsmigin.egg-info
	pip3 uninstall -y oftools-dsmigin

reinstall:
	rm -r build dist oftools_dsmigin.egg-info
	pip3 uninstall -y oftools-dsmigin
	python3 setup.py bdist_wheel
	pip3 install dist/*.whl

upload:
	python3 setup.py sdist upload -r pypi

upload_test:
	python3 setup.py sdist upload -r testpypi

remove:
	curl --form ":action=remove_pkg" --form "name=oftools-dsmigin" --form "version=0.0.1" URL -u id:pass

yapf:
	yapf3 --style='{ based_on_style: google }' *.py -ir

test:
	pytest --color=yes -v -c tests/pytest.ini tests/unit/

coverage:
	coverage run --source=oftools_compile -m pytest --color=yes -v -s
	coverage report
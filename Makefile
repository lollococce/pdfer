
init:
	pip install -r requirements.txt

test:
	py.test tests

publish:
	rm -rf dist/* && rm -rf pdfer.egg-info/* && python3 setup.py sdist && twine upload --skip-existing dist/*

push:
	git add . && git commit -m "update" && git push origin main

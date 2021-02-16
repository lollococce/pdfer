
init:
	sudo apt-get update && sudo apt-get install -y poppler-utils && echo -e 'Y' | sudo apt-get install ffmpeg libsm6 libxext6  -y && echo -e 'Y' | sudo apt install libgl1-mesa-glx && echo -e 'Y' | sudo apt-get install tesseract-ocr && pip install -r requirements.txt

test:
	py.test tests

publish:
	rm -rf dist/* && rm -rf pdfer.egg-info/* && python3 setup.py sdist && twine upload --skip-existing dist/*

push:
	git add . && git commit -m "update" && git push origin main

ship:
	git add . && git commit -m "update" && git push origin main && rm -rf dist/* && rm -rf pdfer.egg-info/* && python3 setup.py sdist && twine upload --skip-existing dist/*

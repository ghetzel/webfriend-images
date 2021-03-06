.PHONY: test deps docs build shell clean

all: env deps build docs

deps:
	./env/bin/pip install -q -r 'test-requirements.txt'
	./env/bin/pip install -q -r 'requirements.txt'

env:
	virtualenv --distribute env

shell:
	./env/bin/ipython

build:
	./env/bin/pip install -e .

test:
	./env/bin/flake8
	./env/bin/py.test -v

clean:
	-rm -rf env *.egg-info build dist
	find . -type f -name "*.pyc" -delete

docs:
	./env/bin/webfriend --generate-docs --only-document-plugins --omit-header --plugins image > docs/commands.md

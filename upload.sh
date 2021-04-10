#!/bin/bash
rm -rf ./dist
rm -rf ./build
python3 setup.py sdist bdist_wheel && twine upload -r nexus dist/*
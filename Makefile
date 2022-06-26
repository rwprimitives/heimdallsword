#
# Tells make that we are using spaces instead of tabs
# REF: 
#   Special Variables in Make
#   https://www.gnu.org/software/make/manual/html_node/Special-Variables.html
#
.RECIPEPREFIX +=

# Get the name of the package from the setup.cfg file
PACKAGE := $(shell cat setup.cfg | grep -E "^name\s*=\s*([^']*)" | cut -d "=" -f2 | xargs)


.PHONY: all clean help html test

all: build-pip

build-pip:
    python3 -m build .

build-deb:
    python3 setup.py --command-packages=stdeb.command bdist_deb

install-pip: build-pip
    python3 -m pip install .

install-deb: build-deb
    sudo dpkg -i deb_dist/python3-${PACKAGE}*.deb

uninstall-pip:
    pip uninstall ${PACKAGE} -y

uninstall-deb:
    sudo dpkg -r python3-${PACKAGE}

html:
    $(MAKE) -C docs/ html

test:
    @cd tests && `./run_test.sh`

clean:
    rm -rf build
    rm -rf docs/build
    rm -rf *.egg-info
    rm -rf */*.egg-info
    rm -rf deb_dist
    rm -rf dist
    rm -rf *.gz
    rm -f good_recipients.txt bad_recipients.txt metrics.txt *.log
    find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
    $(MAKE) -C docs/ clean

help:
    @echo "The following build targets are available:"
    @echo ""
    @echo "build-pip:     Generates a PIP distributions packages (ie: *.whl and *.tar.gz)"
    @echo "build-deb:     Generates a Debian Linux distribution package (ie: *.deb)"
    @echo "install-pip:   Builds and installs PIP distribution package"
    @echo "install-deb:   Builds and installs Debian distribution package"
    @echo "uninstall-pip: Uninstalls PIP distribution package"
    @echo "uninstall-deb: Uninstalls Debian distribution package"
    @echo "html:          Builds the HTML version of the docs"
    @echo "test:          Run unit test script"
    @echo "clean:         Removes any automatically generated files"
    @echo  ""

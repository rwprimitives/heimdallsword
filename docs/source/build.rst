Build
=====

This section covers several build aspects of the **HeimdallSword** project. 


Required Debian Packages
------------------------

The following packages are required:

.. list-table::
   :header-rows: 1

   * - Dependency
     - Version
   * - debhelper
     - 12.10ubuntu1
   * - dh-python
     - 4.20191017ubuntu7
   * - make
     - 4.2.1
   * - python3-all
     - 3.8.2-0ubuntu2
   * - python3-venv
     - 3.8.2-0ubuntu2
   * - python3-setuptools
     - 45.2.0-1


Copy and paste the following command on your terminal:

.. code-block:: console

    sudo apt install debhelper dh-python make python3-all python3-venv python3-setuptools


Required PyPi Packages
----------------------

The following PyPi packages are required:

.. list-table::
   :header-rows: 1

   * - Dependency
     - Version
     - Purpose
   * - build
     - 0.7.0
     - Used to build Python distribution package
   * - stdeb
     - 0.10.0
     - Used to build Debian source package


Copy and paste the following command on your terminal:

.. code-block:: console

    pip install build stdeb


Optional PyPi Packages
----------------------

The following PyPi packages are optional to install:

.. list-table::
   :header-rows: 1

   * - Dependency
     - Version
     - Purpose
   * - flake8
     - 4.0.1
     - Used for checking code style
   * - sphinx_rtd_theme
     - 4.4.0
     - Used for generating documentation


Copy and paste the following command on your terminal:

.. code-block:: console

    pip install flake8 sphinx_rtd_theme


Build Targets
-------------

Once all of the required dependencies have been installed, **HeimdallSword** provides several build targets that make it easier to build and deploy.

To view the build targets supported, run the command `make help` as such:

.. code-block:: console

    $ make help

    The following build targets are available:
    
    build-pip:     Generates a PIP distributions packages (ie: *.whl and *.tar.gz)
    build-deb:     Generates a Debian Linux distribution package (ie: *.deb)
    install-pip:   Builds and installs PIP distribution package
    install-deb:   Builds and installs Debian distribution package
    uninstall-pip: Uninstalls PIP distribution package
    uninstall-deb: Uninstalls Debian distribution package
    html:          Builds the HTML version of the docs
    clean:         Removes any automatically generated files

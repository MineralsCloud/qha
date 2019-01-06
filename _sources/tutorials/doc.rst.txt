How to build this documentation
*******************************

Before reading this, we assume the user already has a Unix or Unix-like shell environment, Bourne-again shell,
`Z shell <http://zsh.sourceforge.net>`_, etc. Every command below is executed in such an environment.

If the user wants to build this documentation before our official documentation website is hosted,
he/she needs to install
Sphinx 1.7.4 and some of its extensions. To install `Sphinx <http://www.sphinx-doc.org/en/stable/install.html>`_, please
look up `this tutorial <http://www.sphinx-doc.org/en/stable/install.html>`_. We generally recommend installing
`pip <https://pip.pypa.io/en/stable/installing/>`_ and use::

   $ pip install -Iv sphinx==1.7.4

to install Sphinx.

Besides Sphinx, two more extensions are needed, type::

   $ pip install sphinx-autodoc-typehints
   $ pip install sphinx_bootstrap_theme

in command line. One may have to install ``qha`` itself, see :ref:`installing` for more details.

After all the installation is done, go to `project repo <https://github.com/MineralsCloud/qha>`_ and type::

   $ git clone https://github.com/MineralsCloud/qha.git

in command line. The go to ``path/to/cloned/repo/docs/``, and run command::

   $ make clean && make html

to build this documentation. The output files are at ``path/to/cloned/repo/docs/build/html/``, and the entry point is
the ``index.html`` under this directory.

There might be some warnings in a not well-formatted documentation building process, but as long as it does not throw
errors, that is fine.

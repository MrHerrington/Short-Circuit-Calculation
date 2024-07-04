.. ShortCircuitCalc documentation master file, created by
   sphinx-quickstart on Wed Jun 26 17:14:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Simplify calculation the electrical system parameters
=====================================================

The program calculates the parameters of the power supply system (at the moment short circuit currents),
and also provides a built-in browser for managing the electrical equipment catalog database.

Modules and technologies used:
    - technologies:
        - python;
        - SQL;
        - databases administration (MySQL, SQLite);
        - Qt Designer;
        - GUI optimization (graphics mapping blitting, multithreading operations).
    - modules:
        - CairoSVG;
        - matplotlib;
        - numpy;
        - pandas;
        - PyQt5;
        - sphinx;
        - SQLAlchemy.

Graphics engine of this program used CairoSVG module.
CairoSVG is an SVG converter based on Cairo. It can export SVG files to PDF, EPS, PS, and PNG files.

Requirements for correctly working CairoSVG module (successful testing on Windows 10 64 bit):
    - | GTK+ for Windows Runtime Environment Installer (fork from http://gtk-win.sourceforge.net)
      | (watch https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer latest release);
    - | UniConvertor 2.0 Release Candidate 5 (RC5)
      | (watch https://sk1project.net/uc2/download/).

.. toctree::
   :hidden:
   :caption: PACKAGES

   rst_files/database
   rst_files/gui
   rst_files/tools

.. toctree::
   :hidden:
   :caption: MODULES

   rst_files/config
   rst_files/run

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

.. * :ref:`search`

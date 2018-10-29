dib-functests
-------------

Run diskimage-builder functional tests

Installs dib and dependencies, and runs functional tests

**Role Variables**

.. zuul:rolevar:: python_version
    :default: 2

    The python version to run the test under

.. zuul:rolevar:: dib_functests
    :default: []

    The list of functional tests to run

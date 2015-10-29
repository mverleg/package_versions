
Package versions
-------------------------------

Implements version numbers, e.g. for use in your custom package/module/extension/addon system.

Version ranges are stored as VersionRange and can be created using syntax similar to pip:

.. code-block:: python

    VersionRange('==3')
    # >=3.0,<4.0
    VersionRange('<=2.5,>1')
    # >=2.0,<=2.5
    VersionRange('==2.*')
    # >=2.0,<3.0

The main functionality is the combination of version ranges as best as possible, which is needed in case two packages rely on the same third package, but with different version limitations:

.. code-block:: python

    VersionRange('<=2.5,>1') & VersionRange('==2.*')
    #>=2.0,<=2.5
    VersionRange('<4.4') & VersionRange('>0,<=7')
    #>=1.0,<4.4
    VersionRange('<4.4') & VersionRange('>5.3')
    #==5.3 and an optional warning or error (due to the mismatch in range)

.. comment:: choose
.. commnet:: parse_dependency (comment, duplicate)


Restrictions
-------------------------------

A restriction this package imposes is that it assumed that feature versions are pairs of at most two integers, like `11.7` but not `11.7.3` or `1.7dev`.

Version `11.7.3` is assumed to contain only bug-fixes compared to `11.7`, and as such will always be preferred. Personally I like this unambiguous interpretation, but it's up to you if you accept it.

Tests
-------------------------------

There are a lot of py.test unit tests that you can run using:

.. code-block:: bash

    python3 -m pytest

License
-------------------------------

BSD 3-clause “Revised” License. Keep the license file and understand that I'm not to be held liable, and then you're free to do pretty much whatever.



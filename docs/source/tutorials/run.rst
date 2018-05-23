Run calculation command: ``qha-run``
************************************

First you need to prepare a standard input file and a YAML file specifying
your computational settings, which by default is named ``settings.yaml``.


+--------------+--------------------------------------------------------------------------+
| Notes                     | Structure of the input data                                              |
+==============+==========================================================================+
| First 3 lines are comments, plus the description of the calculation, but can also be empty.              | # Comment line                                                           |
+--------------+                                                                          |
|              | # Additional comment line                                                |
+--------------+                                                                          |
|              | # Number of volumes, q-vectors, normal mode, formula units               |
+--------------+                                                                          |
|              | nv   nq    3N    nm                                                      |
+--------------+                                                                          |
|              |                                                                          |
+--------------+                                                                          |
|              | P=   P1   V=   V1   E=   E1                                              |
+--------------+--------------------------------------------------------------------------+
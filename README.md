Ordered Filename Pre-Commit Check
=================================

A pre-commit script in python checking that certain files are added, modifier
or removed last, alphabetically. Kind of like a stack.

This is for example useful in projects where database migration scripts are
executed alphabetically.

What it does
------------

Consider an SVN repository with the following contents:

<pre>
module1/
  db/
    01.migration
    02.migration
    04.migration
module2/
  db/
    03.migration
    05.migration
    06.migration
</pre>

Assuming that the script is set up to match the `*.migration` files in the path `db/`
for every module, it would **not** be possible to commit a file named
`module1/db/05.migration` since a file named `06.migration` exists in module2.
A correct filename would rather be module1/db/07.migration`.

Neither would it be possible to modify or remove any migration but
`module2/db/06.migration`.

Usage
-----

For an example of how to run the script in a hook, see the file `pre-commit-example`.

<pre>
Usage: ordered_filename_pre_commit.py REPOS TXN

Run pre-commit verification on a repository transaction.

Options:
  -h, --help      show this help message and exit
  -r, --revision  Test mode. Specify a revision instead of a transaction.
</pre>
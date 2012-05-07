Ordered Filename Pre-Commit Check
=================================

A pre-commit script in python checking that certain files are added last,
alphabetically, in its directory.

This is for example useful for projects where database migration scripts are
executed alphabetically.

Usage
-----

For an example of how to run the script in a hook, see `pre-commit`.

For script usage, see below:

<pre>
Usage: ordered-filename-pre-commit.py REPOS TXN FILE_PATTERN SKIP_KEYWORD

Run pre-commit verification on a repository transaction.

Options:
  -h, --help      show this help message and exit
  -r, --revision  Test mode. Specify a revision instead of a transaction.
</pre>
Ordered Filename Pre-Commit Check
=================================

A pre-commit script in python, checking that files matching a supplied regular 
expression are named alphabetically after all other files in the same directory, 
matching the same regular expression.

This is for example useful for projects where database migrations are stored in files, 
and executed alphabetically. Here this verifies that new migrations are added last and
thus executed in the expected order.
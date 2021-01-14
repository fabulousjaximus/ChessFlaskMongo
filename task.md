# Project objective

To refactor the web app to use a MongoDB database as the backend, with minimal changes in the code.

# Guiding questions

1. Where is the data stored?
2. What function(s)/method(s) require access to the data?
3. How can these function(s)/method(s) be refactored so that the data source can be swapped with another polymorphic object easily?

# Task

1. Refactor the `ChessBoard` class in `chess.py` to abstractise access to the data.
2. Implement a `DataSource` class, with methods for accessing, modifying, and removing data from a MongoDB database.

You may find it helpful to move the data access methods from `ChessBoard` to a new class.

Each group is to submit:

1. A repl link to a working web app.

# Grading criteria

Your group's code will be graded based on:

- proper abstraction in `ChessBoard`
- appropriate access of data in MongoDB
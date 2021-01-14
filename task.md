# Project objective

To refactor the web app to use a MongoDB database as the backend, with minimal changes in the code.

# Guiding questions

1. Where is the data stored?
2. What function(s)/method(s) require access to the data?
3. How can these function(s)/method(s) be refactored so that the data source can be swapped with another polymorphic object easily?

# Task

1. Implement a `DataSource` class, with methods for:
   - retrieving all coordinates
   - retrieving all pieces
   - retrieving one piece
   - removing one piece
   - updating the position of one piece

Each group is to submit:

1. A repl link to a working web app,
2. An *individual* video (not more than 5 min) explaining how the following features were applied:
   - main game features
   - undo feature (Move History)

# Grading criteria

Each criteria is assigned a score of 0-2 depending on how well the requirements were met.


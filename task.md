# Project objective

To refactor the web app to use a MongoDB database for saving the game data, with minimal changes in the code.

## Guiding questions

1. Which objects/attributes hold the data to be stored?
2. At which point in the program should the data be stored/retrieved?
3. What schema would be appropriate for storing the data?
   - What entities are required to represent the game objects?
   - What are the appropriate relationships between entities?
   - What cardinality should each relationship be?

# Task 1

Design an appropriate schema for storing the game data.

(Hint: look at what attributes your objects are already using.)

Use the following format for your designed schema:

   ```
   Name
   ---------
   +attribute1
   +attribute2
   +method1(arg1, arg2)
   +method2(arg1, arg2)
   ...
   ```

# Task 2

The `DataSource` class provides methods for accessing, modifying, and removing data from a MongoDB database. When users start a new game of chess, they must provide a text label for the game. Each game of chess is stored in a different collection, named after its label.

The MongoDB database used for this project is hosted in the cloud, and is accessible through this URI: `mongodb://mongo:ktnHJtg7vBmc@cluster0-shard-00-00.iol15.mongodb.net:27017,cluster0-shard-00-01.iol15.mongodb.net:27017,cluster0-shard-00-02.iol15.mongodb.net:27017/h2_computing?ssl=true&replicaSet=atlas-14p70c-shard-0&authSource=admin&retryWrites=true&w=majority`

There are 4 methods used for storing data to the database, and loading data from the database:
- `get_game(label)`
   Retrieves the game data

- `set_game(label, game)`
  Updates the game data into the database

- `get_board(label)`
  Retrieves the board data

- `set_board(label, data)`
  Updates the board data into the database

Each group is to submit:

1. A repl link to a working web app.

# Grading criteria

Your group's code will be graded based on:

- proper abstraction in `ChessBoard`
- appropriate access of data in MongoDB
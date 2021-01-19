# Project objective

To refactor the web app to use a MongoDB database for saving the game data, with minimal changes in the code.

## Database access

The MongoDB database used for this project is hosted in the cloud, and is accessible through this URI: `mongodb://mongo:ktnHJtg7vBmc@cluster0-shard-00-00.iol15.mongodb.net:27017,cluster0-shard-00-01.iol15.mongodb.net:27017,cluster0-shard-00-02.iol15.mongodb.net:27017/h2_computing?ssl=true&replicaSet=atlas-14p70c-shard-0&authSource=admin&retryWrites=true&w=majority`

**Note:** Do not share this URL publicly!

## Guiding questions

1. Which objects/attributes hold the data to be stored?
2. At which point in the program should the data be stored/retrieved?
3. What schema would be appropriate for storing the data?
   - What entities are required to represent the game objects?
   - What are the appropriate relationships between entities?
   - What cardinality should each relationship be?

# Objectives

## Task 1

Design an appropriate data schema for storing the game data.

(Hint: look at what attributes your objects are already using.)

Use the following format for your designed schema:

   ```
   Name
   ---------
   +attribute1: type1
   +attribute2: type2
   ...
   ```

Valid types: `int`, `float`, `str`, `bool`, array (`list`), obj (`dict`)

## Task 2

The piece, board and game data must be *serialised* to a database document before they can be stored. When retrieved from the database, they must be *deserialised* to an object again before they can be used in the game.

Define two methods for the `BasePiece`, `ChessBoard`, and `GameMaster` classes as follows:

- `fromdoc(doc)` is a **class method** that takes in a document and returns an instance of the class, properly initialised
- `todoc()` is an **instance method** that returns the instance as a document, with appropriate attributes set as keys in the document

## Task 3

Define a `DataSource` class that provides methods for creating, retrieving, and modifying game data from a MongoDB database as follows:

- `load(label) -> board, game`
  Load data from the database using `label`.
  Data from the document should be *deserialised*, and returned as `board` and `game` objects.
  The label should be assigned to `game.name`.

- `save(board, game)`
  Save data to the database.  
  The label used should be obtained from `game.name`.  
  Data from the `board` and `game` objects should be *serialised* before being sent to the database.

- `initgame(board, game)`
  Checks the database to see if game data already exists.  
  If it does not exist, insert a document with initial game data.

**Hint:** Use the `fromdoc()` and `todoc()` methods of each class to carry out serialisation and deserialisation easily.

## Task 4

Define a function, `save_to_json()`, that writes the game data to a JSON file.

This function is called after each players' turn.

(This will aid you in debugging, by making it easier to inspect your data.)

# Submission

Each group is to submit:

1. A repl link to a working web app.

## Grading criteria

Your group's code will be graded based on:

- proper abstraction in `ChessBoard`
- appropriate access of data in MongoDB
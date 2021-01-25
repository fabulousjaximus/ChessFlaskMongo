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

### Reference ER Model

The state of each chess game is stord in a single MongoDB document as follows:

```
{                         ## Chess document
    game: {               ## Game document
        name: str,
        turn: str
    },
    board: {              ## Board document
        position: [
            {             ## Coord document
                x: int,
                y: int,
                piece: {  ## Piece document
                    colour: str,
                    name: str,
                    moved: bool
                }
            }
        ]
    }
}
```

This document is to be stored in a collection named after your group.
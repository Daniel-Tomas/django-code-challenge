# Engineering Assessment

Starter project to use for the engineering assessment exercise

## Requirements
- Docker
- docker compose

## Getting started
Build the docker container and run the container for the first time
```docker compose up```

Rebuild the container after adding any new packages
``` docker compose up --build```

The run command script creates a super-user with username & password picked from `.env` file

## Solution comments
The code tries to be self-explanatory (clear naming and organization accompanied by explanatory comments when necessary) <br>
I would appreciate hearing from you in case you think something is not clear enough

### Some reflections on the solution
Assume all users must have already created an user account? Assume all users are on the system?
I don't assume it, the system wouldn't be very usable.
Then the way of inviting users to a quiz is by sending a link where everybody can signup/signin and participate in a quiz


### Out of scope for this challenge, in a real-world scenario I would:

    1. document key design decisions
    2. document features
    3. test comprehensively

    4. consider adding throttling to the APIs
    5. consider adding pagination to the APIs
    6. consider adding caching to the APIs
    
    7. add feature for quizzes closing
       possible approaches: manually close quiz, automatically when a deadline is reached or when all people already answer (how do we know this? all invited emails answered?)

    8. document all endpoints following the Open API format with the help of the library drf-spectacular 

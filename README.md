# Heavy Rotation

#### Created by Alma Frankenstein for Epicodus, 2020

## Description
Welcome! Heavy Rotation is a blog where people can post the songs they've been listening to on repeat lately, and see what their friends are listening to.

Special thanks to Miguel Grinberg for his excellent book 'Flask Web Development' (O'Reilly, 2018) and many online tutorials.

## Specs
Users can:
* Post which songs they have on heavy rotation
* Click a link to a posted song (if one has been added) and have that link open in a new browser tab
* Follow other users and see their posts
* Add 'about me' information to their profile

Other features include:
* Pagination

## Setup

To run on your localhost, clone this repo using:

```git clone https://github.com/alma-frankenstein/heavy_proto.git heavyRotation```

cd to the heavyRotation directory.

Install Python3, if you haven't already

Create a virtual environment for the project:
* Run ```python3 -m venv venv```
* Activate it with ```source venv/bin/activate```

Run ```pip install -r requirements.txt``` to install all dependencies

Create a migration repository for a database: ```flask db init```

Still with the virtual environment activated, run ```flask run```, then open the browser window indicated
(this will probably be http://127.0.0.1:5000/). You should see the welcome page.

To add changes to the database:
* Add the change to models.py
* Run ```flask db migrate``` to generate a migration script
* Then ```flask db upgrade``` to add the changes to the database

To run the test suite:
* Make sure the virtual environment is activated (see above), then run ```python tests.py```

## Technologies Used

* Python
* Flask
* SQLAlchemy
* Jinja2
* Flask-Login

## Known Bugs
No known bugs at this time.

## Contact Details

For questions or to suggestions, please email A.Q.Frankenstein@gmail.com

### License

This software is licensed under the MIT license.

Copyright (c) 2020 Alma Frankenstein


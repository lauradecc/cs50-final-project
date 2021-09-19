# Circus For Developers
#### Video Demo:  https://www.youtube.com/watch?v=0j7zVeQz1Ls
### Description:

**Circus For Developers** is a web application to register for an event and its activities.
In this case, a circus event organized by five fictitious companies for developers working in them.

### Usage

1. Employees register for the event and select the company they work for.
2. They can sign up for the show and up to two workshops.
3. After registering for an activity, a confirmation email is sent.
4. It is possible to unsubscribe from every activity, after which an email with the cancellation information is sent.
5. Every employee can see what colleagues from their company will attend the event.

### Files

#### application.py

**application.py** is the file that makes everything work properly, where all the logic of the application is set (e.g., ensure information needed is submitted, send an email when appropriate, add/delete/obtain information from database...).

#### Templates

- **register.html** is the template where the registration form is located, so users can register and access the site.
- **login.html** allow users to log in to the application.
- **index.html** is the homepage of the site, from which it is possible to read general information about the event and access the rest of the pages.
- **show.hmtl* contains information about the main show of the event and from it users can register to it.
- **workshops.html** includes all workshops users can sign up to.
- **bookings.html** show each activity that the user is registered for. From this page users can unsubscribe from any of the activities and also see what colleages are attending the event.
- **layout.html** is the template that contains the static data common to every other page, so it does not need to be repeated in all.
- **apology.html** appears every time an error occurs and let the user know what happened (e.g., wrong password submitted, trying to register in more than two workshops, etc.).

#### Other files

- **database.db** is a SQLite database to store users and information related to them. In this case, information about users, their company, and the activities they are registered for.
- **helpers.py** is where the implementation of apology.html, a function to render a message as an apology to user and another function to decorate routes to require login. From CSF0 Finance problem set.
- **styles.css** is the file that cointains the CSS used to modify the design of the application.
- **javascript.js** has two functions used to display new HTML into the templates. The first function displays data from the database on bookings page and the second one displays text on show page.

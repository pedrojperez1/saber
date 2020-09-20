# Saber

[Saber](https://saber-app.herokuapp.com/) was designed to help citizens participate in the democratic process by asking questions to the politicians that represent them. Questions are asked publicly, so users can see what kinds of questions are being asked in their area.

### User Flow

When you create your account, the app uses Google's [Civic Information API](https://developers.google.com/civic-information) to fetch all government officials that represent you, from the POTUS down to the last City Council member.

Once you are set up, you'll be able to see questions that have been asked in your area. You can like another user's question by raising your hand too. Once a question has enough hands up, we'll reach out to the official for comment!

### Technology

Saber uses a HTML/CSS/JS (with [Bootstrap](https://getbootstrap.com/docs/4.5/getting-started/introduction/)) front-end and a Python/[Flask](https://flask.palletsprojects.com/en/1.1.x/) back-end. Deployment is done via [Heroku](https://devcenter.heroku.com/categories/reference).

### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Try the app our for yourself [here](https://saber-app.herokuapp.com/)!

This app was created and is maintained by Pedro Perez.

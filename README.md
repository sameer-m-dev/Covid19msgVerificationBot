# Covid19msgVerificationBot
A chat/voice bot that can determine the validity of messages related to COVID-19 that are forwarded on Social Media
# Folder Info

* # client

Contains static HTML files that form the frontend of the Application

* # server

Contains the Python API what can add new messages to the database and verify the validy of new messages. 
We use Cosine Similarity to determine the similarity between messages.
The verifyMessage route also has an additional paramater, cosineThreshold, which can be set before deploying the application.
This threshold determines what should be the minumum match value between messages in order to determine its validity.
Its value can be anything between 0-1.

* # database
Contains database related files such as dtabase scheme, dumps, etc.

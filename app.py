# Importing all the necessary libraries
import nltk
nltk.download("stopwords")
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from mysql.connector import Error
import mysql.connector
import re
from flask_cors import CORS
from flask import request, jsonify, Flask
from bs4 import BeautifulSoup

# Declaring Variables
SERVER_ADDRESS = "localhost"
DATABASE_NAME = "msgVerificationBot"
DATABASE_USER = "root"
DATABASE_USER_PASSWORD = "123456"
MESSAGES_TABLE = "messages"
# COSINE_THRESHHOLD = 0.8

# Creating a Flask app
app = Flask(__name__)
# Enabling CORS
CORS(app)

# Importing StopWords
# In Python, searching a set is much faster than searching
# a list, so convert the stop words to a set
sw = set(stopwords.words("english"))

# Function to create and return SQL Connection


def sqlConnect():
    try:
        connection = mysql.connector.connect(host=SERVER_ADDRESS,
                                             database=DATABASE_NAME,
                                             user=DATABASE_USER,
                                             password=DATABASE_USER_PASSWORD)
        return connection
    except Error as e:
        print(e)
        return "Error"


# Function to terminat an existing SQL Connection
def sqlDisconnect(connection, cursor):
    if (connection.is_connected()):
        cursor.close()
        connection.close()

# Function to convert a raw text to a string of words


def preprocessData(raw_text):
    # The input is a single string (a raw movie review), and
    # the output is a single string (a preprocessed movie review)
    #
    # 1. Remove HTML
    review_text = BeautifulSoup(raw_text, features="html.parser").get_text()
    #
    # 2. Remove non-letters
    letters_only = re.sub("[^a-zA-Z]", " ", review_text)
    #
    # 3. Convert to lower case, split into individual words
    words = letters_only.lower().split()
    #
    # 4. Remove Stopwords
    meaningful_words = [w for w in words if not w in sw]
    #
    # 5. Join the words back into one string separated by space,
    # and return the result.
    return(" ".join(meaningful_words))

# Function to check the cosine similarity between 2 sentences


def checkSimilarity(messageFromUser, messageFromDB):
    # Tokenizing Sentences
    messageFromUser_list = set(word_tokenize(messageFromUser))
    messageFromDB_list = set(word_tokenize(messageFromDB))
    l1 = []
    l2 = []
    # Form a set containing keywords of both strings
    rvector = messageFromUser_list.union(messageFromDB_list)
    for w in rvector:
        if w in messageFromUser_list:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in messageFromDB_list:
            l2.append(1)
        else:
            l2.append(0)
    c = 0
    # Cosine Formula
    for i in range(len(rvector)):
        c += l1[i]*l2[i]
    cosine = c / float((sum(l1)*sum(l2))**0.5)
    return cosine

# Route to add a message to the database
@app.route('/addMessage', methods=["POST", "GET"])
def addMessage():
    """
    Function to add a message to the database
    Accepts: 
            text: sentence to be added to the database
            truthValue: 1 if the message is correct and 0 if it is incorrect or misleading
    Returns:

    """

    message = request.get_json().get('message', '')
    truthValue = request.get_json().get('truthValue', '')

    # Preprocessing Text
    messageTransformed = preprocessData(message)

    # Creating an SQL Connection
    connection = sqlConnect()
    cursor = ""

    # Checking if connection was established
    if (connection != "Error"):
        try:
            # Creating a new DB Cursor
            cursor = connection.cursor()
            # Executing Query
            cursor.execute("INSERT INTO "+MESSAGES_TABLE +
                           " (sentence, truthValue) VALUES('"+messageTransformed+"', '"+truthValue+"');")
            # Committing transaction
            connection.commit()
            # Disconnecting SQL connection
            sqlDisconnect(connection, cursor)
            # Returning result to user
            return jsonify({"result": "Message Inserted Successfully"})
        except Exception as e:
            # Printing exception to console
            print(e)
            # Returning error message
            return jsonify({"result": "Error occured, please try again later"}), 400
    else:
        # Returning error message
        return jsonify({"result": "Could not connect to server"}), 400

# Route to verify if a message is credible or not
@app.route('/verifyMessage', methods=["POST", "GET"])
def verifyMessage():
    """
    Function to verify if a message is credible or not.
    Accepts: 
            message: message that is to be verified
            cosineThreshold: threshold of sentence similarity
    Returns:

    """

    message = request.get_json().get('message', '')
    cosineThreshold = request.get_json().get('cosineThreshold', '')
    
    # Preprocessing Raw Text
    messageTransformed = preprocessData(message)

    # Creating an SQL Connection
    connection = sqlConnect()

    # Initializing Variables
    finalTruthValue = ""
    cursor = ""
    data = ""
    cosineSimilarityValue = 0
    verficationCount = 0

    # Checking if connection was established
    if (connection != "Error"):
        try:
            # Creating a new DB Cursor
            cursor = connection.cursor()
            # Executing Query
            cursor.execute("SELECT * FROM "+MESSAGES_TABLE + ";")
            data = cursor.fetchall()

            # Iterating over the whole result-set
            for row in data:
                cosineSimilarityValue = checkSimilarity(
                    messageTransformed, row[1])
                print(cosineSimilarityValue)
                if float(cosineSimilarityValue) >= float(cosineThreshold):
                    verficationCount += 1
                    finalTruthValue = row[2]
                    break
            # Disconnecting SQL connection
            sqlDisconnect(connection, cursor)
            # Returning result to user
            if verficationCount != 0:
                if finalTruthValue == 1:
                    return jsonify({"result": "Valid Message"})
                else:
                    return jsonify({"result": "Invalid Message"})
            else:
                return jsonify({"result": "Cannot determine validity of the message at this time. Please try again later"})
        except Exception as e:
            # Printing exception to console
            print(e)
            # Returning error message
            return jsonify({"result": "Error occured, please try again later"}), 400

    else:
        # Returning error message
        return jsonify({"result": "Could not connect to server"}), 400

    # Returning results in JSON Format
    return jsonify({"result": data})


if __name__ == '__main__':
    app.run(debug=True, host="localhost", threaded=False)
    app.run()

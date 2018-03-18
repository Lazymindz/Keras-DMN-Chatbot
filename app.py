from flask import Flask, render_template, request, flash
from flask import jsonify
import sys
from data_utils import *
from rnn_model import *
import numpy as np

sys.path.append("..")

app = Flask(__name__,static_url_path="/static")

memory_network = memoryNetwork()

def add_story(story, msg):

    if not msg.endswith('.'): msg += '.'
    story += msg

    return story

def bot_response(msg):

    if parm['story'] == '' and parm['stage'] != 's':
        parm['stage'] = 's'
        return 'I can only read this vocabulary to form Questions:\n' + ' , '.join(memory_network.word_id.keys())

    if request.form['msg'].upper() != 'END' and parm['stage'] == 's':
        parm['story'] = add_story(parm['story'], request.form['msg'])
        return "i'm listening...type 'END' to stop"

    elif request.form['msg'].upper() == 'END' and parm['stage'] != 'q':
        parm['stage'] = 'q'
        return 'Here is the Story:' + '\n' + parm['story'] + '\n' + 'post your question:'

    elif parm['question'] == '' and parm['stage'] == 'q':
        parm['question'] = request.form['msg']
        story_vector, query_vector = vectorize_ques([(tokenize(parm['story']), tokenize(parm['question']))],
                                                    memory_network.word_id, 68, 4)
        prediction = memory_network.model.predict([np.array(story_vector), np.array(query_vector)])

        prediction_word_index = np.argmax(prediction)

        try:
            answer = memory_network.word_id.keys()[memory_network.word_id.values().index(prediction_word_index)]
            parm['story'] = ''
            parm['question'] = ''
            parm['stage'] = 'a'

        except:
            answer = 'Something has gone wrong. '
            parm['story'] = ''
            parm['question'] = ''
            parm['stage'] = 'a'

        return 'Answer is : ' + answer

    else:
        answer = 'Something has gone wrong. '
        parm['story'] = ''
        parm['question'] = ''
        parm['stage'] = 'a'
        return "I'm lost. Try again!"


# Routing
#
@app.route('/message', methods=['POST'])
def reply():
    return jsonify( { 'text': bot_response(request.form['msg'].upper()) } )

@app.route("/")
def index():
    return render_template("index.html")
#############

# start app
if (__name__ == "__main__"):
    parm = {'story' : '', 'question': '', 'answer': '', 'stage':''}
    app.run(port = 5000)

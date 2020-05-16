from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Question, Survey, satisfaction_survey

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'redpanda321'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

RESPONSES = []
CURR_QUESTION = 0
SURVEY = satisfaction_survey
FINISHED = False


@app.route('/')
def survey_home():
    """Returns the survey home page"""
    return render_template(
        'home.html',
        survey_title=SURVEY.title,
        survey_instructions=SURVEY.instructions
    )


@app.route('/start-survey', methods=["POST"])
def start_survey():
    session["responses"] = []
    return redirect('/questions/0')

@app.route('/questions/<int:question_id>')
def show_question(question_id):
    """
    Responds with question given question_id. Redirects user if they try to access a question
    out of order or if they try to access a question after they are done.
    """
    if not FINISHED:
        if question_id != CURR_QUESTION: # redirect if trying to access question out of order
            flash("Invalid URL. Redirecting you to next question.")
            return redirect(f'/questions/{CURR_QUESTION}')
        else:
            question = SURVEY.questions[question_id]
            return render_template(
                'questions.html',
                title=SURVEY.title,
                question=question.question,
                choices=question.choices,
                allow_text=question.allow_text
            )
    else: # redirect to /thanks if they try to access a question after survey is FINISHED
        return redirect('/thanks')


@app.route('/answers', methods=["POST"])
def record_answer():
    """
    This endpoint records the answer provided and redirects to next question. Also redirects
    user if the survey is done.
    """
    responses = session["responses"]
    responses.append(request.form['answer'])
    session["responses"] = responses
    global CURR_QUESTION
    CURR_QUESTION += 1
    if CURR_QUESTION < len(SURVEY.questions):
        return redirect(f'/questions/{CURR_QUESTION}')
    else:
        global FINISHED
        FINISHED = True
        return redirect('/thanks')


@app.route('/thanks')
def show_thanks():
    """Thank the user for taking the survey"""
    return render_template('thanks.html')
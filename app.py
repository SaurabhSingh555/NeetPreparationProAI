from flask import Flask, render_template, request, session, jsonify, redirect, url_for
import pandas as pd
import random
from datetime import datetime, timedelta
import os
import csv

app = Flask(__name__)

# Define available years and subjects
AVAILABLE_YEARS = ['2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016']
AVAILABLE_SUBJECTS = ['Botany', 'Zoology', 'Physics', 'Chemistry']

# Dataset directory path
DATASET_DIR = os.path.join(os.path.dirname(__file__), 'data')

# Dataset file mapping for each subject and year
SUBJECT_FILE_MAP = {
    'Botany': {
        '2024': 'Botny_Previous_Year 2024.csv',
        '2023': 'Botany_2023_Neet.csv',
        '2022': 'Botany_2022_Neet.csv',
        '2021': 'Botany_2021_Neet.csv',
        '2020': 'Botany_2020_Neet.csv',
        '2019': 'Botany_2019_Neet.csv',
    },
    'Zoology': {
        '2024': 'NEET2024_Zoology_previous_Questions.csv',
    },
    'Physics': {
        '2024': 'Physics2024PreviousYearQ&A.csv',
        '2023': 'Physics_Neet_2023.csv',
        '2022': 'Physics_2022_Neet_Unique_40_Questions.csv',
        '2021': 'Physics_2021_Neet_Unique_40_Questions.csv',
        '2020': 'Physics_2020_Neet_Unique_40_Questions.csv',
        '2019': 'Physics_2019_Neet_Unique_40_Questions.csv',
        '2018': 'Physics_2018_Neet_Unique_40_Questions.csv',
        '2017': 'Physics_2017_Neet_Unique_40_Questions.csv',
        '2016': 'Physics_2016_Neet_Unique_40_Questions.csv',
    },
    'Chemistry': {
        '2024': 'Chemistry_Previous_Year 2024.csv',
        '2023': 'Chemistry_2023_Neet_Unique_40_Questions.csv',
        '2021': 'Chemistry_2021_Neet_Unique_40_Questions (1).csv',
        '2020': 'Chemistry_2020_Neet_Unique_40_Questions (1).csv',
        '2019': 'Chemistry_2019_Neet_Unique_40_Questions.csv',
        '2017': 'Chemistry_2017_Neet_Unique_40_Questions.csv',
        '2016': 'Chemistry_2016_Neet_Unique_40_Questions.csv',
    }
}

def load_datasets():
    """Load all datasets from the data directory with proper error handling"""
    datasets = {}
    
    # Check if data directory exists
    if not os.path.exists(DATASET_DIR):
        print(f"Data directory not found at: {DATASET_DIR}")
        return datasets
    
    for subject in AVAILABLE_SUBJECTS:
        for year in AVAILABLE_YEARS:
            # Initialize year in datasets if not exists
            if year not in datasets:
                datasets[year] = {}
            
            # Check if this subject-year combination exists in our mapping
            if subject in SUBJECT_FILE_MAP and year in SUBJECT_FILE_MAP[subject]:
                filename = SUBJECT_FILE_MAP[subject][year]
                filepath = os.path.join(DATASET_DIR, filename)
                
                if os.path.exists(filepath):
                    try:
                        # First try to read as CSV with standard format
                        try:
                            df = pd.read_csv(filepath)
                            
                            # Check for required columns
                            required_columns = ['Question', 'Option A', 'Option B', 
                                             'Option C', 'Option D', 'Answer']
                            if not all(col in df.columns for col in required_columns):
                                # If standard columns not found, try alternative format
                                df = pd.read_csv(filepath, header=None)
                                if len(df.columns) >= 9:  # For your specific format
                                    df.columns = ['Question', 'Option A', 'Option B', 
                                                'Option C', 'Option D', 'Answer',
                                                'Subject', 'Topic', 'Year']
                                    # Add missing columns with defaults
                                    df['Explanation'] = "Explanation not available"
                                    df['Difficulty'] = "Medium"
                                
                        except Exception as e:
                            print(f"Error reading {filename} as CSV: {str(e)}")
                            df = None
                        
                        if df is not None and not df.empty:
                            # Ensure Answer column is consistently named
                            if 'Correct Answer' in df.columns and 'Answer' not in df.columns:
                                df.rename(columns={'Correct Answer': 'Answer'}, inplace=True)
                            
                            datasets[year][subject] = df
                        else:
                            print(f"Empty or invalid dataframe for {filename}")
                            datasets[year][subject] = None
                            
                    except Exception as e:
                        print(f"Error loading {filename}: {str(e)}")
                        datasets[year][subject] = None
                else:
                    print(f"File not found: {filepath}")
                    datasets[year][subject] = None
            else:
                # No file mapping for this subject-year combination
                datasets[year][subject] = None
    
    return datasets

# Load all datasets at startup
all_datasets = load_datasets()

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'your-secret-key-here'


@app.route('/motivation')
def motivation():
    success_stories = [
        {
            'title': "From Failure to AIR 42 🎯",
            'content': """I failed my first NEET attempt with just 320 marks 😔. But I didn't give up! 
            \n\n📌 Changed my strategy: Focused more on NCERT (read 5 times!) 
            \n📌 Daily routine: 6AM-10PM study with 45min breaks 
            \n📌 Key tip: Made my own formula book 📒
            \n\nNext year: Scored 680/720! 🎉""",
            'author': "Ananya S. (AIR 42)",
            'date': "2023-08-15"
        },
        {
            'title': "Village to Medical College 🌱",
            'content': """Coming from a village with no coaching, just NCERT and YouTube 📚
            \n\n🔥 Secret: Solved last 20 years papers 3 times 
            \n🔥 Created mnemonics for Biology 🧠 
            \n🔥 Practiced 10,000+ MCQs 💪
            \n\nGot AIIMS Delhi! Dreams do come true ✨""",
            'author': "Rahul K. (AIIMS)",
            'date': "2023-06-22"
        },
        {
            'title': "Single Mom's NEET Journey 👩‍👧",
            'content': """Prepared while raising my baby 👶 and working part-time:
            \n\n⏳ 4AM-7AM: Golden study hours 
            \n📱 Used apps for quick revisions 
            \n💡 Focused on high-weightage topics 
            \n\nAt 28, I cracked NEET in first attempt! Age is just a number 🎓""",
            'author': "Priya M. (MBBS Student)",
            'date': "2023-09-10"
        },
        {
            'title': "Third Attempt Triumph 🚀",
            'content': """I gave NEET thrice. First two attempts were full of anxiety and comparison. 
            \n\n📘 Year 3, I went offline: Deleted social media completely. 
            \n🧘 Mental health became priority: Daily 30 min walk + meditation. 
            \n📚 Studied 10 hours/day with deep focus blocks. 
            \n\nMy mock test average went from 520 to 690 over 4 months! I secured a govt seat finally in my third try. Never give up if your dream is alive. 🏥""",
            'author': "Kavya R. (Govt Medical College)",
            'date': "2024-01-05"
        },
        {
            'title': "NEET with No Tuition – Just Discipline 📖",
            'content': """No coaching. No expensive courses. Just books and belief. 
            \n\n💡 Studied with a strict timetable from Day 1. 
            \n🎯 Key tools: NCERT, PYQs, MTG 31 Years, Biology wall charts. 
            \n📅 Monthly mock test analysis with Excel sheets. 
            \n\nI ranked in top 1,000 and saved my family lakhs in tuition costs. Smart work over hype works!""",
            'author': "Mehul T. (Top 1000 Ranker)",
            'date': "2023-11-20"
        },
        {
            'title': "From ICU Bed to NEET Rank 🏥➡️🎓",
            'content': """In class 12, I was hospitalized for 3 months with a lung condition. Doctors doubted I could give the exam. 
            \n\n🛏️ While recovering, I studied in bed using audio lectures and NEET-prep podcasts. 
            \n✍️ Couldn’t write much, so revised using flashcards and mind maps. 
            \n⚡ Came back stronger: 12 hours daily prep post-recovery for 5 months. 
            \n\nNot only did I sit for NEET, I scored 660 and got admission to a top college. Mindset matters more than anything. ❤️‍🔥""",
            'author': "Ishaan B. (Survivor & Student Doctor)",
            'date': "2024-03-18"
        }
    ]
    return render_template('motivation.html', stories=success_stories)



@app.route('/')
def home():
    # Calculate which years actually have data for any subject
    available_years_data = {
        year: any(
            data is not None and not data.empty
            for subject, data in all_datasets.get(year, {}).items()
        )
        for year in AVAILABLE_YEARS
    }
    
    return render_template('index.html', 
                         years=AVAILABLE_YEARS, 
                         subjects=AVAILABLE_SUBJECTS,
                         available_years_data=available_years_data)

@app.route('/quiz', methods=['POST'])
def quiz():
    subject = request.form['subject']
    year = request.form['year']
    
    # Validate inputs
    if subject not in AVAILABLE_SUBJECTS or year not in AVAILABLE_YEARS:
        return "Invalid subject or year selected", 400

    try:
        num_questions = int(request.form['num_questions'])
        timer_minutes = int(request.form.get('timer', 60))  # Default 60 minutes
    except (KeyError, ValueError) as e:
        return "Invalid input parameters", 400

    # Get the dataset for the selected year and subject
    subject_data = all_datasets.get(year, {}).get(subject)
    
    if subject_data is None or subject_data.empty:
        return "No questions available for the selected year and subject", 400

    if num_questions < 1 or num_questions > len(subject_data):
        return f"Number of questions must be between 1 and {len(subject_data)}", 400

    # Randomly select questions without replacement
    selected_questions = subject_data.sample(n=min(num_questions, len(subject_data)))
    selected_questions_list = selected_questions.to_dict(orient='records')
    
    # Calculate end time for the quiz
    end_time = datetime.now() + timedelta(minutes=timer_minutes)
    
    # Store in session
    session['selected_questions'] = selected_questions_list
    session['end_time'] = end_time.isoformat()
    session['timer_minutes'] = timer_minutes
    session['subject'] = subject
    session['year'] = year
    
    return render_template('quiz.html', 
                        questions=selected_questions_list,
                        end_time=end_time.isoformat(),
                        timer_minutes=timer_minutes,
                        subject=subject,
                        year=year)

@app.route('/get_time_remaining')
def get_time_remaining():
    if 'end_time' not in session:
        return jsonify({'error': 'No active quiz session'}), 400
        
    end_time = datetime.fromisoformat(session['end_time'])
    remaining = end_time - datetime.now()
    
    # If time is up, return zeros
    if remaining.total_seconds() <= 0:
        return jsonify({
            'minutes': 0,
            'seconds': 0,
            'total_seconds': 0,
            'time_up': True
        })
    
    return jsonify({
        'minutes': max(0, remaining.seconds // 60),
        'seconds': max(0, remaining.seconds % 60),
        'total_seconds': max(0, int(remaining.total_seconds())),
        'time_up': False
    })

@app.route('/result', methods=['POST'])
def result():
    if 'selected_questions' not in session:
        return "Quiz session expired or invalid", 400
        
    selected_questions = session.get('selected_questions', [])
    user_answers = []
    score = 0
    
    for question in selected_questions:
        user_answer_key = f"answer_{question['Question']}"
        answer = request.form.get(user_answer_key)
        correct_answer = question['Answer']
        is_correct = answer == correct_answer
        
        if is_correct:
            score += 1
            
        user_answers.append({
            'question': question['Question'],
            'user_answer': answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.get('Explanation', 'No explanation available'),
            'options': {
                'A': question.get('Option A', ''),
                'B': question.get('Option B', ''),
                'C': question.get('Option C', ''),
                'D': question.get('Option D', '')
            }
        })
    
    # Calculate percentage
    total_questions = len(selected_questions)
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Store results in session
    session['last_score'] = score
    session['last_total'] = total_questions
    session['last_percentage'] = percentage
    
    return render_template('result.html', 
                         user_answers=user_answers,
                         score=score,
                         total=total_questions,
                         percentage=percentage,
                         subject=session.get('subject'),
                         year=session.get('year'))

@app.route('/dashboard')
def dashboard():
    # In a real app, you would fetch this from a database
    performance_history = [
        {'date': '2023-05-01', 'subject': 'Physics', 'score': 75, 'total': 100},
        {'date': '2023-05-02', 'subject': 'Chemistry', 'score': 82, 'total': 100},
        {'date': '2023-05-03', 'subject': 'Botany', 'score': 68, 'total': 100},
    ]
    
    return render_template('dashboard.html', 
                         performance_history=performance_history,
                         subjects=AVAILABLE_SUBJECTS)

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"Created data directory at: {DATASET_DIR}")
    
    app.run(debug=True, port=5000)
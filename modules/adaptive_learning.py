import json
import os
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample question data
# In a real implementation, this would be loaded from a database
QUESTIONS = {
    'id': [
        # Level 1 - Beginner
        [
            {
                "id": "id-l1-q1",
                "text": "Apa bahasa resmi Indonesia?",
                "options": ["Bahasa Indonesia", "Bahasa Inggris", "Bahasa Jawa", "Bahasa Sunda"],
                "answer": "Bahasa Indonesia",
                "explanation": "Bahasa Indonesia adalah bahasa resmi Republik Indonesia."
            },
            {
                "id": "id-l1-q2",
                "text": "Lengkapi kalimat: Saya ___ ke sekolah setiap hari.",
                "options": ["pergi", "pergian", "perpergian", "berpergian"],
                "answer": "pergi",
                "explanation": "Kata 'pergi' adalah kata kerja yang tepat untuk melengkapi kalimat tersebut."
            },
            {
                "id": "id-l1-q3",
                "text": "Manakah kata sifat di bawah ini?",
                "options": ["cantik", "makan", "mereka", "cepat-cepat"],
                "answer": "cantik",
                "explanation": "Cantik adalah kata sifat yang menjelaskan keadaan atau kualitas."
            }
        ],
        # Level 2 - Intermediate
        [
            {
                "id": "id-l2-q1",
                "text": "Manakah kalimat yang menggunakan kata hubung dengan benar?",
                "options": [
                    "Dia tidak datang karena dia sakit.",
                    "Dia tidak datang tapi dia sakit.",
                    "Dia tidak datang dan dia sakit.",
                    "Dia tidak datang atau dia sakit."
                ],
                "answer": "Dia tidak datang karena dia sakit.",
                "explanation": "Kata hubung 'karena' menunjukkan hubungan sebab-akibat antara tidak datang dan sakit."
            },
            {
                "id": "id-l2-q2",
                "text": "Imbuhan mana yang tepat untuk kata 'ajar' dalam konteks 'orang yang mengajar'?",
                "options": ["pe-", "peng-", "pem-", "per-"],
                "answer": "peng-",
                "explanation": "Imbuhan 'peng-' pada kata dasar 'ajar' membentuk kata 'pengajar' yang berarti orang yang mengajar."
            },
            {
                "id": "id-l2-q3",
                "text": "Bentuk jamak dari kata 'anak' dalam bahasa Indonesia yang benar adalah...",
                "options": ["anak-anak", "para anak", "anaks", "anak semua"],
                "answer": "anak-anak",
                "explanation": "Dalam bahasa Indonesia, bentuk jamak dapat dibuat dengan pengulangan kata, seperti 'anak-anak'."
            }
        ],
        # Level 3 - Advanced
        [
            {
                "id": "id-l3-q1",
                "text": "Kalimat manakah yang mengandung majas personifikasi?",
                "options": [
                    "Angin berbisik di telinga saya.",
                    "Dia seperti harimau ketika marah.",
                    "Rumahnya sangat besar sekali.",
                    "Mereka tertawa terbahak-bahak."
                ],
                "answer": "Angin berbisik di telinga saya.",
                "explanation": "Personifikasi adalah majas yang memberikan sifat manusia pada benda mati. Angin tidak bisa 'berbisik', ini adalah sifat manusia."
            },
            {
                "id": "id-l3-q2",
                "text": "Dalam Ejaan Yang Disempurnakan (EYD), manakah penulisan gelar yang benar?",
                "options": [
                    "Dr. Ahmad, S.H., M.Hum.",
                    "DR Ahmad SH M.Hum",
                    "dr Ahmad, SH, M.HUM",
                    "Dr Ahmad S.H. M.Hum"
                ],
                "answer": "Dr. Ahmad, S.H., M.Hum.",
                "explanation": "Penulisan gelar yang benar menurut EYD menggunakan titik setelah singkatan dan koma setelah nama."
            },
            {
                "id": "id-l3-q3",
                "text": "Manakah yang merupakan contoh kalimat aktif?",
                "options": [
                    "Buku itu dibaca oleh siswa.",
                    "Siswa membaca buku itu.",
                    "Buku itu sedang dibaca.",
                    "Terdengar suara gemuruh dari kejauhan."
                ],
                "answer": "Siswa membaca buku itu.",
                "explanation": "Kalimat aktif adalah kalimat yang subjeknya melakukan tindakan. Pada kalimat tersebut, 'siswa' (subjek) melakukan tindakan 'membaca'."
            }
        ]
    ],
    'en': [
        # Level 1 - Beginner
        [
            {
                "id": "en-l1-q1",
                "text": "What is the plural form of 'child'?",
                "options": ["childs", "childen", "children", "child"],
                "answer": "children",
                "explanation": "The plural form of 'child' is 'children'. It's an irregular plural."
            },
            {
                "id": "en-l1-q2",
                "text": "Choose the correct pronoun: ___ are going to the park.",
                "options": ["I", "He", "She", "They"],
                "answer": "They",
                "explanation": "When referring to multiple people, we use the pronoun 'they'."
            },
            {
                "id": "en-l1-q3",
                "text": "Which is the correct verb form? She ___ to school every day.",
                "options": ["go", "goes", "going", "gone"],
                "answer": "goes",
                "explanation": "For third person singular (she, he, it) in the present simple, we add -s or -es to the verb."
            },
            {
                "id": "en-l1-q4",
                "text": "What is the past tense of 'eat'?",
                "options": ["eated", "ate", "eaten", "eating"],
                "answer": "ate",
                "explanation": "The past tense of 'eat' is 'ate'. It's an irregular verb."
            },
            {
                "id": "en-l1-q5",
                "text": "Which article would you use before the word 'university'?",
                "options": ["a", "an", "the", "no article"],
                "answer": "a",
                "explanation": "We use 'a' before words that begin with a consonant sound. Although 'university' starts with a vowel letter, it begins with a consonant sound /j/."
            }
        ],
        # Level 2 - Intermediate
        [
            {
                "id": "en-l2-q1",
                "text": "Choose the correct tense: I ___ the movie last night.",
                "options": ["watch", "watching", "watched", "am watching"],
                "answer": "watched",
                "explanation": "For completed actions in the past, we use the past simple tense (watched)."
            },
            {
                "id": "en-l2-q2",
                "text": "What is the correct preposition? She arrived ___ the airport on time.",
                "options": ["in", "on", "at", "by"],
                "answer": "at",
                "explanation": "We use 'at' with specific locations like airports, stations, etc."
            },
            {
                "id": "en-l2-q3",
                "text": "Choose the correct phrasal verb: Can you ___ this form?",
                "options": ["fill in", "fill out", "fill up", "Both A and B are correct"],
                "answer": "Both A and B are correct",
                "explanation": "Both 'fill in' and 'fill out' mean to complete a form with information."
            },
            {
                "id": "en-l2-q4",
                "text": "Which sentence uses the present perfect correctly?",
                "options": [
                    "I have seen that movie yesterday.", 
                    "I have seen that movie three times.", 
                    "I have see that movie already.", 
                    "I have saw that movie."
                ],
                "answer": "I have seen that movie three times.",
                "explanation": "The present perfect is used for experiences or actions with a connection to the present. We don't use specific past time expressions like 'yesterday' with it."
            },
            {
                "id": "en-l2-q5",
                "text": "What is the correct comparative form of 'good'?",
                "options": ["gooder", "better", "more good", "goodest"],
                "answer": "better",
                "explanation": "The comparative form of 'good' is 'better'. It's an irregular comparative."
            }
        ],
        # Level 3 - Advanced
        [
            {
                "id": "en-l3-q1",
                "text": "Identify the correct subjunctive mood: The teacher insisted that the student ___ the assignment.",
                "options": ["completes", "complete", "completed", "completing"],
                "answer": "complete",
                "explanation": "After verbs like 'insist', 'recommend', 'suggest' in formal contexts, we use the subjunctive form, which is the base form of the verb (without -s)."
            },
            {
                "id": "en-l3-q2",
                "text": "Which sentence contains an Oxford comma?",
                "options": [
                    "I bought apples oranges and bananas.",
                    "I bought apples, oranges and bananas.",
                    "I bought apples, oranges, and bananas.",
                    "I bought apples and oranges and bananas."
                ],
                "answer": "I bought apples, oranges, and bananas.",
                "explanation": "The Oxford comma is the comma used after the penultimate item in a list of three or more items."
            },
            {
                "id": "en-l3-q3",
                "text": "Which sentence uses the passive voice correctly?",
                "options": [
                    "The experiment was conducted by the scientist.",
                    "The scientist conducted the experiment.",
                    "The experiment conducting by the scientist.",
                    "The scientist was conducted the experiment."
                ],
                "answer": "The experiment was conducted by the scientist.",
                "explanation": "In passive voice, the subject (the experiment) receives the action, and the agent (the scientist) is introduced with 'by'."
            },
            {
                "id": "en-l3-q4",
                "text": "Which of the following is a dangling modifier?",
                "options": [
                    "Walking down the street, she saw a cat.",
                    "Walking down the street, a cat was seen.",
                    "She saw a cat while walking down the street.",
                    "The cat was seen by her while walking down the street."
                ],
                "answer": "Walking down the street, a cat was seen.",
                "explanation": "A dangling modifier is a word or phrase that modifies a word not clearly stated in the sentence. In this case, 'walking down the street' seems to modify 'a cat' which doesn't make logical sense."
            },
            {
                "id": "en-l3-q5",
                "text": "Choose the sentence with the correct use of the subjunctive mood:",
                "options": [
                    "I wish I was taller.",
                    "I wish I were taller.",
                    "I wish I am taller.",
                    "I wish I be taller."
                ],
                "answer": "I wish I were taller.",
                "explanation": "After 'wish' we use the past subjunctive ('were') for all persons, not 'was', to talk about unreal or hypothetical situations."
            }
        ]
    ]
}

# Pretest questions
PRETEST_QUESTIONS = {
    'id': [
        # Multiple Choice
        {
            "id": "pre-id-mc-1",
            "type": "multiple_choice",
            "text": "Manakah dari berikut ini yang merupakan kata kerja?",
            "options": ["makan", "rumah", "cantik", "cepat"],
            "answer": "makan",
            "weight": 1
        },
        {
            "id": "pre-id-mc-2",
            "type": "multiple_choice",
            "text": "Manakah kalimat berikut yang memiliki struktur S-P-O yang benar?",
            "options": [
                "Ke sekolah pergi Ani.", 
                "Ani pergi ke sekolah.", 
                "Pergi Ani ke sekolah.", 
                "Sekolah Ani pergi ke."
            ],
            "answer": "Ani pergi ke sekolah.",
            "weight": 1
        },
        # Essay
        {
            "id": "pre-id-essay-1",
            "type": "essay",
            "text": "Tuliskan sebuah paragraf pendek tentang hobi Anda (minimal 50 kata).",
            "min_words": 50,
            "keywords": ["saya", "hobi", "waktu", "senang", "kegiatan"],
            "weight": 3
        },
        # True/False
        {
            "id": "pre-id-tf-1",
            "type": "true_false",
            "text": "Kata 'berlari' adalah kata kerja.",
            "answer": True,
            "weight": 1
        },
        # Fill in the blank
        {
            "id": "pre-id-fill-1",
            "type": "fill_blank",
            "text": "Saya ___ ke sekolah setiap hari.",
            "answer": ["pergi", "berangkat", "berjalan"],
            "weight": 1
        }
    ],
    'en': [
        # Multiple Choice
        {
            "id": "pre-en-mc-1",
            "type": "multiple_choice",
            "text": "Which of the following is a verb?",
            "options": ["eat", "house", "beautiful", "fast"],
            "answer": "eat",
            "weight": 1
        },
        {
            "id": "pre-en-mc-2",
            "type": "multiple_choice",
            "text": "Which sentence has the correct subject-verb agreement?",
            "options": [
                "The team are playing well.",
                "The team is playing well.",
                "The teams is playing well.",
                "The teams were plays well."
            ],
            "answer": "The team is playing well.",
            "weight": 1
        },
        {
            "id": "pre-en-mc-3",
            "type": "multiple_choice",
            "text": "Choose the correct form of the adjective: This is the ___ book I've ever read.",
            "options": ["good", "better", "best", "goodest"],
            "answer": "best",
            "weight": 1
        },
        {
            "id": "pre-en-mc-4",
            "type": "multiple_choice",
            "text": "Which of these is a proper noun?",
            "options": ["city", "country", "London", "mountain"],
            "answer": "London",
            "weight": 1
        },
        {
            "id": "pre-en-mc-5",
            "type": "multiple_choice",
            "text": "Which sentence uses the past continuous tense correctly?",
            "options": [
                "I was walking when I saw the accident.",
                "I walking when I saw the accident.",
                "I were walking when I saw the accident.",
                "I am walking when I saw the accident."
            ],
            "answer": "I was walking when I saw the accident.",
            "weight": 1
        },
        # Essay
        {
            "id": "pre-en-essay-1",
            "type": "essay",
            "text": "Write a short paragraph about your hobby (minimum 50 words).",
            "min_words": 50,
            "keywords": ["I", "hobby", "time", "enjoy", "activity"],
            "weight": 3
        },
        {
            "id": "pre-en-essay-2",
            "type": "essay",
            "text": "Describe your favorite place to visit (minimum 60 words).",
            "min_words": 60,
            "keywords": ["place", "favorite", "visit", "experience", "memories"],
            "weight": 3
        },
        # True/False
        {
            "id": "pre-en-tf-1", 
            "type": "true_false",
            "text": "The word 'running' is a verb.",
            "answer": True,
            "weight": 1
        },
        {
            "id": "pre-en-tf-2", 
            "type": "true_false",
            "text": "In English, adjectives usually come after the noun they describe.",
            "answer": False,
            "weight": 1
        },
        # Fill in the blank
        {
            "id": "pre-en-fill-1",
            "type": "fill_blank",
            "text": "I ___ to school every day.",
            "answer": ["go", "walk", "travel", "commute"],
            "weight": 1
        },
        {
            "id": "pre-en-fill-2",
            "type": "fill_blank",
            "text": "She ___ her homework before dinner.",
            "answer": ["finished", "completed", "did", "submitted"],
            "weight": 1
        }
    ]
}

# Post-test questions by level
POST_TEST_QUESTIONS = {
    'id': {
        # Level 1 Post-test
        1: [
            {
                "id": "post-id-l1-mc-1",
                "type": "multiple_choice",
                "text": "Apa kata ganti orang pertama tunggal dalam bahasa Indonesia?",
                "options": ["saya", "kamu", "dia", "mereka"],
                "answer": "saya",
                "weight": 1
            },
            {
                "id": "post-id-l1-essay-1",
                "type": "essay",
                "text": "Tuliskan minimal 3 kalimat tentang kegiatan sehari-hari Anda.",
                "min_words": 30,
                "keywords": ["bangun", "makan", "tidur", "bekerja", "sekolah"],
                "weight": 3
            },
            {
                "id": "post-id-l1-tf-1",
                "type": "true_false",
                "text": "Kata 'tidak' digunakan untuk menyangkal pernyataan dalam bahasa Indonesia.",
                "answer": True,
                "weight": 1
            }
        ],
        # Level 2 Post-test
        2: [
            {
                "id": "post-id-l2-mc-1",
                "type": "multiple_choice",
                "text": "Manakah dari berikut yang merupakan contoh kalimat pasif?",
                "options": [
                    "Saya membaca buku.", 
                    "Buku itu dibaca oleh saya.", 
                    "Membaca buku itu menyenangkan.", 
                    "Bacalah buku itu!"
                ],
                "answer": "Buku itu dibaca oleh saya.",
                "weight": 1
            },
            {
                "id": "post-id-l2-essay-1",
                "type": "essay",
                "text": "Jelaskan perbedaan antara kata kerja aktif dan pasif dalam bahasa Indonesia. Berikan contoh masing-masing.",
                "min_words": 50,
                "keywords": ["aktif", "pasif", "subjek", "objek", "di-", "me-"],
                "weight": 3
            }
        ],
        # Level 3 Post-test
        3: [
            {
                "id": "post-id-l3-mc-1",
                "type": "multiple_choice",
                "text": "Manakah kalimat berikut yang menggunakan majas personifikasi?",
                "options": [
                    "Dia cantik seperti bunga.", 
                    "Angin berbisik di telingaku.", 
                    "Gedung itu sangat tinggi.", 
                    "Mereka berlari sangat cepat."
                ],
                "answer": "Angin berbisik di telingaku.",
                "weight": 1
            },
            {
                "id": "post-id-l3-essay-1",
                "type": "essay",
                "text": "Tuliskan sebuah paragraf argumentatif tentang pentingnya mempelajari bahasa asing.",
                "min_words": 100,
                "keywords": ["penting", "global", "komunikasi", "budaya", "karir", "pendidikan"],
                "weight": 5
            }
        ]
    },
    'en': {
        # Level 1 Post-test
        1: [
            {
                "id": "post-en-l1-mc-1",
                "type": "multiple_choice",
                "text": "What is the first person singular pronoun in English?",
                "options": ["I", "you", "he", "they"],
                "answer": "I",
                "weight": 1
            },
            {
                "id": "post-en-l1-mc-2",
                "type": "multiple_choice",
                "text": "Which of the following is a plural noun?",
                "options": ["child", "person", "women", "man"],
                "answer": "women",
                "weight": 1
            },
            {
                "id": "post-en-l1-mc-3",
                "type": "multiple_choice",
                "text": "What is the past tense of 'go'?",
                "options": ["goed", "gone", "went", "going"],
                "answer": "went",
                "weight": 1
            },
            {
                "id": "post-en-l1-tf-1",
                "type": "true_false",
                "text": "The word 'beautiful' is an adjective.",
                "answer": True,
                "weight": 1
            },
            {
                "id": "post-en-l1-tf-2",
                "type": "true_false",
                "text": "The present continuous tense is formed with 'will' + verb.",
                "answer": False,
                "weight": 1
            },
            {
                "id": "post-en-l1-fill-1",
                "type": "fill_blank",
                "text": "She ___ breakfast every morning at 7 AM.",
                "answer": ["has", "eats", "takes", "makes"],
                "weight": 1
            },
            {
                "id": "post-en-l1-essay-1",
                "type": "essay",
                "text": "Write at least 3 sentences about your daily routine.",
                "min_words": 30,
                "keywords": ["wake", "eat", "work", "study", "sleep"],
                "weight": 3
            }
        ],
        # Level 2 Post-test
        2: [
            {
                "id": "post-en-l2-mc-1",
                "type": "multiple_choice",
                "text": "Which of these sentences is in the passive voice?",
                "options": [
                    "John wrote the letter.",
                    "The letter was written by John.",
                    "John is writing the letter.",
                    "John will write the letter."
                ],
                "answer": "The letter was written by John.",
                "weight": 1
            },
            {
                "id": "post-en-l2-mc-2",
                "type": "multiple_choice",
                "text": "Choose the correct reported speech: He said, 'I am working.'",
                "options": [
                    "He said that he is working.",
                    "He said that he was working.",
                    "He said that I am working.",
                    "He said that I was working."
                ],
                "answer": "He said that he was working.",
                "weight": 1
            },
            {
                "id": "post-en-l2-mc-3",
                "type": "multiple_choice",
                "text": "Which sentence uses a modal verb correctly?",
                "options": [
                    "I must to go now.",
                    "She can swimming very well.",
                    "They might be late.",
                    "He should to study harder."
                ],
                "answer": "They might be late.",
                "weight": 1
            },
            {
                "id": "post-en-l2-tf-1",
                "type": "true_false",
                "text": "In the sentence 'If I had studied, I would have passed the exam,' the tense used is past perfect.",
                "answer": True,
                "weight": 1
            },
            {
                "id": "post-en-l2-fill-1",
                "type": "fill_blank",
                "text": "I wish I ___ more time to finish the project.",
                "answer": ["had", "have", "would have", "having"],
                "weight": 1
            },
            {
                "id": "post-en-l2-essay-1",
                "type": "essay",
                "text": "Explain the difference between active and passive voice in English. Give examples of each.",
                "min_words": 50,
                "keywords": ["active", "passive", "subject", "object", "by", "agent"],
                "weight": 3
            }
        ],
        # Level 3 Post-test
        3: [
            {
                "id": "post-en-l3-mc-1",
                "type": "multiple_choice",
                "text": "Which sentence contains a participle phrase?",
                "options": [
                    "I think that he is right.",
                    "Walking to school, I saw my friend.",
                    "The boy who lives next door is friendly.",
                    "She said she would come later."
                ],
                "answer": "Walking to school, I saw my friend.",
                "weight": 1
            },
            {
                "id": "post-en-l3-mc-2",
                "type": "multiple_choice",
                "text": "Which of these is an example of the subjunctive mood?",
                "options": [
                    "She runs every morning.",
                    "He suggested that the meeting be postponed.",
                    "They were watching a movie.",
                    "I will visit Paris next year."
                ],
                "answer": "He suggested that the meeting be postponed.",
                "weight": 1
            },
            {
                "id": "post-en-l3-mc-3",
                "type": "multiple_choice",
                "text": "Identify the sentence that uses a gerund:",
                "options": [
                    "To swim is good exercise.",
                    "Swimming is good exercise.",
                    "She swims every day.",
                    "She should swim more often."
                ],
                "answer": "Swimming is good exercise.",
                "weight": 1
            },
            {
                "id": "post-en-l3-tf-1",
                "type": "true_false",
                "text": "A restrictive clause provides essential information and doesn't need commas.",
                "answer": True,
                "weight": 1
            },
            {
                "id": "post-en-l3-fill-1",
                "type": "fill_blank",
                "text": "Had I known about the problem earlier, I ___ able to help.",
                "answer": ["would have been", "would be", "will be", "had been"],
                "weight": 1
            },
            {
                "id": "post-en-l3-essay-1",
                "type": "essay",
                "text": "Write an argumentative paragraph about the importance of learning foreign languages.",
                "min_words": 100,
                "keywords": ["important", "global", "communication", "culture", "career", "education"],
                "weight": 5
            }
        ]
    }
}

def get_questions(level, count=3, language='en'):
    """
    Get questions based on user level
    """
    # Convert level to integer if it's not already
    level = int(level) if not isinstance(level, int) else level
    
    # Ensure level is between 1 and 3
    level = max(1, min(level, 3))
    
    # Get questions for the specified level and language
    available_questions = QUESTIONS.get(language, QUESTIONS['en'])[level-1]
    
    # Limit number of questions
    count = min(count, len(available_questions))
    
    # Randomly select questions
    selected_questions = random.sample(available_questions, count)
    
    return selected_questions

def evaluate_answer(user_answer, question_id, current_level):
    """
    Evaluate user's answer and adjust level if needed
    """
    # Ensure current_level is an integer
    current_level = int(current_level) if not isinstance(current_level, int) else current_level
    
    # Find the question by ID
    question = None
    language = 'en'  # Default to English
    
    # Determine language from question ID
    if question_id.startswith('id-'):
        language = 'id'
    
    # Find the question in all levels
    for level_index, level_questions in enumerate(QUESTIONS[language]):
        for q in level_questions:
            if q['id'] == question_id:
                question = q
                break
        if question:
            break
    
    if not question:
        return False, "Question not found", current_level
    
    # Check if the answer is correct
    is_correct = user_answer == question['answer']
    
    # Prepare feedback
    if is_correct:
        feedback = "Benar! " + question['explanation'] if language == 'id' else "Correct! " + question['explanation']
    else:
        feedback = f"Salah. Jawaban yang benar adalah '{question['answer']}'. " + question['explanation'] if language == 'id' else f"Incorrect. The correct answer is '{question['answer']}'. " + question['explanation']
    
    # Adjust level based on performance
    new_level = current_level
    
    # If user gets a question right at their current level, consider increasing level
    if is_correct and current_level < 3:
        # Check if the question was from the current level
        question_level = int(question_id.split('-l')[1][0])
        if question_level == current_level:
            # Simple 50% chance to increase level if correct
            if random.random() > 0.5:
                new_level = current_level + 1
    
    # If user gets a question wrong, consider decreasing level
    elif not is_correct and current_level > 1:
        # Simple 50% chance to decrease level if incorrect
        if random.random() > 0.5:
            new_level = current_level - 1
    
    return is_correct, feedback, new_level 

# New functions for pretest
def get_pretest_questions(language='en', count=10):
    """
    Get pretest questions for a specific language.
    Optionally specify how many questions to return (randomized).
    """
    all_questions = PRETEST_QUESTIONS.get(language, PRETEST_QUESTIONS['en']).copy()
    
    # If count is specified and less than total questions, select random subset
    if count and count < len(all_questions):
        # Ensure we have at least one question of each type
        mc_questions = [q for q in all_questions if q['type'] == 'multiple_choice']
        tf_questions = [q for q in all_questions if q['type'] == 'true_false']
        essay_questions = [q for q in all_questions if q['type'] == 'essay']
        fill_questions = [q for q in all_questions if q['type'] == 'fill_blank']
        
        selected_questions = []
        
        # Add at least one of each type if available
        types = [
            (mc_questions, 1, 3),  # At least 1, up to 3 multiple choice
            (tf_questions, 1, 2),  # At least 1, up to 2 true/false
            (essay_questions, 1, 2),  # At least 1, up to 2 essays
            (fill_questions, 1, 2),  # At least 1, up to 2 fill blanks
        ]
        
        # First pass: add minimum number of each type
        remaining_count = count
        for question_list, min_count, max_count in types:
            if question_list and min_count <= len(question_list):
                # Take minimum count of this type
                selected = random.sample(question_list, min(min_count, len(question_list)))
                selected_questions.extend(selected)
                remaining_count -= len(selected)
        
        # Second pass: fill remaining slots randomly, respecting max counts
        if remaining_count > 0:
            candidates = []
            for question_list, min_count, max_count in types:
                # Get questions of this type that aren't already selected
                already_selected_ids = [q['id'] for q in selected_questions]
                remaining_questions = [q for q in question_list if q['id'] not in already_selected_ids]
                
                # Count how many of this type we've already selected
                type_selected = len([q for q in selected_questions if q['type'] == question_list[0]['type']]) if question_list else 0
                
                # Calculate how many more we can add of this type
                can_add = max(0, max_count - type_selected) if max_count else len(remaining_questions)
                
                # Add eligible questions to candidates
                candidates.extend(remaining_questions[:can_add])
            
            # Randomly select from candidates to fill remaining slots
            if candidates and remaining_count > 0:
                additional = random.sample(candidates, min(remaining_count, len(candidates)))
                selected_questions.extend(additional)
        
        return selected_questions
    
    # Otherwise return all questions, shuffled
    random.shuffle(all_questions)
    return all_questions

def evaluate_pretest_answers(answers, language='en'):
    """
    Evaluate pretest answers and determine the user's initial level
    
    Args:
        answers: Dictionary of user answers with question IDs as keys
        language: Language code ('id' or 'en')
        
    Returns:
        Dict with score, percentage, and assigned level
    """
    # Get all questions of the language
    all_questions = PRETEST_QUESTIONS.get(language, PRETEST_QUESTIONS['en'])
    
    # Filter to only the questions that were answered
    question_ids = answers.keys()
    questions = [q for q in all_questions if q['id'] in question_ids]
    
    total_points = 0
    earned_points = 0
    correct_count = 0
    
    # Calculate total possible points
    for question in questions:
        total_points += question['weight']
    
    # Evaluate each answer
    for question in questions:
        question_id = question['id']
        if question_id not in answers:
            continue
            
        user_answer = answers[question_id]
        question_type = question['type']
        
        if question_type == 'multiple_choice':
            if user_answer == question['answer']:
                earned_points += question['weight']
                correct_count += 1
                
        elif question_type == 'true_false':
            user_bool = user_answer.lower() == 'true' if isinstance(user_answer, str) else user_answer
            if user_bool == question['answer']:
                earned_points += question['weight']
                correct_count += 1
                
        elif question_type == 'fill_blank':
            if user_answer.lower() in [ans.lower() for ans in question['answer']]:
                earned_points += question['weight']
                correct_count += 1
                
        elif question_type == 'essay':
            # For essays, use simple keyword checking and word count
            word_count = len(user_answer.split())
            if word_count >= question['min_words']:
                # Check for keywords
                keyword_count = sum(1 for keyword in question['keywords'] 
                                   if keyword.lower() in user_answer.lower())
                
                # Award partial points based on keyword presence
                keyword_ratio = keyword_count / len(question['keywords'])
                awarded_points = question['weight'] * min(1.0, keyword_ratio)
                earned_points += awarded_points
    
    # Calculate percentage score
    percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
    
    # Determine level based on percentage
    if percentage >= 80:
        level = 3
    elif percentage >= 50:
        level = 2
    else:
        level = 1
        
    return {
        'score': round(earned_points, 1),
        'total_points': total_points,
        'percentage': round(percentage, 1),
        'level': level,
        'correct_count': correct_count,
        'total_questions': len(questions)
    }

# New functions for post-test
def get_post_test_questions(level, language='en', count=None):
    """
    Get post-test questions for a specific level and language.
    Optionally specify count to randomize the questions.
    """
    level_int = int(level) if not isinstance(level, int) else level
    level_int = max(1, min(level_int, 3))  # Ensure level is between 1 and 3
    
    # Get questions for the level and language
    language_questions = POST_TEST_QUESTIONS.get(language, POST_TEST_QUESTIONS['en'])
    available_questions = language_questions.get(level_int, []).copy()
    
    # If count specified and less than available, select random subset
    if count and count < len(available_questions):
        # Ensure we have at least one of each question type if possible
        mc_questions = [q for q in available_questions if q['type'] == 'multiple_choice']
        tf_questions = [q for q in available_questions if q['type'] == 'true_false']
        essay_questions = [q for q in available_questions if q['type'] == 'essay']
        fill_questions = [q for q in available_questions if q['type'] == 'fill_blank']
        
        # Try to select at least one of each type
        selected_questions = []
        for question_list in [mc_questions, tf_questions, essay_questions, fill_questions]:
            if question_list:
                selected_questions.append(random.choice(question_list))
        
        # If we have more slots to fill, randomly select more questions
        remaining_slots = count - len(selected_questions)
        if remaining_slots > 0:
            # Get all questions we haven't selected yet
            already_selected_ids = [q['id'] for q in selected_questions]
            remaining_questions = [q for q in available_questions if q['id'] not in already_selected_ids]
            
            # Add more random questions
            if remaining_questions:
                additional = random.sample(remaining_questions, min(remaining_slots, len(remaining_questions)))
                selected_questions.extend(additional)
        
        # Shuffle the final selection
        random.shuffle(selected_questions)
        return selected_questions
    
    # Otherwise return all questions, shuffled
    random.shuffle(available_questions)
    return available_questions

def evaluate_post_test_answers(answers, level, language='en'):
    """
    Evaluate post-test answers to determine if the user can move to the next level
    
    Args:
        answers: Dictionary of user answers with question IDs as keys
        level: Current user level
        language: Language code ('id' or 'en')
        
    Returns:
        Dict with score, percentage, pass/fail status, and new level
    """
    level_int = int(level) if not isinstance(level, int) else level
    level_int = max(1, min(level_int, 3))  # Ensure level is between 1 and 3
    
    language_questions = POST_TEST_QUESTIONS.get(language, POST_TEST_QUESTIONS['en'])
    all_questions = language_questions.get(level_int, [])
    
    # Filter to only questions that were answered
    question_ids = answers.keys()
    questions = [q for q in all_questions if q['id'] in question_ids]
    
    # If no questions for this level, user automatically passes
    if not questions:
        return {
            'score': 0,
            'total_points': 0,
            'percentage': 100,
            'passed': True,
            'new_level': min(level_int + 1, 3),
            'correct_count': 0,
            'total_questions': 0
        }
    
    total_points = 0
    earned_points = 0
    correct_count = 0
    
    # Calculate total possible points
    for question in questions:
        total_points += question['weight']
    
    # Evaluate each answer
    for question in questions:
        question_id = question['id']
        if question_id not in answers:
            continue
            
        user_answer = answers[question_id]
        question_type = question['type']
        
        if question_type == 'multiple_choice':
            if user_answer == question['answer']:
                earned_points += question['weight']
                correct_count += 1
                
        elif question_type == 'true_false':
            user_bool = user_answer.lower() == 'true' if isinstance(user_answer, str) else user_answer
            if user_bool == question['answer']:
                earned_points += question['weight']
                correct_count += 1
                
        elif question_type == 'fill_blank':
            if user_answer.lower() in [ans.lower() for ans in question['answer']]:
                earned_points += question['weight']
                correct_count += 1
                
        elif question_type == 'essay':
            # For essays, use simple keyword checking and word count
            word_count = len(user_answer.split())
            if word_count >= question['min_words']:
                # Check for keywords
                keyword_count = sum(1 for keyword in question['keywords'] 
                                   if keyword.lower() in user_answer.lower())
                
                # Award partial points based on keyword presence
                keyword_ratio = keyword_count / len(question['keywords'])
                awarded_points = question['weight'] * min(1.0, keyword_ratio)
                earned_points += awarded_points
    
    # Calculate percentage score
    percentage = (earned_points / total_points) * 100 if total_points > 0 else 0
    
    # Determine if the user passed (need 70% to pass)
    passed = percentage >= 70
    
    # Determine new level
    new_level = level_int + 1 if passed and level_int < 3 else level_int
    
    return {
        'score': round(earned_points, 1),
        'total_points': total_points,
        'percentage': round(percentage, 1),
        'passed': passed,
        'new_level': new_level,
        'correct_count': correct_count,
        'total_questions': len(questions)
    }

# Function to check if user has taken pretest
def has_completed_pretest(user_data):
    """Check if user has completed the pretest"""
    return user_data and 'pretest_completed' in user_data and user_data['pretest_completed']

# Function to get the appropriate learning materials based on user's level
def get_learning_materials(level, language='en'):
    """Get learning materials appropriate for user's level"""
    level_int = int(level) if not isinstance(level, int) else level
    
    materials = {
        'id': {
            1: [
                {
                    "title": "Dasar Tata Bahasa Indonesia",
                    "description": "Mempelajari struktur kalimat dasar dan kata kerja umum dalam bahasa Indonesia",
                    "content_type": "article",
                    "url": "/materials/id/beginner/grammar_basics.html"
                },
                {
                    "title": "Kosakata Dasar Sehari-hari",
                    "description": "100 kata yang sering digunakan dalam percakapan sehari-hari",
                    "content_type": "vocabulary",
                    "url": "/materials/id/beginner/essential_vocabulary.html"
                },
                {
                    "title": "Percakapan Dasar",
                    "description": "Dialog sederhana untuk situasi umum",
                    "content_type": "dialogue",
                    "url": "/materials/id/beginner/basic_conversations.html"
                }
            ],
            2: [
                {
                    "title": "Struktur Kalimat Kompleks",
                    "description": "Mempelajari kalimat majemuk dan penggunaan kata hubung",
                    "content_type": "article",
                    "url": "/materials/id/intermediate/complex_sentences.html"
                },
                {
                    "title": "Imbuhan dalam Bahasa Indonesia",
                    "description": "Penggunaan awalan, akhiran, dan sisipan dalam bahasa Indonesia",
                    "content_type": "article",
                    "url": "/materials/id/intermediate/affixes.html"
                }
            ],
            3: [
                {
                    "title": "Majas dan Gaya Bahasa",
                    "description": "Penggunaan majas dan gaya bahasa dalam tulisan formal dan sastra",
                    "content_type": "article",
                    "url": "/materials/id/advanced/figures_of_speech.html"
                },
                {
                    "title": "Penulisan Akademik",
                    "description": "Panduan menulis esai dan makalah akademik dalam bahasa Indonesia",
                    "content_type": "article",
                    "url": "/materials/id/advanced/academic_writing.html"
                }
            ]
        },
        'en': {
            1: [
                {
                    "title": "Basic English Grammar",
                    "description": "Learn basic sentence structures and common verbs in English",
                    "content_type": "article",
                    "url": "/materials/en/beginner/grammar_basics.html"
                },
                {
                    "title": "Essential Everyday Vocabulary",
                    "description": "100 commonly used words in daily conversations",
                    "content_type": "vocabulary",
                    "url": "/materials/en/beginner/essential_vocabulary.html"
                },
                {
                    "title": "Basic Conversations",
                    "description": "Simple dialogues for common situations",
                    "content_type": "dialogue",
                    "url": "/materials/en/beginner/basic_conversations.html"
                },
                {
                    "title": "Present Simple vs Present Continuous",
                    "description": "Understanding the difference between present tenses",
                    "content_type": "article",
                    "url": "/materials/en/beginner/present_tenses.html"
                }
            ],
            2: [
                {
                    "title": "Complex Sentence Structures",
                    "description": "Learn compound sentences and connectors",
                    "content_type": "article",
                    "url": "/materials/en/intermediate/complex_sentences.html"
                },
                {
                    "title": "Past Tenses in English",
                    "description": "Understanding the past simple, past continuous, and past perfect",
                    "content_type": "article",
                    "url": "/materials/en/intermediate/past_tenses.html"
                },
                {
                    "title": "Conditionals and Reported Speech",
                    "description": "Advanced grammatical structures for intermediate learners",
                    "content_type": "article",
                    "url": "/materials/en/intermediate/conditionals.html"
                }
            ],
            3: [
                {
                    "title": "Advanced English Grammar",
                    "description": "Complex structures including subjunctive mood and inversion",
                    "content_type": "article",
                    "url": "/materials/en/advanced/advanced_grammar.html"
                },
                {
                    "title": "Academic Writing",
                    "description": "How to write essays and academic papers in English",
                    "content_type": "article",
                    "url": "/materials/en/advanced/academic_writing.html"
                },
                {
                    "title": "Business English and Presentations",
                    "description": "Formal English for professional settings",
                    "content_type": "article",
                    "url": "/materials/en/advanced/business_english.html"
                },
                {
                    "title": "Literary Analysis",
                    "description": "Understanding metaphors, idioms, and figurative language",
                    "content_type": "article",
                    "url": "/materials/en/advanced/literary_analysis.html"
                }
            ]
        }
    }
    
    return materials.get(language, materials['en']).get(level_int, []) 
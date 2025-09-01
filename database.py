import psycopg2
import psycopg2.extras
from psycopg2 import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
        self.initialize_words()
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'english_bot'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'password'),
                port=os.getenv('DB_PORT', '5432')
            )
            print("Database connection established successfully")
        except Error as e:
            print(f"Database connection error: {e}")
    
    def create_tables(self):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS common_words (
                    id SERIAL PRIMARY KEY,
                    english_word VARCHAR(255) UNIQUE NOT NULL,
                    translation_word VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_words (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                    english_word VARCHAR(255) NOT NULL,
                    translation_word VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, english_word)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_stats (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                    word_id INTEGER,
                    word_type VARCHAR(20),
                    correct_answers INTEGER DEFAULT 0,
                    wrong_answers INTEGER DEFAULT 0,
                    last_practiced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            cursor.close()
            print("Tables created successfully")
            
        except Error as e:
            print(f"Error creating tables: {e}")
    
    def initialize_words(self):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM common_words")
            count = cursor.fetchone()[0]
            
            if count == 0:
                basic_words = [
                    ('Peace', 'Peace', 'Basic'),
                    ('Hello', 'Hello', 'Greetings'),
                    ('Goodbye', 'Goodbye', 'Greetings'),
                    ('Car', 'Car', 'Transport'),
                    ('House', 'House', 'Housing'),
                    ('Red', 'Red', 'Colors'),
                    ('Blue', 'Blue', 'Colors'),
                    ('Green', 'Green', 'Colors'),
                    ('White', 'White', 'Colors'),
                    ('Black', 'Black', 'Colors'),
                    ('I', 'I', 'Pronouns'),
                    ('You', 'You', 'Pronouns'),
                    ('He', 'He', 'Pronouns'),
                    ('She', 'She', 'Pronouns'),
                    ('We', 'We', 'Pronouns')
                ]
                
                cursor.executemany(
                    "INSERT INTO common_words (english_word, translation_word, category) VALUES (%s, %s, %s)",
                    basic_words
                )
                
                self.connection.commit()
                print(f"Added {len(basic_words)} basic words")
            
            cursor.close()
            
        except Error as e:
            print(f"Error initializing words: {e}")
    
    def add_user(self, user_id, username, first_name, last_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name
            """, (user_id, username, first_name, last_name))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False
    
    def get_random_word(self, user_id):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN uw.id IS NOT NULL THEN 'user'
                        ELSE 'common'
                    END as word_type,
                    COALESCE(uw.english_word, cw.english_word) as english_word,
                    COALESCE(uw.translation_word, cw.translation_word) as translation_word,
                    COALESCE(uw.id, cw.id) as word_id
                FROM (
                    SELECT id, english_word, translation_word, created_at, NULL as user_id FROM common_words 
                    UNION ALL 
                    SELECT id, english_word, translation_word, created_at, user_id FROM user_words 
                    WHERE user_id = %s
                ) AS all_words
                LEFT JOIN user_words uw ON all_words.id = uw.id AND all_words.user_id = uw.user_id
                LEFT JOIN common_words cw ON all_words.id = cw.id
                ORDER BY RANDOM()
                LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'word_type': result[0],
                    'english_word': result[1],
                    'translation_word': result[2],
                    'word_id': result[3]
                }
            return None
            
        except Error as e:
            print(f"Error getting random word: {e}")
            return None
    
    def get_random_words_for_quiz(self, user_id, target_word, count=3):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT english_word FROM (
                    SELECT english_word FROM common_words 
                    UNION ALL 
                    SELECT english_word FROM user_words WHERE user_id = %s
                ) AS all_words
                WHERE english_word != %s
                ORDER BY RANDOM()
                LIMIT %s
            """, (user_id, target_word, count))
            
            words = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return words
            
        except Error as e:
            print(f"Error getting words for quiz: {e}")
            return []
    
    def get_random_words_for_quiz_with_translations(self, user_id, target_word, count=3):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT translation_word FROM (
                    SELECT translation_word FROM common_words 
                    UNION ALL 
                    SELECT translation_word FROM user_words WHERE user_id = %s
                ) AS all_words
                WHERE translation_word != (
                    SELECT translation_word FROM common_words WHERE english_word = %s
                    UNION ALL
                    SELECT translation_word FROM user_words WHERE user_id = %s AND english_word = %s
                    LIMIT 1
                )
                ORDER BY RANDOM()
                LIMIT %s
            """, (user_id, target_word, user_id, target_word, count))
            
            words = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return words
            
        except Error as e:
            print(f"Error getting words for quiz with translations: {e}")
            return []
    
    def add_user_word(self, user_id, english_word, translation_word):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO user_words (user_id, english_word, translation_word)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, english_word) DO UPDATE SET
                translation_word = EXCLUDED.translation_word
            """, (user_id, english_word, translation_word))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error adding user word: {e}")
            return False
    
    def delete_user_word(self, user_id, english_word):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM user_words 
                WHERE user_id = %s AND english_word = %s
            """, (user_id, english_word))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"Error deleting user word: {e}")
            return False
    
    def get_user_words_count(self, user_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM user_words WHERE user_id = %s
            """, (user_id,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error as e:
            print(f"Error getting user word count: {e}")
            return 0
    
    def get_database_stats(self):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM common_words")
            common_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_words")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'common_words': common_count,
                'user_words': user_count,
                'users': users_count
            }
        except Error as e:
            print(f"Error getting database stats: {e}")
            return None
    
    def get_user_words(self, user_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT english_word, translation_word FROM user_words 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (user_id,))
            words = cursor.fetchall()
            cursor.close()
            return words
        except Error as e:
            print(f"Error getting user words: {e}")
            return []
    
    def update_learning_stats(self, user_id, word_id, word_type, is_correct):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT id FROM learning_stats 
                WHERE user_id = %s AND word_id = %s AND word_type = %s
            """, (user_id, word_id, word_type))
            
            existing = cursor.fetchone()
            
            if existing:
                if is_correct:
                    cursor.execute("""
                        UPDATE learning_stats 
                        SET correct_answers = correct_answers + 1, last_practiced = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (existing[0],))
                else:
                    cursor.execute("""
                        UPDATE learning_stats 
                        SET wrong_answers = wrong_answers + 1, last_practiced = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (existing[0],))
            else:
                if is_correct:
                    cursor.execute("""
                        INSERT INTO learning_stats (user_id, word_id, word_type, correct_answers)
                        VALUES (%s, %s, %s, 1)
                    """, (user_id, word_id, word_type))
                else:
                    cursor.execute("""
                        INSERT INTO learning_stats (user_id, word_id, word_type, wrong_answers)
                        VALUES (%s, %s, %s, 1)
                    """, (user_id, word_id, word_type))
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error updating statistics: {e}")
            return False
    
    def close(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed") 
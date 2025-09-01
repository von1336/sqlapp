CREATE DATABASE english_bot;

\c english_bot;

CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE common_words (
    id SERIAL PRIMARY KEY,
    english_word VARCHAR(255) UNIQUE NOT NULL,
    translation_word VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_words (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    english_word VARCHAR(255) NOT NULL,
    translation_word VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, english_word)
);

CREATE TABLE learning_stats (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    word_id BIGINT,
    word_type VARCHAR(50),
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    last_practiced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_common_words_english ON common_words(english_word);
CREATE INDEX idx_user_words_user_id ON user_words(user_id);
CREATE INDEX idx_user_words_english ON user_words(english_word);
CREATE INDEX idx_learning_stats_user_id ON learning_stats(user_id);
CREATE INDEX idx_learning_stats_word_id ON learning_stats(word_id);

INSERT INTO common_words (english_word, translation_word, category) VALUES
('Peace', 'Мир', 'Basic'),
('Hello', 'Привет', 'Greetings'),
('Goodbye', 'До свидания', 'Greetings'),
('Car', 'Машина', 'Transport'),
('House', 'Дом', 'Housing'),
('Red', 'Красный', 'Colors'),
('Blue', 'Синий', 'Colors'),
('Green', 'Зеленый', 'Colors'),
('White', 'Белый', 'Colors'),
('Black', 'Черный', 'Colors'),
('I', 'Я', 'Pronouns'),
('You', 'Ты', 'Pronouns'),
('He', 'Он', 'Pronouns'),
('She', 'Она', 'Pronouns'),
('We', 'Мы', 'Pronouns');

SELECT COUNT(*) as total_words FROM common_words;

SELECT COUNT(*) as total_users FROM users;

SELECT COUNT(*) as total_user_words FROM user_words;

SELECT COUNT(*) as total_stats FROM learning_stats; 
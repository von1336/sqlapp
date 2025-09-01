# English Learning Telegram Bot

## Project Overview

This project is a comprehensive English language learning system built as a Telegram bot with a PostgreSQL database backend and a custom GUI application for management. The system is designed to help users learn English vocabulary through interactive quizzes, personalized word management, and progress tracking.

## Core Features

### Telegram Bot Functionality
- **Interactive Word Quizzes**: Users receive Russian words and must select the correct English translation from multiple choice options
- **Personal Word Management**: Users can add custom words to their personal learning database
- **Word Deletion**: Users can remove words from their personal collection
- **Learning Statistics**: Tracks user progress and learning performance
- **Multi-language Interface**: Russian interface with English word content

### Database Management
- **PostgreSQL Integration**: Robust database backend for data persistence
- **User Management**: Stores user information and learning progress
- **Word Categories**: Organized vocabulary by themes (Basic, Greetings, Transport, Housing, Colors, Pronouns)
- **Learning Analytics**: Tracks correct/incorrect answers for performance analysis

### GUI Application
- **Bot Control**: Start, stop, and restart the Telegram bot
- **Database Connection Management**: Configure and test database connections
- **Real-time Monitoring**: View bot logs and system status
- **User-friendly Interface**: Modern dark theme with intuitive controls

## Technical Architecture

### System Components

#### 1. Telegram Bot (`bot.py`)
- **Framework**: pyTelegramBotAPI (telebot)
- **State Management**: Custom state machine for multi-step interactions
- **Data Persistence**: Global dictionary for user session management
- **Error Handling**: Comprehensive validation and user feedback
- **Quiz Logic**: Random word selection with multiple choice options

#### 2. Database Layer (`database.py`)
- **Database**: PostgreSQL with psycopg2 driver
- **Connection Pooling**: Efficient database connection management
- **Schema Design**: Four main tables with proper relationships
- **Data Operations**: CRUD operations for words, users, and statistics

#### 3. GUI Application (`gui_app.py`)
- **Framework**: CustomTkinter for modern UI
- **Process Management**: Subprocess handling for bot execution
- **Configuration**: Environment-based settings management
- **Logging**: Real-time log display and monitoring

### Database Schema

#### Tables Structure

**users**
- `user_id` (BIGINT, PRIMARY KEY)
- `username` (VARCHAR)
- `first_name` (VARCHAR)
- `last_name` (VARCHAR)
- `created_at` (TIMESTAMP)

**common_words**
- `id` (SERIAL, PRIMARY KEY)
- `english_word` (VARCHAR, UNIQUE)
- `translation_word` (VARCHAR)
- `category` (VARCHAR)
- `created_at` (TIMESTAMP)

**user_words**
- `id` (SERIAL, PRIMARY KEY)
- `user_id` (BIGINT, FOREIGN KEY)
- `english_word` (VARCHAR)
- `translation_word` (VARCHAR)
- `created_at` (TIMESTAMP)

**learning_stats**
- `id` (SERIAL, PRIMARY KEY)
- `user_id` (BIGINT, FOREIGN KEY)
- `word_id` (BIGINT)
- `word_type` (VARCHAR)
- `is_correct` (BOOLEAN)
- `created_at` (TIMESTAMP)

## Installation and Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Telegram Bot Token

### Dependencies
```
pyTelegramBotAPI==4.14.0
customtkinter==5.2.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
```

### Environment Configuration
Create a `.env` file with the following variables:
```
BOT_TOKEN=your_telegram_bot_token
DB_HOST=localhost
DB_NAME=english_bot
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

### Database Setup
1. Create PostgreSQL database: `english_bot`
2. Run the application - tables will be created automatically
3. Initial vocabulary will be populated with 15 basic words
4. Alternative: Use provided `database_schema.sql` for manual setup

## Usage Instructions

### Starting the System
1. **Launch GUI**: `python gui_app.py`
2. **Configure Database**: Enter connection details and test connection
3. **Start Bot**: Click "Start Bot" button
4. **Monitor Status**: Watch logs and system status in real-time

### Using the Telegram Bot
1. **Start Command**: Send `/start` to begin
2. **Word Quizzes**: Answer translation questions with multiple choice
3. **Add Words**: Use "добавить слово ➕" to add personal vocabulary
4. **Delete Words**: Use "удалить слово 🔙" to remove personal words
5. **View Stats**: Check "Статистика" for learning progress

### Bot Commands
- `/start` - Initialize bot and show main menu
- `/cards` - Generate new word quiz (handled automatically)

## Implementation Details

### Quiz Algorithm
1. **Word Selection**: Random selection from common and personal words
2. **Option Generation**: Correct answer + 3 random incorrect options
3. **Answer Validation**: Checks against valid options and correct answer
4. **Feedback System**: Immediate response with correct/incorrect feedback
5. **Progress Tracking**: Updates learning statistics for each answer

### Data Flow
1. **User Input** → **Message Handler** → **Data Validation**
2. **Database Query** → **Word Selection** → **Quiz Generation**
3. **User Answer** → **Answer Processing** → **Feedback Generation**
4. **Statistics Update** → **Next Word Selection** → **New Quiz**

### Error Handling
- **Input Validation**: Checks for empty or invalid responses
- **Database Errors**: Graceful fallback and user notification
- **Connection Issues**: Automatic reconnection attempts
- **User Feedback**: Clear error messages and guidance

## Performance Characteristics

### Scalability
- **User Sessions**: In-memory storage for active users
- **Database**: Efficient indexing and query optimization
- **Bot Processing**: Asynchronous message handling

### Reliability
- **Connection Management**: Robust database connection handling
- **Error Recovery**: Automatic retry mechanisms
- **Data Integrity**: Foreign key constraints and validation

## Development and Maintenance

### Code Structure
- **Modular Design**: Separate concerns for bot, database, and GUI
- **Clean Architecture**: Clear separation of business logic and presentation
- **Error Logging**: Comprehensive logging for debugging and monitoring

### Testing
- **Database Tests**: Connection and query validation
- **Bot Functionality**: Core quiz and management features
- **GUI Operations**: User interface functionality

### Future Enhancements
- **Advanced Analytics**: Detailed learning progress reports
- **Word Difficulty**: Adaptive difficulty based on user performance
- **Spaced Repetition**: Intelligent word review scheduling
- **Multi-language Support**: Additional language interfaces
- **Mobile App**: Native mobile application development

## Troubleshooting

### Common Issues
1. **Database Connection**: Verify PostgreSQL service and credentials
2. **Bot Token**: Ensure valid Telegram bot token in .env file
3. **Port Conflicts**: Check for available ports and firewall settings
4. **Dependencies**: Verify all Python packages are installed correctly

### Debug Information
- **Console Logs**: Detailed logging in bot and GUI applications
- **Database Logs**: PostgreSQL query and connection logs
- **Telegram API**: Bot API response and error information

## License and Attribution

This project is developed as an educational tool for English language learning. The system architecture and implementation demonstrate modern software development practices including:

- **API Integration**: Telegram Bot API integration
- **Database Design**: Relational database schema and optimization
- **User Interface**: Modern GUI development with CustomTkinter
- **Process Management**: Subprocess handling and system integration
- **Error Handling**: Comprehensive error management and user feedback

## Contact and Support

For technical support or feature requests, please refer to the project documentation or create an issue in the project repository.

---

**Note**: This project is designed for educational purposes and demonstrates practical implementation of a complete language learning system with modern web technologies and database management. 
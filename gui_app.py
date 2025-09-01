import customtkinter as ctk
import threading
import os
import sys
from dotenv import load_dotenv
from database import DatabaseManager
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class EnglishLearningBotGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("English Learning Bot - Management")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.db = None
        self.bot_process = None
        self.bot_running = False
        
        load_dotenv()
        
        self.setup_ui()
        self.check_database_connection()
    
    def setup_ui(self):
        title_label = ctk.CTkLabel(
            self.root, 
            text="English Learning Bot", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        self.create_database_frame()
        self.create_bot_control_frame()
        self.create_status_frame()
        self.create_log_frame()
    
    def create_database_frame(self):
        db_frame = ctk.CTkFrame(self.root)
        db_frame.pack(fill="x", padx=20, pady=10)
        
        db_title = ctk.CTkLabel(db_frame, text="Database", font=ctk.CTkFont(size=16, weight="bold"))
        db_title.pack(pady=10)
        
        db_params_frame = ctk.CTkFrame(db_frame)
        db_params_frame.pack(fill="x", padx=20, pady=10)
        
        host_frame = ctk.CTkFrame(db_params_frame)
        host_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(host_frame, text="Host:").pack(side="left", padx=10)
        self.host_entry = ctk.CTkEntry(host_frame, placeholder_text="localhost")
        self.host_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.host_entry.insert(0, os.getenv('DB_HOST', 'localhost'))
        
        db_name_frame = ctk.CTkFrame(db_params_frame)
        db_name_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(db_name_frame, text="Database:").pack(side="left", padx=10)
        self.db_name_entry = ctk.CTkEntry(db_name_frame, placeholder_text="english_bot")
        self.db_name_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.db_name_entry.insert(0, os.getenv('DB_NAME', 'english_bot'))
        
        user_frame = ctk.CTkFrame(db_params_frame)
        user_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(user_frame, text="User:").pack(side="left", padx=10)
        self.user_entry = ctk.CTkEntry(user_frame, placeholder_text="postgres")
        self.user_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.user_entry.insert(0, os.getenv('DB_USER', 'postgres'))
        
        password_frame = ctk.CTkFrame(db_params_frame)
        password_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(password_frame, text="Password:").pack(side="left", padx=10)
        self.password_entry = ctk.CTkEntry(password_frame, placeholder_text="password", show="*")
        self.password_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.password_entry.insert(0, os.getenv('DB_PASSWORD', 'password'))
        
        port_frame = ctk.CTkFrame(db_params_frame)
        port_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(port_frame, text="Port:").pack(side="left", padx=10)
        self.port_entry = ctk.CTkEntry(port_frame, placeholder_text="5432")
        self.port_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.port_entry.insert(0, os.getenv('DB_PORT', '5432'))
        
        db_buttons_frame = ctk.CTkFrame(db_frame)
        db_buttons_frame.pack(fill="x", padx=20, pady=10)
        
        self.connect_db_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="Connect to DB", 
            command=self.connect_database
        )
        self.connect_db_btn.pack(side="left", padx=10)
        
        self.test_db_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="Test Connection", 
            command=self.test_database_connection
        )
        self.test_db_btn.pack(side="left", padx=10)
        
        self.init_db_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="Initialize DB", 
            command=self.initialize_database
        )
        self.init_db_btn.pack(side="left", padx=10)
    
    def create_bot_control_frame(self):
        bot_frame = ctk.CTkFrame(self.root)
        bot_frame.pack(fill="x", padx=20, pady=10)
        
        bot_title = ctk.CTkLabel(bot_frame, text="Bot Control", font=ctk.CTkFont(size=16, weight="bold"))
        bot_title.pack(pady=10)
        
        token_frame = ctk.CTkFrame(bot_frame)
        token_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(token_frame, text="Bot Token:").pack(side="left", padx=10)
        self.token_entry = ctk.CTkEntry(token_frame, placeholder_text="Enter Telegram bot token", show="*")
        self.token_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.token_entry.insert(0, os.getenv('BOT_TOKEN', ''))
        
        bot_buttons_frame = ctk.CTkFrame(bot_frame)
        bot_buttons_frame.pack(fill="x", padx=20, pady=10)
        
        self.start_bot_btn = ctk.CTkButton(
            bot_buttons_frame, 
            text="Start Bot", 
            command=self.start_bot,
            fg_color="green"
        )
        self.start_bot_btn.pack(side="left", padx=10)
        
        self.stop_bot_btn = ctk.CTkButton(
            bot_buttons_frame, 
            text="Stop Bot", 
            command=self.stop_bot,
            fg_color="red",
            state="disabled"
        )
        self.stop_bot_btn.pack(side="left", padx=10)
        
        self.restart_bot_btn = ctk.CTkButton(
            bot_buttons_frame, 
            text="Restart", 
            command=self.restart_bot
        )
        self.restart_bot_btn.pack(side="left", padx=10)
    
    def create_status_frame(self):
        status_frame = ctk.CTkFrame(self.root)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        status_title = ctk.CTkLabel(status_frame, text="System Status", font=ctk.CTkFont(size=16, weight="bold"))
        status_title.pack(pady=10)
        
        db_status_frame = ctk.CTkFrame(status_frame)
        db_status_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(db_status_frame, text="Database:").pack(side="left", padx=10)
        self.db_status_label = ctk.CTkLabel(db_status_frame, text="Not Connected", text_color="red")
        self.db_status_label.pack(side="right", padx=10)
        
        bot_status_frame = ctk.CTkFrame(status_frame)
        bot_status_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(bot_status_frame, text="Telegram Bot:").pack(side="left", padx=10)
        self.bot_status_label = ctk.CTkLabel(bot_status_frame, text="Stopped", text_color="orange")
        self.bot_status_label.pack(side="right", padx=10)
        
        stats_frame = ctk.CTkFrame(status_frame)
        stats_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(stats_frame, text="Words in DB:").pack(side="left", padx=10)
        self.words_count_label = ctk.CTkLabel(stats_frame, text="0")
        self.words_count_label.pack(side="right", padx=10)
    
    def create_log_frame(self):
        log_frame = ctk.CTkFrame(self.root)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_title = ctk.CTkLabel(log_frame, text="Event Log", font=ctk.CTkFont(size=16, weight="bold"))
        log_title.pack(pady=10)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_buttons_frame = ctk.CTkFrame(log_frame)
        log_buttons_frame.pack(fill="x", padx=20, pady=10)
        
        self.clear_log_btn = ctk.CTkButton(
            log_buttons_frame, 
            text="Clear Log", 
            command=self.clear_log
        )
        self.clear_log_btn.pack(side="left", padx=10)
        
        self.save_log_btn = ctk.CTkButton(
            log_buttons_frame, 
            text="Save Log", 
            command=self.save_log
        )
        self.save_log_btn.pack(side="left", padx=10)
    
    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
    
    def check_database_connection(self):
        try:
            self.db = DatabaseManager()
            self.db_status_label.configure(text="Connected", text_color="green")
            self.log_message("Database connection established")
            
            self.update_words_count()
            
        except Exception as e:
            self.db_status_label.configure(text="Connection Error", text_color="red")
            self.log_message(f"Database connection error: {e}")
    
    def connect_database(self):
        try:
            os.environ['DB_HOST'] = self.host_entry.get()
            os.environ['DB_NAME'] = self.db_name_entry.get()
            os.environ['DB_USER'] = self.user_entry.get()
            os.environ['DB_PASSWORD'] = self.password_entry.get()
            os.environ['DB_PORT'] = self.port_entry.get()
            
            if self.db:
                self.db.close()
            
            self.db = DatabaseManager()
            self.db_status_label.configure(text="Connected", text_color="green")
            self.log_message("Database reconnection successful")
            
            self.update_words_count()
            
        except Exception as e:
            self.db_status_label.configure(text="Connection Error", text_color="red")
            self.log_message(f"Database reconnection error: {e}")
    
    def test_database_connection(self):
        try:
            if self.db and self.db.connection:
                cursor = self.db.connection.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                cursor.close()
                
                self.log_message(f"Connection test successful. PostgreSQL version: {version[0]}")
                
                cursor = self.db.connection.cursor()
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in cursor.fetchall()]
                cursor.close()
                
                self.log_message(f"Found tables: {', '.join(tables)}")
                
            else:
                self.log_message("Database not connected")
                
        except Exception as e:
            self.log_message(f"Database test error: {e}")
    
    def initialize_database(self):
        try:
            if self.db:
                self.db.create_tables()
                self.db.initialize_words()
                self.log_message("Database initialized successfully")
                
                self.update_words_count()
            else:
                self.log_message("Database not connected")
                
        except Exception as e:
            self.log_message(f"Database initialization error: {e}")
    
    def update_words_count(self):
        try:
            if self.db and self.db.connection:
                cursor = self.db.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM common_words")
                common_count = cursor.fetchone()[0]
                cursor.close()
                
                self.words_count_label.configure(text=str(common_count))
                
        except Exception as e:
            self.log_message(f"Error updating word count: {e}")
    
    def start_bot(self):
        if self.bot_running:
            self.log_message("Bot is already running")
            return
        
        token = self.token_entry.get().strip()
        if not token:
            self.log_message("Enter bot token")
            return
        
        try:
            os.environ['BOT_TOKEN'] = token
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            bot_path = os.path.join(script_dir, "bot.py")
            
            self.bot_process = subprocess.Popen(
                [sys.executable, bot_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=script_dir
            )
            
            self.bot_running = True
            self.bot_status_label.configure(text="Running", text_color="green")
            self.start_bot_btn.configure(state="disabled")
            self.stop_bot_btn.configure(state="normal")
            
            self.log_message("Telegram bot started")
            
            threading.Thread(target=self.monitor_bot_process, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"Bot start error: {e}")
    
    def stop_bot(self):
        if not self.bot_running:
            return
        
        try:
            if self.bot_process:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
            
            self.bot_running = False
            self.bot_status_label.configure(text="Stopped", text_color="orange")
            self.start_bot_btn.configure(state="normal")
            self.stop_bot_btn.configure(state="disabled")
            
            self.log_message("Telegram bot stopped")
            
        except Exception as e:
            self.log_message(f"Bot stop error: {e}")
    
    def restart_bot(self):
        self.log_message("Restarting bot...")
        self.stop_bot()
        threading.Timer(2.0, self.start_bot).start()
    
    def monitor_bot_process(self):
        try:
            while self.bot_running and self.bot_process:
                if self.bot_process.poll() is not None:
                    self.bot_running = False
                    self.bot_status_label.configure(text="Terminated with Error", text_color="red")
                    self.start_bot_btn.configure(state="normal")
                    self.stop_bot_btn.configure(state="disabled")
                    
                    stdout, stderr = self.bot_process.communicate()
                    if stdout:
                        self.log_message(f"Bot output: {stdout.strip()}")
                    if stderr:
                        self.log_message(f"Bot errors: {stderr.strip()}")
                    
                    self.log_message("Bot process terminated unexpectedly")
                    break
                
                threading.Event().wait(1)
                
        except Exception as e:
            self.log_message(f"Process monitoring error: {e}")
    
    def clear_log(self):
        self.log_text.delete("1.0", "end")
        self.log_message("Log cleared")
    
    def save_log(self):
        try:
            from datetime import datetime
            filename = f"bot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get("1.0", "end"))
            
            self.log_message(f"Log saved to file: {filename}")
            
        except Exception as e:
            self.log_message(f"Log save error: {e}")
    
    def run(self):
        self.log_message("GUI application started")
        self.root.mainloop()
        
        if self.bot_running:
            self.stop_bot()
        
        if self.db:
            self.db.close()

if __name__ == "__main__":
    app = EnglishLearningBotGUI()
    app.run() 
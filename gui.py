"""
EduMentor AI - Graphical User Interface
A simple Tkinter-based GUI for the multi-agent educational system
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def strip_markdown(text):
    """
    Convert markdown to plain text with nice formatting for display.
    Removes markdown syntax while preserving readability.
    """
    if not text:
        return text
    
    # Remove code blocks (```...```)
    text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0).replace('```', '').strip(), text)
    
    # Remove inline code (`...`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Convert headers to plain text with emphasis
    text = re.sub(r'^#{1,6}\s+(.+)$', r'◆ \1', text, flags=re.MULTILINE)
    
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic (*text* or _text_)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\1', text)
    
    # Convert bullet points
    text = re.sub(r'^\s*[-*+]\s+', '  • ', text, flags=re.MULTILINE)
    
    # Convert numbered lists (keep them as is but clean up)
    text = re.sub(r'^\s*(\d+)\.\s+', r'  \1. ', text, flags=re.MULTILINE)
    
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '─' * 40, text, flags=re.MULTILINE)
    
    # Remove links but keep text [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'[Image: \1]', text)
    
    # Remove blockquotes
    text = re.sub(r'^>\s+', '  │ ', text, flags=re.MULTILINE)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from lines but preserve structure
    lines = text.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    text = '\n'.join(cleaned_lines)
    
    return text.strip()


class EduMentorGUI:
    """
    Simple GUI for EduMentor AI using Tkinter
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 EduMentor AI - Your Learning Assistant")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Configure colors
        self.bg_color = "#151554"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.input_bg = "#626485"
        self.button_color = "#89b4fa"
        self.button_fg = "#1e1e2e"
        
        self.root.configure(bg=self.bg_color)
        
        # State variables
        self.orchestrator = None
        self.student_id = None
        self.session_id = None
        self.is_initialized = False
        self.is_processing = False
        self.is_ending_session = False  # Prevent multiple end session calls
        
        # Setup UI
        self._setup_styles()
        self._create_widgets()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        
        # Start initialization in background
        self.root.after(100, self._start_initialization)
    
    def _setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Times new Roman", 16, "bold"), foreground=self.accent_color)
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#a6adc8")
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground=self.input_bg)
        
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header (pack at top)
        self._create_header(main_frame)
        
        # Student ID section (pack at top)
        self._create_student_section(main_frame)
        
        # Status bar (pack at BOTTOM first)
        self._create_status_bar(main_frame)
        
        # Input section (pack at BOTTOM)
        self._create_input_section(main_frame)
        
        # Quick action buttons (pack at BOTTOM)
        self._create_quick_actions(main_frame)
        
        # Chat display (pack LAST with expand - takes remaining space)
        self._create_chat_display(main_frame)
    
    def _create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="🎓 EduMentor AI", 
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle = ttk.Label(
            header_frame,
            text="Your Personal Learning Assistant",
            style="Status.TLabel"
        )
        subtitle.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_student_section(self, parent):
        """Create student ID input section"""
        student_frame = ttk.Frame(parent)
        student_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(student_frame, text="👤 Student ID:").pack(side=tk.LEFT)
        
        self.student_entry = tk.Entry(
            student_frame,
            font=("Segoe UI", 10),
            bg=self.input_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            width=20
        )
        self.student_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.student_entry.insert(0, "")
        
        self.connect_btn = tk.Button(
            student_frame,
            text="Start Session",
            command=self._start_session,
            bg= "#15ee3d",
            fg=self.button_fg,
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.connect_btn.pack(side=tk.LEFT)
        
        # End Session button (initially hidden)
        self.end_session_btn = tk.Button(
            student_frame,
            text="End Session 🛑",
            command=self._end_session,
            bg="#f80f0f",
            fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        # Don't pack yet - will show when session starts
        
        self.session_label = ttk.Label(
            student_frame,
            text="",
            style="Status.TLabel"
        )
        self.session_label.pack(side=tk.LEFT, padx=(15, 0))
    
    def _create_chat_display(self, parent):
        """Create chat display area"""
        chat_frame = ttk.Frame(parent)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat text area
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#181825",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            padx=15,
            pady=15,
            spacing1=2,
            spacing2=2,
            spacing3=5
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for styling
        self.chat_display.tag_configure("user", foreground="#20e90d", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_configure("assistant", foreground="#0f4baa", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_configure("system", foreground="#eba819", font=("Segoe UI", 10, "italic"))
        self.chat_display.tag_configure("error", foreground="#f41e5a")
    
    def _create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        ttk.Label(actions_frame, text="Quick Actions:").pack(side=tk.LEFT, padx=(0, 10))
        
        quick_actions = [
            ("📊 Progress", "Show my learning progress"),
            ("📝 Quiz Me", "Give me a practice quiz"),
            ("💡 Explain", "Explain a concept"),
            ("📚 Help", "What can you help me with?"),
        ]
        
        for text, command in quick_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=lambda cmd=command: self._send_quick_action(cmd),
                bg="#45475a",
                fg=self.fg_color,
                font=("Times New Roman", 9),
                relief=tk.FLAT,
                padx=10,
                pady=3
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def _create_input_section(self, parent):
        """Create input section"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 5))
        
        # Input field
        self.input_field = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg=self.input_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.input_field.bind("<Return>", lambda e: self._send_message())
        
        # Send button
        self.send_btn = tk.Button(
            input_frame,
            text="Send 📤",
            command=self._send_message,
            bg= "#11dce3",
            fg=self.button_fg,
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        self.send_btn.pack(side=tk.RIGHT)
    
    def _create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="⏳ Initializing...",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Exit button
        exit_btn = tk.Button(
            status_frame,
            text="Exit ✕",
            command=self._on_exit,
            bg="#f70449",
            fg="#1e1e2e",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10
        )
        exit_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clear button
        clear_btn = tk.Button(
            status_frame,
            text="Clear Chat",
            command=self._clear_chat,
            bg="#0F0F10",
            fg=self.fg_color,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10
        )
        clear_btn.pack(side=tk.RIGHT)
    
    def _start_initialization(self):
        """Start background initialization"""
        thread = threading.Thread(target=self._initialize_orchestrator, daemon=True)
        thread.start()
    
    def _initialize_orchestrator(self):
        """Initialize the orchestrator in background"""
        try:
            # Check API key
            if not os.getenv('GOOGLE_API_KEY'):
                self._update_status("❌ GOOGLE_API_KEY not found in .env file", error=True)
                self._append_chat(
                    "⚠️ API Key Missing!\n\n"
                    "Please add your GOOGLE_API_KEY to the .env file.\n"
                    "Get your API key from: https://aistudio.google.com/app/apikey",
                    "error"
                )
                return
            
            self._update_status("⏳ Loading AI agents...")
            
            # Import and initialize
            from main import OrchestratorAgent
            self.orchestrator = OrchestratorAgent()
            
            self.is_initialized = True
            self._update_status("✅ Ready - Enter your Student ID and click 'Start Session'")
            self._append_chat(
                "🎓 Welcome to EduMentor AI!\n\n"
                "I'm your personal learning assistant. I can help you with:\n"
                "  Understanding difficult concepts 📚\n"
                "  Homework and problem-solving ✍️\n"
                "  Practice quizzes and exercises 📝\n"
                "  Tracking your learning progress 📊\n\n"
                "Enter your Student ID above and click 'Start Session' to begin!",
                "system"
            )
            
        except Exception as e:
            self._update_status(f"❌ Initialization failed: {str(e)[:50]}", error=True)
            self._append_chat(f"Error initializing: {e}", "error")
    
    def _start_session(self):
        """Start a learning session"""
        if not self.is_initialized:
            messagebox.showwarning("Not Ready", "Please wait for initialization to complete.")
            return
        
        student_id = self.student_entry.get().strip()
        if not student_id:
            messagebox.showwarning("Input Required", "Please enter a Student ID.")
            return
        
        self.student_id = student_id
        self.student_entry.config(state=tk.DISABLED)
        self.connect_btn.config(state=tk.DISABLED, text="Connected")
        
        # Start session in background
        thread = threading.Thread(target=self._async_start_session, daemon=True)
        thread.start()
    
    def _async_start_session(self):
        """Async start session"""
        try:
            self._update_status(f"⏳ Starting session for {self.student_id}...")
            
            # Run async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            greeting = loop.run_until_complete(
                self.orchestrator.start_learning_session(self.student_id)
            )
            loop.close()
            
            self.session_id = self.orchestrator.session_manager.get_current_session(self.student_id)
            
            self._update_status(f"✅ Session active for: {self.student_id}")
            
            # Update UI to show session is active
            def show_session_ui():
                self.session_label.config(text=f"Session: {self.session_id[:8]}...")
                self.connect_btn.pack_forget()
                self.end_session_btn.pack(side=tk.LEFT, padx=(5, 0))
            
            self.root.after(0, show_session_ui)
            
            self._append_chat(f"🎉 Session started for {self.student_id}!\n\nWhat would you like to learn today?", "system")
            
        except Exception as e:
            self._update_status(f"❌ Session error: {str(e)[:50]}", error=True)
            self._append_chat(f"Error starting session: {e}", "error")
    
    def _end_session(self):
        """End the current session and reset UI for new session"""
        # Multiple guards to prevent re-entry
        if not self.session_id or self.is_ending_session:
            return
        
        self.is_ending_session = True  # Lock to prevent re-entry
        
        # Immediately disable the button to prevent multiple clicks
        self.end_session_btn.config(state=tk.DISABLED)
        
        # Prevent multiple calls - immediately clear session_id
        current_session = self.session_id
        current_student = self.student_id
        self.session_id = None
        self.student_id = None
        
        # Get session stats before ending
        duration_min = 0
        message_count = 0
        
        if self.orchestrator:
            try:
                stats = self.orchestrator.session_manager.get_session_stats(current_session)
                if stats:
                    duration_min = stats.get('duration_seconds', 0) / 60
                    message_count = stats.get('message_count', 0)
            except Exception:
                pass
        
        # Build session summary message (use simple characters to avoid regex issues)
        summary = (
            "👋 Thank you for learning with EduMentor AI!\n"
            f"📊 Session ended for: {current_student}\n"
            "🌟 Keep learning and stay curious!\n"
            "\n"
            f"⏱️ Session duration: {duration_min:.5f} minutes\n"
            f"💬 Total interactions: {message_count}"
        )
        
        # Display in chat
        self._append_chat(summary, "system")
        
        # Also print to console
        print("\n" + "─" * 50)
        print("👋 Thank you for learning with EduMentor AI!")
        print(f"📊 Session ended for: {current_student}")
        print("🌟 Keep learning and stay curious!")
        print("─" * 50)
        print(f"\n⏱️  Session duration: {duration_min:.1f} minutes")
        print(f"💬 Total interactions: {message_count}\n")
        
        # Reset UI
        def reset_ui():
            self.student_entry.config(state=tk.NORMAL)
            self.student_entry.delete(0, tk.END)
            self.connect_btn.config(state=tk.NORMAL, text="Start Session")
            self.end_session_btn.pack_forget()
            self.end_session_btn.config(state=tk.NORMAL)  # Re-enable for next session
            self.connect_btn.pack(side=tk.LEFT)
            self.session_label.config(text="")
            self.is_ending_session = False  # Reset flag for next session
        
        self.root.after(0, reset_ui)
        self._update_status("✅ Ready - Enter your Student ID and click 'Start Session'")
    
    def _send_message(self):
        """Send a message"""
        if self.is_processing:
            return
        
        message = self.input_field.get().strip()
        if not message:
            return
        
        if not self.session_id:
            messagebox.showwarning("No Session", "Please start a session first.")
            return
        
        # Clear input
        self.input_field.delete(0, tk.END)
        
        # Display user message
        self._append_chat(f"You: {message}", "user")
        
        # Process in background
        self.is_processing = True
        self._update_status("⏳ Processing...")
        self.send_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=lambda: self._async_process(message), daemon=True)
        thread.start()
    
    def _send_quick_action(self, action):
        """Send a quick action"""
        if not self.session_id:
            messagebox.showwarning("No Session", "Please start a session first.")
            return
        
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, action)
        self._send_message()
    
    def _async_process(self, message):
        """Process message asynchronously"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.orchestrator.route_query(message, self.student_id, self.session_id)
            )
            loop.close()
            
            # Strip markdown formatting for clean display
            clean_response = strip_markdown(response)
            self._append_chat(f"🤖 EduMentor:\n{clean_response}", "assistant")
            self._update_status("✅ Ready")
            
        except Exception as e:
            self._append_chat(f"Error: {e}", "error")
            self._update_status("❌ Error occurred")
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
    
    def _append_chat(self, message, tag=""):
        """Append message to chat display"""
        def update():
            self.chat_display.config(state=tk.NORMAL)
            if self.chat_display.get("1.0", tk.END).strip():
                self.chat_display.insert(tk.END, "\n\n")
            self.chat_display.insert(tk.END, message, tag)
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
        
        self.root.after(0, update)
    
    def _update_status(self, text, error=False):
        """Update status bar"""
        def update():
            self.status_label.config(text=text)
            if error:
                self.status_label.config(foreground="#f38ba8")
            else:
                self.status_label.config(foreground="#a6adc8")
        
        self.root.after(0, update)
    
    def _clear_chat(self):
        """Clear chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _on_exit(self):
        """Handle application exit with cleanup"""
        # Confirm exit if session is active
        if self.session_id:
            confirm = messagebox.askyesno(
                "Exit EduMentor AI",
                "You have an active learning session.\n\n"
                "Your progress has been saved automatically.\n\n"
                "Are you sure you want to exit?"
            )
            if not confirm:
                return
        
        # Show goodbye message
        print("\n" + "─" * 50)
        print("👋 Thank you for learning with EduMentor AI!")
        if self.student_id:
            print(f"📊 Session ended for: {self.student_id}")
        print("🌟 Keep learning and stay curious!")
        print("─" * 50 + "\n")
        
        # End session if active
        if self.session_id and self.orchestrator:
            try:
                # Get session stats
                stats = self.orchestrator.session_manager.get_session_stats(self.session_id)
                if stats:
                    duration_min = stats.get('duration_seconds', 0) / 60
                    print(f"⏱️  Session duration: {duration_min:.1f} minutes")
                    print(f"💬 Total interactions: {stats.get('message_count', 0)}")
            except Exception:
                pass  # Non-critical
        
        # Destroy the window
        self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point for GUI"""
    print("🎓 Starting EduMentor AI GUI...")
    app = EduMentorGUI()
    app.run()


if __name__ == "__main__":
    main()

import tkinter as tk
import string
from tkinter import ttk

class WordProcessorApp:
    def __init__(self, root, inactivity_time=3, warning_time=3, font=("Georgia", 18)):
        self.root = root
        self.root.title("Evil writing app")

        # Parameters
        self.inactivity_time = inactivity_time  # Seconds of inactivity before warning
        self.warning_time = warning_time        # Seconds for warning before deletion
        self.font=font

        # Timer variable
        self.inactivity_timer = None
        self.time_to_delete = False
        self.warning_active = False
        self.targeting_word_count = False

        self.deletion_enabled = False
        self.allow_copy = False

        self.word_count = 0
        self.word_count_target= 0

        self.goal_time=0

        # Create the text widget
        self.text_area = tk.Text(self.root, wrap=tk.WORD, font=self.font)
        # self.text_area.pack(padx=10, pady=10)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)

        self.text_area.config(state="disabled")

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)

        # Create multiple buttons in a row
        self.buttons = [
            tk.Button(self.button_frame, text="1-Min Timer", fg="#420a27", command=lambda: self.start_timer(1)),
            tk.Button(self.button_frame, text="5-Min Timer", fg="#420a27", command=lambda: self.start_timer(5)),
            tk.Button(self.button_frame, text="10-Min Timer", fg="#420a27", command=lambda: self.start_timer(10)),
            tk.Button(self.button_frame, text="Word Count: 50", fg="#05023b", command=lambda: self.start_word_count_goal(50)),
            tk.Button(self.button_frame, text="Word Count: 150", fg="#05023b", command=lambda: self.start_word_count_goal(150)),
            tk.Button(self.button_frame, text="Word Count: 300", fg="#05023b", command=lambda: self.start_word_count_goal(300))

        ]

        # Place buttons in a row using grid
        for i, button in enumerate(self.buttons):
            button.grid(row=0, column=i, padx=5)  # Grid layout

        # Create a label to show warning message
        self.warning_label = tk.Label(self.root, text="", fg="red")
        self.warning_label.pack()

        self.word_count_label = tk.Label(self.root, text="", fg="#919599")
        self.word_count_label.pack()

        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)  # Ensures full width

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Custom.Horizontal.TProgressbar", background="#a889f5")

        # Create the progress bar
        self.progress_bar = ttk.Progressbar(self.progress_frame, style="Custom.Horizontal.TProgressbar", orient="horizontal", mode="determinate") #, style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, expand=True)  # Allows it to resize with the window
        self.progress_bar["maximum"] = 300  # 5-minute max (300 seconds)

        self.root.bind("<Configure>", self.on_resize)

        # Bind the key events to detect user activity
        self.text_area.bind("<KeyPress>", self.on_user_activity)

        self.text_area.bind("<Control-x>", self.disable_copy_cut)
        self.text_area.bind("<Command-x>", self.disable_copy_cut)
        self.text_area.bind("<Control-c>", self.disable_copy_cut)
        self.text_area.bind("<Command-c>", self.disable_copy_cut)

        # Start the inactivity timer
        self.reset_inactivity_timer()

    def on_resize(self, event):
        """Adjusts the progress bar length dynamically."""
        self.progress_bar.config(length=event.width - 20)  # Adjust length dynamically

    def set_progress(self, percentage):
        """Custom method to update the progress bar."""
        if percentage < 0:
            percentage = 0
        if percentage > 1:
            percentage = 1
        self.progress_bar["value"] = int(percentage*300)  
        # self.warning_label.config(text=f"Progress {percentage}") #debugging
        if int(percentage) >= 1:
            self.style.configure("Custom.Horizontal.TProgressbar", background="#3bb322")
            

    def start_word_count_goal(self, wc_goal):
        self.button_frame.pack_forget()
        self.text_area.config(state="normal")
        self.deletion_enabled = True
        self.targeting_word_count = True
        self.word_count_target = wc_goal
        self.reset_inactivity_timer()

    def start_timer(self, num_minutes):
        """Start the 5-minute timer to stop text deletion after expiration."""
        self.button_frame.pack_forget()
        self.goal_time = num_minutes*60
        self.text_area.config(state="normal")
        self.elapsed_time = 0
        self.deletion_enabled = True  # Enable deletion initially
        self.progress_bar_timer()
        # self.warning_label.config(text="5-minute timer started!")
        self.root.after(num_minutes * 60 * 1000, self.disable_deletion)  # Set timer

        # Start tracking inactivity
        self.reset_inactivity_timer()

    def progress_bar_timer(self):
        progress = self.elapsed_time / float(self.goal_time)
        self.set_progress(progress)
        self.elapsed_time += 1
        self.root.after(1000, self.progress_bar_timer)
            

    def disable_deletion(self):
        """Disable text deletion after 5 minutes."""
        self.deletion_enabled = False
        self.allow_copy = True
        self.warning_label.config(text="Done! Text will no longer be deleted.", fg="#3bb322")


    def on_user_activity(self, event=None):
        """Reset the inactivity timer whenever the user types."""

        if event.char and (event.char.isalnum() or event.char in string.punctuation):
            # self.warning_label.config(text=f"{event.char} counts as alnum or punctuation")
            if self.inactivity_timer:
                self.root.after_cancel(self.inactivity_timer)  # Cancel the existing timer
                self.time_to_delete = False
            self.reset_inactivity_timer()
        self.update_word_count()

        if self.targeting_word_count:
            self.check_word_count_target()
    
    def update_word_count(self):
        text_content = self.text_area.get("1.0", tk.END).strip()
        tokens = text_content.split()
        self.word_count = len(tokens)
        self.word_count_label.config(text=f"Word count: {self.word_count}")
    
    def check_word_count_target(self):
        progress_percentage = float(self.word_count) / float(self.word_count_target)
        self.set_progress(progress_percentage)
        if self.word_count >= self.word_count_target:
            self.disable_deletion()
    
    def disable_copy_cut(self, event=None):
        if self.allow_copy:
            pass
        else:
            # pass
            return "break"

    def reset_inactivity_timer(self):
        """Start a new inactivity timer."""
        if self.warning_active:
            self.reset_after_warning()

        if self.deletion_enabled:
            self.inactivity_timer = self.root.after(self.inactivity_time * 1000, self.show_warning)

    def show_warning(self):
        """Show the warning before deletion."""
        if self.deletion_enabled:
            self.time_to_delete = True
            self.warning_active = True
            self.warning_label.config(text=f"Text will be deleted in {self.warning_time} seconds!")
            self.text_area.config(bg="#f1daf7")  # Change background to yellow for warning
            self.warning_timer = self.root.after((self.warning_time-2) * 1000, self.penultimate_second)

    def penultimate_second(self):
        if self.warning_active:
            self.text_area.config(bg="#e6b0f5")
            self.warning_label.config(text=f"Text will be deleted in {2} seconds!")
        self.warning_timer = self.root.after(1 * 1000, self.last_second)
    
    def last_second(self):
        if self.warning_active:
            self.text_area.config(bg="#e894ff")
            self.warning_label.config(text=f"Text will be deleted in {1} seconds!")
        self.warning_timer = self.root.after(1 * 1000, self.decide_delete)
    
    def decide_delete(self):
        if self.time_to_delete and self.deletion_enabled:
            self.delete_text()
        elif self.warning_active:
            self.reset_after_warning()
    
    def reset_after_warning(self):
        self.warning_label.config(text="")  # Clear the warning message
        self.text_area.config(bg="white")
        self.warning_active = False

    def delete_text(self):
        """Delete the text after the warning time."""
        self.text_area.delete(1.0, tk.END)
        # self.text_area.insert("end-1c", "\n\n\nWhoops...")
        self.warning_label.config(text="")  # Clear the warning message
        self.text_area.config(bg="white")  # Reset background to white
        self.warning_active = False
        self.update_word_count()

if __name__ == "__main__":
    root = tk.Tk()
    app = WordProcessorApp(root)
    root.mainloop()

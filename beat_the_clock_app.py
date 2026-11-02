"""
BEAT THE CLOCK - Smart Study Planner  (DAA mini project)

Problem : I have a few free hours this week and several subjects to study.
          Each subject needs some hours and has an importance score.
          Which subjects should I study to earn the most marks?
Method  : 0/1 Knapsack solved with Dynamic Programming,
          compared against a Greedy "best value per hour" shortcut.

Run     : python beat_the_clock.py      (Python 3 only, tkinter is built in)

The file has 3 parts:
    PART 1  the algorithms (the DAA part)
    PART 2  colours and small helpers
    PART 3  the window (everything the user sees)
"""
import tkinter as tk
from tkinter import font as tkfont, messagebox


# =====================================================================
# PART 1 - THE ALGORITHMS
# A subject is a tuple: (name, hours_needed, importance)
# =====================================================================
def dp_plan(subjects, budget):
    """0/1 Knapsack using Dynamic Programming (bottom-up table).

    table[i][w] = best importance we can get using only the first i subjects
                  when we have w hours.
    Returns: (best_value, chosen_subject_numbers, last_row_of_table)
    The last row tells us the best value for EVERY number of hours 0..budget,
    which we use for the "what if I had more or fewer hours?" chart.
    """
    n = len(subjects)
    table = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        hours = subjects[i - 1][1]
        value = subjects[i - 1][2]
        for w in range(budget + 1):
            table[i][w] = table[i - 1][w]                       # option 1: skip subject i
            if hours <= w:                                      # option 2: take subject i
                take = table[i - 1][w - hours] + value
                table[i][w] = max(table[i][w], take)            # keep the better option

    # Backtrack: walk up the table to find WHICH subjects were chosen.
    chosen = []
    w = budget
    for i in range(n, 0, -1):
        if table[i][w] != table[i - 1][w]:                      # value changed, so subject i was taken
            chosen.append(i - 1)
            w -= subjects[i - 1][1]
    chosen.sort()
    return table[n][budget], chosen, table[n]


def greedy_plan(subjects, budget):
    """Greedy shortcut: keep taking the subject with the best importance-per-hour
    until the hours run out. Fast, but not always the best answer."""
    order = sorted(range(len(subjects)),
                   key=lambda k: subjects[k][2] / subjects[k][1], reverse=True)
    hours_used = 0
    total_value = 0
    for k in order:
        if hours_used + subjects[k][1] <= budget:
            hours_used += subjects[k][1]
            total_value += subjects[k][2]
    return total_value


# =====================================================================
# PART 2 - COLOURS AND SMALL HELPERS
# =====================================================================
BG = "#f5f2ec"        # page background
CARD = "#ffffff"      # white cards
INK = "#14213d"       # main text
MUTED = "#667085"     # grey text
LINE = "#e9e4d9"      # thin borders
SOFT = "#f3efe6"      # light fills
TEAL = "#0f766e"
CORAL = "#ff6b4a"
SUN = "#ffb703"
NAVY = "#14213d"      # dark result panel
NAVY_LIGHT = "#223a6b"
NAVY_ROW = "#2a4478"
NAVY_TEXT = "#aebbd9"
SUBJECT_COLOURS = ["#0f766e", "#ff6b4a", "#3b5bdb", "#d6336c", "#d99100", "#7048e8"]

SAMPLE_SUBJECTS = [("DAA", 7, 9), ("DBMS", 6, 8), ("AIP", 5, 6), ("Data Science", 4, 5)]


def mix(colour1, colour2, amount):
    """Blend two '#rrggbb' colours. amount=0 gives colour1, amount=1 gives colour2."""
    a = [int(colour1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(colour2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[j] + (b[j] - a[j]) * amount) for j in range(3))


def make_button(parent, text, command, bg, fg, font, padx=14, pady=7):
    """A flat coloured button. (Label is used because it looks the same on Windows/Mac/Linux.)"""
    button = tk.Label(parent, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady, cursor="hand2")
    darker = mix(bg, "#000000", 0.12)
    button.bind("<Button-1>", lambda event: command())
    button.bind("<Enter>", lambda event: button.config(bg=darker))
    button.bind("<Leave>", lambda event: button.config(bg=bg))
    return button


class Slider(tk.Canvas):
    """A simple slider drawn by hand: click or drag to pick a whole number."""

    def __init__(self, parent, low, high, value, colour, on_change, width=240, bg=CARD):
        tk.Canvas.__init__(self, parent, width=width, height=28, bg=bg, highlightthickness=0, cursor="hand2")
        self.low, self.high, self.value = low, high, value
        self.colour, self.on_change, self.box_width = colour, on_change, width
        self.bind("<Button-1>", self.move)
        self.bind("<B1-Motion>", self.move)
        self.draw()

    def set(self, value):
        """Change the value from code (does not call on_change)."""
        self.value = max(self.low, min(self.high, value))
        self.draw()

    def move(self, event):
        edge = 12
        fraction = (event.x - edge) / (self.box_width - 2 * edge)
        fraction = max(0, min(1, fraction))
        self.value = round(self.low + fraction * (self.high - self.low))
        self.draw()
        self.on_change(self.value)

    def draw(self):
        self.delete("all")
        edge = 12
        fraction = (self.value - self.low) / (self.high - self.low)
        thumb_x = edge + fraction * (self.box_width - 2 * edge)
        self.create_line(edge, 14, self.box_width - edge, 14, fill=SOFT, width=8, capstyle="round")
        self.create_line(edge, 14, thumb_x, 14, fill=self.colour, width=8, capstyle="round")
        self.create_oval(thumb_x - 10, 4, thumb_x + 10, 24, fill=self.colour, outline="white", width=3)


# =====================================================================
# PART 3 - THE WINDOW
# =====================================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("Beat the Clock - Smart Study Planner")
        root.configure(bg=BG)
        root.geometry("1160x740")
        root.minsize(1040, 700)

        # pick a nice font that exists on this computer
        installed = set(tkfont.families())
        names = ("Segoe UI", "Helvetica Neue", "Calibri", "Arial", "DejaVu Sans")
        self.face = next((n for n in names if n in installed), "Helvetica")

        # ---- the data the user controls ----
        self.hours = 11          # free hours this week
        self.subjects = []       # list of dicts: {"name": StringVar, "hours": int, "importance": int}
        self.result = None       # latest answer, used by the drawing functions

        # ---- gauge animation ----
        self.shown_percent = 0.0
        self.target_percent = 0.0
        self.animation_id = None

        self.build_header()
        body = tk.Frame(root, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=(4, 12))
        body.columnconfigure(0, weight=5, uniform="col")
        body.columnconfigure(1, weight=6, uniform="col")
        body.rowconfigure(0, weight=1)
        self.build_inputs(body)
        self.build_results(body)
        self.load_sample()

        root.update_idletasks()
        height = max(680, min(root.winfo_reqheight(), root.winfo_screenheight() - 70))
        root.geometry("1160x%d" % height)

    def font(self, size=10, bold=False):
        return (self.face, size, "bold" if bold else "normal")

    def card(self, parent, bg=CARD, border=LINE):
        return tk.Frame(parent, bg=bg, highlightbackground=border, highlightthickness=1)

    def section_title(self, parent, number, text, bg=CARD, fg=INK):
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", padx=18, pady=(14, 8))
        if number:
            tk.Label(row, text=number, font=self.font(10, True), bg=INK, fg="white", width=2).pack(side="left", padx=(0, 10))
        tk.Label(row, text=text, font=self.font(12, True), bg=bg, fg=fg).pack(side="left")

    # ------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------
    def build_header(self):
        self.header = tk.Canvas(self.root, height=84, highlightthickness=0, bd=0)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", self.draw_header)

    def draw_header(self, event=None):
        c = self.header
        c.delete("all")
        width = max(c.winfo_width(), 900)
        for x in range(0, width, 3):                                   # colour gradient, left to right
            c.create_line(x, 0, x, 84, fill=mix(NAVY, TEAL, x / width), width=3)
        c.create_text(28, 30, text="Beat the Clock", anchor="w", font=self.font(22, True), fill="white")
        c.create_text(30, 61, anchor="w", font=self.font(10), fill="#cfe3f0",
                      text="Tell us your free hours. We pick the subjects that earn you the most marks.")
        c.create_text(width - 26, 42, anchor="e", font=self.font(9, True), fill="#cfe3f0",
                      text="0/1 Knapsack  |  Dynamic Programming")

    # ------------------------------------------------------------------
    # LEFT SIDE - INPUTS
    # ------------------------------------------------------------------
    def build_inputs(self, body):
        left = self.card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # --- step 1: weekly hours ---
        self.section_title(left, "1", "How many hours do you have this week?")
        row = tk.Frame(left, bg=CARD)
        row.pack(fill="x", padx=18)
        make_button(row, "\u2212", lambda: self.set_hours(self.hours - 1), SOFT, INK, self.font(16, True), 14, 4).pack(side="left")
        self.hours_label = tk.Label(row, text="11", font=self.font(40, True), bg=CARD, fg=TEAL, width=3)
        self.hours_label.pack(side="left", padx=4)
        make_button(row, "+", lambda: self.set_hours(self.hours + 1), SOFT, INK, self.font(16, True), 14, 4).pack(side="left")
        tk.Label(row, text="hours free\nthis week", font=self.font(10), bg=CARD, fg=MUTED, justify="left").pack(side="left", padx=14)

        self.hours_slider = Slider(left, 1, 40, self.hours, TEAL, self.set_hours, width=380)
        self.hours_slider.pack(padx=18, pady=(8, 4), anchor="w")
        quick = tk.Frame(left, bg=CARD)
        quick.pack(fill="x", padx=18)
        for h in (8, 12, 20, 30):
            make_button(quick, "%d h" % h, lambda h=h: self.set_hours(h), SOFT, MUTED, self.font(9, True), 10, 3).pack(side="left", padx=(0, 6))

        # --- step 2: subjects ---
        self.section_title(left, "2", "What do you need to study?")
        tk.Label(left, text="Importance: 1 = can wait, 10 = must do (exam weightage, deadline, difficulty).",
                 font=self.font(9), bg=CARD, fg=MUTED, anchor="w", justify="left", wraplength=400).pack(fill="x", padx=18, pady=(0, 4))
        area = tk.Frame(left, bg=CARD)
        area.pack(fill="both", expand=True, padx=(18, 8))
        self.scroll_canvas = tk.Canvas(area, width=10, bg=CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(area, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.rows_frame = tk.Frame(self.scroll_canvas, bg=CARD)
        window = self.scroll_canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.rows_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        self.scroll_canvas.bind("<Configure>", lambda e: self.scroll_canvas.itemconfigure(window, width=e.width))
        self.scroll_canvas.bind("<Enter>", lambda e: self.mouse_wheel(True))
        self.scroll_canvas.bind("<Leave>", lambda e: self.mouse_wheel(False))

        buttons = tk.Frame(left, bg=CARD)
        buttons.pack(fill="x", padx=18, pady=(8, 16))
        make_button(buttons, "+  Add subject", self.add_subject, INK, "white", self.font(10, True), 16, 8).pack(side="left")
        make_button(buttons, "Sample", self.load_sample, SOFT, INK, self.font(10, True)).pack(side="left", padx=6)
        make_button(buttons, "Clear", self.clear_subjects, SOFT, INK, self.font(10, True)).pack(side="left")
        make_button(buttons, "Save plan", self.save_plan, SOFT, TEAL, self.font(10, True)).pack(side="right")

    def mouse_wheel(self, on):
        """Let the mouse wheel scroll the subject list while the pointer is over it."""
        canvas = self.scroll_canvas
        if on:
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
            canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        else:
            for event_name in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                canvas.unbind_all(event_name)

    # ---- working with the list of subjects ----
    def new_subject(self, name, hours, importance):
        name_var = tk.StringVar(value=name)
        name_var.trace_add("write", lambda *args: self.update())      # re-calculate when the name changes
        return {"name": name_var, "hours": hours, "importance": importance}

    def add_subject(self):
        self.subjects.append(self.new_subject("Subject %d" % (len(self.subjects) + 1), 4, 5))
        self.draw_subject_rows()
        self.scroll_canvas.update_idletasks()
        self.scroll_canvas.yview_moveto(1.0)

    def remove_subject(self, number):
        del self.subjects[number]
        self.draw_subject_rows()

    def clear_subjects(self):
        self.subjects = []
        self.draw_subject_rows()

    def load_sample(self):
        self.subjects = [self.new_subject(*s) for s in SAMPLE_SUBJECTS]
        self.set_hours(11)
        self.draw_subject_rows()

    def draw_subject_rows(self):
        """Build one card per subject in the left panel."""
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        if not self.subjects:
            tk.Label(self.rows_frame, text="No subjects yet.\nPress  + Add subject  to begin.",
                     font=self.font(10), bg=CARD, fg=MUTED, pady=26).pack()

        for number, subject in enumerate(self.subjects):
            colour = SUBJECT_COLOURS[number % len(SUBJECT_COLOURS)]
            card = self.card(self.rows_frame)
            card.pack(fill="x", pady=6, padx=(0, 6))
            tk.Frame(card, bg=colour, width=6).pack(side="left", fill="y")      # coloured stripe
            inner = tk.Frame(card, bg=CARD)
            inner.pack(side="left", fill="x", expand=True, padx=12, pady=10)

            # line 1: name box and delete button
            line1 = tk.Frame(inner, bg=CARD)
            line1.pack(fill="x")
            tk.Entry(line1, textvariable=subject["name"], font=self.font(12, True), bd=0, bg=SOFT, fg=INK,
                     insertbackground=INK, highlightthickness=0).pack(side="left", fill="x", expand=True, ipady=5, ipadx=6)
            delete = tk.Label(line1, text="\u2715", font=self.font(11), bg=CARD, fg=MUTED, cursor="hand2", padx=8)
            delete.pack(side="right")
            delete.bind("<Button-1>", lambda e, n=number: self.remove_subject(n))

            # line 2: hours needed  (- 7 h +)
            line2 = tk.Frame(inner, bg=CARD)
            line2.pack(fill="x", pady=(8, 0))
            tk.Label(line2, text="Time needed", font=self.font(9), bg=CARD, fg=MUTED, width=11, anchor="w").pack(side="left")
            hours_text = tk.Label(line2, text="%d h" % subject["hours"], font=self.font(11, True), bg=CARD, fg=INK, width=4)
            make_button(line2, "\u2212", lambda n=number, t=hours_text: self.change_subject_hours(n, -1, t),
                        SOFT, INK, self.font(11, True), 8, 1).pack(side="left")
            hours_text.pack(side="left")
            make_button(line2, "+", lambda n=number, t=hours_text: self.change_subject_hours(n, 1, t),
                        SOFT, INK, self.font(11, True), 8, 1).pack(side="left")

            # line 3: importance slider  (1 to 10)
            line3 = tk.Frame(inner, bg=CARD)
            line3.pack(fill="x", pady=(8, 0))
            tk.Label(line3, text="Importance", font=self.font(9), bg=CARD, fg=MUTED, width=11, anchor="w").pack(side="left")
            value_text = tk.Label(line3, text="%d/10" % subject["importance"], font=self.font(10, True), bg=CARD, fg=INK, width=5)

            def importance_changed(value, subject=subject, label=value_text):
                subject["importance"] = value
                label.config(text="%d/10" % value)
                self.update()

            Slider(line3, 1, 10, subject["importance"], colour, importance_changed, width=190).pack(side="left")
            value_text.pack(side="left")
        self.update()

    def change_subject_hours(self, number, change, label):
        hours = max(1, min(30, self.subjects[number]["hours"] + change))
        self.subjects[number]["hours"] = hours
        label.config(text="%d h" % hours)
        self.update()

    def set_hours(self, value):
        self.hours = max(1, min(40, int(value)))
        self.hours_label.config(text=str(self.hours))
        self.hours_slider.set(self.hours)
        self.update()

    # ------------------------------------------------------------------
    # RIGHT SIDE - RESULTS
    # ------------------------------------------------------------------
    def build_results(self, body):
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.columnconfigure(0, weight=1)
        right.columnconfigure(1, weight=1)

        # ---- dark "best plan" panel ----
        panel = tk.Frame(right, bg=NAVY)
        panel.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(panel, text="YOUR BEST PLAN", font=self.font(9, True), bg=NAVY, fg=NAVY_TEXT).pack(anchor="w", padx=20, pady=(12, 0))

        top = tk.Frame(panel, bg=NAVY)
        top.pack(fill="x", padx=14, pady=(4, 0))
        self.gauge = tk.Canvas(top, width=140, height=140, bg=NAVY, highlightthickness=0)
        self.gauge.pack(side="left")
        words = tk.Frame(top, bg=NAVY)
        words.pack(side="left", fill="x", expand=True, padx=(8, 12))
        self.headline = tk.Label(words, font=self.font(18, True), bg=NAVY, fg="white", justify="left", anchor="w", wraplength=300)
        self.headline.pack(fill="x")
        self.subline = tk.Label(words, font=self.font(10), bg=NAVY, fg=NAVY_TEXT, justify="left", anchor="w", wraplength=300)
        self.subline.pack(fill="x", pady=(6, 0))

        self.week_bar = tk.Canvas(panel, width=10, height=58, bg=NAVY, highlightthickness=0)
        self.week_bar.pack(fill="x", padx=20, pady=(2, 2))
        self.week_bar.bind("<Configure>", lambda e: self.draw_week_bar())
        self.plan_list = tk.Frame(panel, bg=NAVY)
        self.plan_list.pack(fill="x", padx=20, pady=(0, 14))

        # ---- compare card ----
        compare = self.card(right)
        compare.grid(row=1, column=0, sticky="nsew", pady=(14, 0), padx=(0, 7))
        self.section_title(compare, None, "Smart method vs quick guess")
        self.compare_canvas = tk.Canvas(compare, width=10, height=84, bg=CARD, highlightthickness=0)
        self.compare_canvas.pack(fill="x", padx=18)
        self.compare_canvas.bind("<Configure>", lambda e: self.draw_compare())
        self.compare_text = tk.Label(compare, font=self.font(9), bg=CARD, fg=MUTED, justify="left", anchor="nw", wraplength=250)
        self.compare_text.pack(fill="x", padx=18, pady=(2, 14))

        # ---- what-if chart card ----
        chart = self.card(right)
        chart.grid(row=1, column=1, sticky="nsew", pady=(14, 0), padx=(7, 0))
        self.section_title(chart, None, "More or fewer hours?")
        self.chart_canvas = tk.Canvas(chart, width=10, height=150, bg=CARD, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.chart_canvas.bind("<Configure>", lambda e: self.draw_chart())
        right.rowconfigure(1, weight=1)

    # ------------------------------------------------------------------
    # THE MAIN STEP: run both algorithms, then refresh everything
    # ------------------------------------------------------------------
    def update(self):
        subjects = []
        for number, s in enumerate(self.subjects):
            name = s["name"].get().strip() or "Subject %d" % (number + 1)
            subjects.append((name, s["hours"], s["importance"]))

        total_importance = sum(s[2] for s in subjects)
        total_hours_needed = sum(s[1] for s in subjects)

        if subjects:
            best, chosen, _ = dp_plan(subjects, self.hours)           # smart method
            greedy_best = greedy_plan(subjects, self.hours)           # quick guess
        else:
            best, chosen, greedy_best = 0, [], 0

        if total_importance:
            dp_percent = round(100 * best / total_importance)
            greedy_percent = round(100 * greedy_best / total_importance)
        else:
            dp_percent = greedy_percent = 0
        hours_used = sum(subjects[k][1] for k in chosen)

        self.result = {"subjects": subjects, "chosen": chosen, "dp_percent": dp_percent,
                       "greedy_percent": greedy_percent, "hours_used": hours_used,
                       "total_importance": total_importance}

        # headline text
        if not subjects:
            self.headline.config(text="Add your subjects")
            self.subline.config(text="Then set the time each one needs and how important it is.")
        elif not chosen:
            self.headline.config(text="Nothing fits in %d hour%s" % (self.hours, "" if self.hours == 1 else "s"))
            self.subline.config(text="Add more hours or shorten what a subject needs.")
        else:
            names = [subjects[k][0] for k in chosen]
            if len(names) > 1:
                self.headline.config(text="Study " + ", ".join(names[:-1]) + " and " + names[-1])
            else:
                self.headline.config(text="Study " + names[0])
            if total_hours_needed > self.hours:
                self.subline.config(text="Your subjects need %d hours but you have %d. This mix earns the most marks in %d hours."
                                    % (total_hours_needed, self.hours, hours_used))
            else:
                self.subline.config(text="Great news: everything fits in your %d hours." % self.hours)

        self.start_gauge_animation(dp_percent)
        self.draw_week_bar()
        self.draw_plan_list()
        self.draw_compare()
        self.draw_chart()

    # ------------------------------------------------------------------
    # DRAWING FUNCTIONS
    # ------------------------------------------------------------------
    def start_gauge_animation(self, target):
        self.target_percent = target
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
        self.animate_gauge()

    def animate_gauge(self):
        difference = self.target_percent - self.shown_percent
        if abs(difference) < 0.6:
            self.shown_percent = self.target_percent
            self.animation_id = None
        else:
            self.shown_percent += difference * 0.25                    # move a quarter of the way each step
            self.animation_id = self.root.after(18, self.animate_gauge)
        self.draw_gauge()

    def draw_gauge(self):
        c = self.gauge
        c.delete("all")
        c.create_arc(14, 14, 126, 126, start=0, extent=359.9, style="arc", outline=NAVY_ROW, width=14)
        if self.shown_percent > 0.5:
            c.create_arc(14, 14, 126, 126, start=90, extent=-3.599 * self.shown_percent,
                         style="arc", outline="#ff8a3d", width=14)
        c.create_text(70, 62, text="%d%%" % round(self.shown_percent), font=self.font(26, True), fill="white")
        c.create_text(70, 92, text="of what matters\ncovered", font=self.font(8), fill=NAVY_TEXT, justify="center")

    def draw_week_bar(self):
        """One bar for the whole week, split between the chosen subjects."""
        c = self.week_bar
        c.delete("all")
        if not self.result:
            return
        r = self.result
        width = max(c.winfo_width(), 300) - 4
        per_hour = width / self.hours
        x = 2
        for k in r["chosen"]:
            name, hours, _ = r["subjects"][k]
            box_width = hours * per_hour
            c.create_rectangle(x, 4, x + box_width, 38, fill=SUBJECT_COLOURS[k % len(SUBJECT_COLOURS)], outline=NAVY, width=2)
            label = "%s  %dh" % (name, hours) if box_width > 100 else "%dh" % hours
            c.create_text(x + box_width / 2, 21, text=label, fill="white", font=self.font(9, True))
            x += box_width
        free = self.hours - r["hours_used"]
        if free > 0:
            c.create_rectangle(x, 4, 2 + width, 38, fill=NAVY_ROW, outline=NAVY, width=2)
            if free >= 2:
                c.create_text((x + 2 + width) / 2, 21, text="free", fill=NAVY_TEXT, font=self.font(9))
        c.create_text(2, 50, anchor="w", text="0 h", fill=NAVY_TEXT, font=self.font(9))
        c.create_text(2 + width, 50, anchor="e", fill=NAVY_TEXT, font=self.font(9),
                      text="%d of %d hours used" % (r["hours_used"], self.hours))

    def draw_plan_list(self):
        """One row per subject: STUDY (green) or LATER (grey)."""
        for widget in self.plan_list.winfo_children():
            widget.destroy()
        if not self.result:
            return
        r = self.result
        for k, (name, hours, importance) in enumerate(r["subjects"]):
            studying = k in r["chosen"]
            row = tk.Frame(self.plan_list, bg=NAVY_LIGHT)
            row.pack(fill="x", pady=2)
            tk.Frame(row, bg=SUBJECT_COLOURS[k % len(SUBJECT_COLOURS)], width=6).pack(side="left", fill="y")
            tk.Label(row, text=name, font=self.font(11, True), bg=NAVY_LIGHT, fg="white" if studying else "#7f8fb3",
                     anchor="w").pack(side="left", padx=(10, 8), pady=4)
            tk.Label(row, text="%d hours  \u2022  importance %d" % (hours, importance), font=self.font(9),
                     bg=NAVY_LIGHT, fg=NAVY_TEXT if studying else "#7f8fb3").pack(side="left")
            tag = tk.Label(row, text="STUDY" if studying else "LATER", font=self.font(8, True),
                           bg="#1f9d6b" if studying else "#4a5d8a", fg="white", padx=9, pady=2)
            tag.pack(side="right", padx=10)

    def draw_compare(self):
        """Two bars: smart method (DP) against quick guess (Greedy)."""
        c = self.compare_canvas
        c.delete("all")
        if not self.result:
            return
        r = self.result
        bar_width = max(c.winfo_width(), 240) - 56
        bars = (("Smart method (DP)", r["dp_percent"], TEAL), ("Quick guess (Greedy)", r["greedy_percent"], SUN))
        for row, (label, percent, colour) in enumerate(bars):
            y = row * 42
            c.create_text(0, y + 2, text=label, anchor="nw", font=self.font(9), fill=MUTED)
            c.create_rectangle(0, y + 20, bar_width, y + 34, fill=SOFT, outline=SOFT)
            if percent > 0:
                c.create_rectangle(0, y + 20, bar_width * percent / 100, y + 34, fill=colour, outline=colour)
            c.create_text(bar_width + 8, y + 27, text="%d%%" % percent, anchor="w", font=self.font(11, True), fill=INK)
        gap = r["dp_percent"] - r["greedy_percent"]
        if not r["subjects"]:
            self.compare_text.config(text="")
        elif gap > 0:
            self.compare_text.config(text="The smart method finds %d more points. The quick guess takes the best value-per-hour first "
                                          "and can waste hours." % gap)
        else:
            self.compare_text.config(text="Both methods agree here. Change the hours to see where the quick guess slips.")

    def draw_chart(self):
        """Line chart: how much of the importance you cover at every number of weekly hours."""
        c = self.chart_canvas
        c.delete("all")
        if not self.result or not self.result["subjects"] or not self.result["total_importance"]:
            return
        r = self.result
        subjects = r["subjects"]
        max_hours = max(sum(s[1] for s in subjects), self.hours)
        last_row = dp_plan(subjects, max_hours)[2]                       # best value for hours 0..max_hours
        total = r["total_importance"]

        width, height = max(c.winfo_width(), 320), max(c.winfo_height(), 140)
        left, right, top, bottom = 38, 12, 28, 26

        def x_of(hours):
            return left + (width - left - right) * hours / max_hours

        def y_of(percent):
            return top + (height - top - bottom) * (1 - percent / 100)

        for percent in (0, 50, 100):                                     # grid lines
            c.create_line(left, y_of(percent), width - right, y_of(percent), fill=SOFT)
            c.create_text(left - 6, y_of(percent), text="%d%%" % percent, anchor="e", font=self.font(8), fill=MUTED)

        dp_points, greedy_points = [], []
        for h in range(max_hours + 1):
            dp_points += [x_of(h), y_of(100 * last_row[h] / total)]
            greedy_points += [x_of(h), y_of(100 * greedy_plan(subjects, h) / total)]
        c.create_polygon([x_of(0), y_of(0)] + dp_points + [x_of(max_hours), y_of(0)],
                         fill=mix(TEAL, "#ffffff", 0.85), outline="")
        c.create_line(*greedy_points, fill=SUN, width=2, dash=(5, 3))
        c.create_line(*dp_points, fill=TEAL, width=3)

        you_x, you_y = x_of(self.hours), y_of(100 * last_row[self.hours] / total)   # "you are here" marker
        c.create_line(you_x, top, you_x, y_of(0), fill=CORAL, dash=(3, 4))
        c.create_oval(you_x - 6, you_y - 6, you_x + 6, you_y + 6, fill=CORAL, outline="white", width=2)
        c.create_text(left, height - 6, text="0 h", anchor="sw", font=self.font(8), fill=MUTED)
        c.create_text(width - right, height - 6, text="%d h per week" % max_hours, anchor="se", font=self.font(8), fill=MUTED)
        c.create_text(width - right, 2, anchor="ne", font=self.font(8), fill=MUTED,
                      text="green: smart   yellow: quick guess")

    # ------------------------------------------------------------------
    # SAVE
    # ------------------------------------------------------------------
    def save_plan(self):
        if not self.result or not self.result["chosen"]:
            messagebox.showinfo("Nothing to save", "Add subjects first.")
            return
        r = self.result
        lines = ["BEAT THE CLOCK - STUDY PLAN", "Hours available: %d" % self.hours, ""]
        for k, (name, hours, importance) in enumerate(r["subjects"]):
            status = "STUDY" if k in r["chosen"] else "LATER"
            lines.append("%-6s %-20s %2d hours   importance %d" % (status, name, hours, importance))
        lines += ["", "Hours used: %d of %d" % (r["hours_used"], self.hours),
                  "Smart method (DP) covers %d%%" % r["dp_percent"],
                  "Quick guess (Greedy) covers %d%%" % r["greedy_percent"]]
        with open("study_plan.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Saved", "Your plan was saved as study_plan.txt in this folder.")


if __name__ == "__main__":
    window = tk.Tk()
    App(window)
    window.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
from datetime import datetime
import json
from user_manager import UserManager
from key_manager import KeyManager
from crypto_manager import CryptoManager
from diary_storage import DiaryStorage


# ─── Colour Palette ───────────────────────────────────────────────────────────
BG_ROOT      = '#070B12'
BG_CARD      = '#0C1220'
BG_ELEVATED  = '#111927'
BG_INPUT     = '#0A1019'
BG_HOVER     = '#162035'
BG_SEL       = '#0F2A45'

ACCENT       = '#00C8FF'
ACCENT_DIM   = '#007EB4'
ACCENT_GLOW  = '#40DAFF'
ACCENT_MUTED = '#1A4A66'

GREEN        = '#00E87A'
GREEN_DIM    = '#00703A'
RED          = '#FF4455'
RED_DIM      = '#7A1520'
ORANGE       = '#FFB340'

TEXT_PRI     = '#DDE8F5'
TEXT_SEC     = '#6A8BA8'
TEXT_MUTED   = '#2E4560'   

BORDER       = '#162030'   
BORDER_ACC   = '#1E3550'   
BORDER_HI    = '#00C8FF'   

FONT_UI      = ('Segoe UI', 10)
FONT_TITLE   = ('Segoe UI', 16, 'bold')
FONT_SUB     = ('Segoe UI', 12, 'bold')
FONT_SMALL   = ('Segoe UI', 9)
FONT_MONO    = ('Consolas', 9)
FONT_ENTRY   = ('Segoe UI', 11)
FONT_ICON    = ('Segoe UI', 20)
# ──────────────────────────────────────────────────────────────────────────────


def apply_dark_theme(style: ttk.Style):
    """Configure ttk styles for the dark cyber theme."""
    style.theme_use('clam')

    # ── Base frames & labels
    style.configure('TFrame',        background=BG_ROOT)
    style.configure('TLabel',        background=BG_ROOT, foreground=TEXT_PRI,  font=FONT_UI)
    style.configure('Title.TLabel',  background=BG_ROOT, foreground=ACCENT,    font=FONT_TITLE)
    style.configure('Sub.TLabel',    background=BG_ROOT, foreground=ACCENT,    font=FONT_SUB)
    style.configure('Muted.TLabel',  background=BG_ROOT, foreground=TEXT_SEC,  font=FONT_SMALL)
    style.configure('Card.TLabel',   background=BG_CARD, foreground=TEXT_PRI,  font=FONT_UI)
    style.configure('Mono.TLabel',   background=BG_CARD, foreground=ACCENT,    font=FONT_MONO)

    # ── Card frame
    style.configure('Card.TFrame',   background=BG_CARD)
    style.configure('Elevated.TFrame', background=BG_ELEVATED)
    style.configure('Input.TFrame',  background=BG_INPUT)

    # ── Separator
    style.configure('TSeparator', background=BORDER_ACC)

    # ── LabelFrame
    style.configure('TLabelframe',
                    background=BG_CARD,
                    foreground=ACCENT,
                    font=('Segoe UI', 9, 'bold'),
                    bordercolor=BORDER_ACC,
                    relief='solid',
                    borderwidth=1)
    style.configure('TLabelframe.Label',
                    background=BG_CARD,
                    foreground=ACCENT,
                    font=('Segoe UI', 9, 'bold'))

    # ── Entry
    style.configure('TEntry',
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRI,
                    insertcolor=ACCENT,
                    bordercolor=BORDER_ACC,
                    lightcolor=BORDER_ACC,
                    darkcolor=BORDER_ACC,
                    relief='flat',
                    padding=6)
    style.map('TEntry',
              bordercolor=[('focus', BORDER_HI), ('!focus', BORDER_ACC)],
              lightcolor=[('focus', BORDER_HI), ('!focus', BORDER_ACC)],
              darkcolor=[('focus', BORDER_HI),  ('!focus', BORDER_ACC)])

    # ── Button base
    style.configure('TButton',
                    background=BG_ELEVATED,
                    foreground=TEXT_SEC,
                    font=FONT_UI,
                    bordercolor=BORDER_ACC,
                    lightcolor=BORDER_ACC,
                    darkcolor=BORDER_ACC,
                    relief='flat',
                    padding=(10, 6))
    style.map('TButton',
              background=[('active', BG_HOVER), ('pressed', BG_SEL)],
              foreground=[('active', TEXT_PRI), ('pressed', TEXT_PRI)],
              bordercolor=[('active', ACCENT_DIM)])

    # ── Action / Primary button
    style.configure('Action.TButton',
                    background=ACCENT_MUTED,
                    foreground=ACCENT,
                    font=('Segoe UI', 10, 'bold'),
                    bordercolor=ACCENT_DIM,
                    lightcolor=ACCENT_DIM,
                    darkcolor=ACCENT_DIM,
                    relief='flat',
                    padding=(12, 7))
    style.map('Action.TButton',
              background=[('active', '#1A3A55'), ('pressed', '#0F2A3F')],
              foreground=[('active', ACCENT_GLOW), ('pressed', ACCENT_GLOW)],
              bordercolor=[('active', ACCENT)])

    # ── Danger button
    style.configure('Danger.TButton',
                    background='#1A0A0E',
                    foreground=RED,
                    font=('Segoe UI', 10, 'bold'),
                    bordercolor='#4A1520',
                    lightcolor='#4A1520',
                    darkcolor='#4A1520',
                    relief='flat',
                    padding=(12, 7))
    style.map('Danger.TButton',
              background=[('active', RED_DIM), ('pressed', '#5A1020')],
              foreground=[('active', '#FF6677')])

    # ── Notebook (tabs)
    style.configure('TNotebook',
                    background=BG_CARD,
                    tabmargins=[2, 5, 2, 0],
                    bordercolor=BORDER)
    style.configure('TNotebook.Tab',
                    background=BG_ELEVATED,
                    foreground=TEXT_SEC,
                    font=FONT_UI,
                    padding=[12, 6],
                    bordercolor=BORDER)
    style.map('TNotebook.Tab',
              background=[('selected', BG_CARD), ('active', BG_HOVER)],
              foreground=[('selected', ACCENT), ('active', TEXT_PRI)])

    # ── Scrollbar
    style.configure('TScrollbar',
                    background=BG_ELEVATED,
                    troughcolor=BG_INPUT,
                    bordercolor=BORDER,
                    arrowcolor=TEXT_MUTED,
                    relief='flat')
    style.map('TScrollbar',
              background=[('active', ACCENT_DIM), ('pressed', ACCENT)])

    # ── Treeview
    style.configure('Treeview',
                    background=BG_INPUT,
                    foreground=TEXT_PRI,
                    fieldbackground=BG_INPUT,
                    font=FONT_MONO,
                    rowheight=28,
                    bordercolor=BORDER,
                    relief='flat')
    style.configure('Treeview.Heading',
                    background=BG_ELEVATED,
                    foreground=ACCENT,
                    font=('Segoe UI', 9, 'bold'),
                    relief='flat',
                    bordercolor=BORDER_ACC)
    style.map('Treeview',
              background=[('selected', BG_SEL)],
              foreground=[('selected', ACCENT)])

    # ── PanedWindow
    style.configure('TPanedwindow', background=BG_ROOT)
    style.configure('Sash', sashthickness=4, background=BORDER_ACC)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def dark_entry(parent, **kwargs):
    """A consistently dark-styled Entry widget."""
    e = tk.Entry(parent,
                 bg=BG_INPUT,
                 fg=TEXT_PRI,
                 insertbackground=ACCENT,
                 selectbackground=BG_SEL,
                 selectforeground=ACCENT,
                 relief='flat',
                 highlightthickness=1,
                 highlightcolor=ACCENT,
                 highlightbackground=BORDER_ACC,
                 **kwargs)
    return e


def dark_text(parent, **kwargs):
    """A consistently dark-styled Text / ScrolledText widget."""
    t = scrolledtext.ScrolledText(parent,
                                   bg=BG_INPUT,
                                   fg=TEXT_PRI,
                                   insertbackground=ACCENT,
                                   selectbackground=BG_SEL,
                                   selectforeground=ACCENT,
                                   relief='flat',
                                   highlightthickness=1,
                                   highlightcolor=ACCENT,
                                   highlightbackground=BORDER_ACC,
                                   padx=8, pady=8,
                                   **kwargs)
    # Style the scrollbar inside ScrolledText
    t.vbar.configure(bg=BG_ELEVATED, troughcolor=BG_INPUT,
                     activebackground=ACCENT_DIM, highlightthickness=0)
    return t


def dark_listbox(parent, **kwargs):
    lb = tk.Listbox(parent,
                    bg=BG_INPUT,
                    fg=TEXT_PRI,
                    selectbackground=BG_SEL,
                    selectforeground=ACCENT,
                    activestyle='none',
                    relief='flat',
                    highlightthickness=1,
                    highlightcolor=ACCENT,
                    highlightbackground=BORDER_ACC,
                    **kwargs)
    return lb


def separator(parent, orient='horizontal', color=BORDER_ACC, thickness=1):
    """Thin styled separator."""
    if orient == 'horizontal':
        f = tk.Frame(parent, bg=color, height=thickness)
        f.pack(fill=tk.X, pady=4)
    else:
        f = tk.Frame(parent, bg=color, width=thickness)
        f.pack(fill=tk.Y, padx=4)
    return f


def section_label(parent, text, **kwargs):
    """Uppercase section label in accent color."""
    lbl = tk.Label(parent,
                   text=text.upper(),
                   bg=parent.cget('bg') if hasattr(parent, 'cget') else BG_CARD,
                   fg=ACCENT,
                   font=('Segoe UI', 8, 'bold'),
                   **kwargs)
    return lbl


class CryptDiaryApp:
    """Main application class for CryptDiary (Multi-User) — Dark Edition"""

    def __init__(self, root):
        self.root = root
        self.root.title("CryptDiary  ·  Secure Multi-User Diary")
        self.root.geometry("1000x720")
        self.root.configure(bg=BG_ROOT)
        self.root.minsize(820, 580)

        # ── Start maximized (cross-platform)
        try:
            # Windows & macOS
            self.root.state('zoomed')
        except tk.TclError:
            # Linux (X11) – use attributes
            self.root.attributes('-zoomed', True)

        # ── Icon-ish window colour
        try:
            self.root.wm_attributes('-transparentcolor', '')
        except Exception:
            pass

        # Initialize managers
        self.user_manager  = UserManager()
        self.key_manager   = None
        self.crypto_manager = None
        self.diary_storage  = None

        # Current state
        self.current_user     = None
        self.current_entry_id = None
        self.is_authenticated  = False

        self.style = ttk.Style()
        apply_dark_theme(self.style)

        self.show_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ─────────────────────────────────────────────────────────────────────────
    # LOGIN / REGISTRATION
    # ─────────────────────────────────────────────────────────────────────────
    def show_login_screen(self):
        self.clear_window()

        # Full-window canvas background with subtle grid lines
        canvas = tk.Canvas(self.root, bg=BG_ROOT, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        def draw_bg(event=None):
            canvas.delete('bg_grid')
            w, h = canvas.winfo_width(), canvas.winfo_height()
            step = 44
            for x in range(0, w, step):
                canvas.create_line(x, 0, x, h, fill='#0D1825', tags='bg_grid')
            for y in range(0, h, step):
                canvas.create_line(0, y, w, y, fill='#0D1825', tags='bg_grid')
            canvas.tag_lower('bg_grid')

        canvas.bind('<Configure>', draw_bg)

        # ── Centre card
        card_width = 440
        card = tk.Frame(canvas, bg=BG_CARD, relief='flat', bd=0)
        canvas.create_window(500, 360, window=card, width=card_width)
        canvas.bind('<Configure>', lambda e: (
            draw_bg(e),
            canvas.coords(canvas.find_all()[-1], e.width // 2, e.height // 2)
        ))

        # Top accent strip
        strip = tk.Frame(card, bg=ACCENT, height=3)
        strip.pack(fill=tk.X)

        inner = tk.Frame(card, bg=BG_CARD, padx=40, pady=35)
        inner.pack(fill=tk.BOTH, expand=True)

        # ── Logo
        logo_frame = tk.Frame(inner, bg=BG_CARD)
        logo_frame.pack(pady=(0, 5))
        tk.Label(logo_frame, text='🔐', font=('Segoe UI', 32),
                 bg=BG_CARD, fg=ACCENT).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(logo_frame, text='CryptDiary',
                 font=('Segoe UI', 26, 'bold'),
                 bg=BG_CARD, fg=TEXT_PRI).pack(side=tk.LEFT, pady=5)

        tk.Label(inner,
                 text='Secure · Encrypted · Signed',
                 font=('Consolas', 10),
                 bg=BG_CARD, fg=TEXT_SEC).pack(pady=(0, 25))

        separator(inner, color=BORDER_ACC)

        # ── Fields
        section_label(inner, 'Username').pack(anchor='w', pady=(12, 3))
        self.username_entry = dark_entry(inner, font=FONT_ENTRY, width=28)
        self.username_entry.pack(fill=tk.X, pady=(0, 8), ipady=7)
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())

        section_label(inner, 'Password').pack(anchor='w', pady=(6, 3))
        self.password_entry = dark_entry(inner, show='*', font=FONT_ENTRY, width=28)
        self.password_entry.pack(fill=tk.X, pady=(0, 20), ipady=7)
        self.password_entry.bind('<Return>', lambda e: self.login())

        # ── Buttons row (now ttk buttons)
        btn_row = tk.Frame(inner, bg=BG_CARD)
        btn_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_row, text='  Login  ', command=self.login,
                   style='Action.TButton', width=12).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(btn_row, text='Register', command=self.show_registration_screen,
                   style='TButton', width=10).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(btn_row, text='Users', command=self.show_user_list,
                   style='TButton', width=8).pack(side=tk.LEFT)

        separator(inner, color=BORDER)

        tk.Label(inner,
                 text='First time? Click Register to create an account.',
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(pady=(8, 0))

        # bottom accent strip
        tk.Frame(card, bg=BG_ELEVATED, height=6).pack(fill=tk.X)

        self.username_entry.focus()

    def show_registration_screen(self):
        self.clear_window()

        outer = tk.Frame(self.root, bg=BG_ROOT)
        outer.pack(fill=tk.BOTH, expand=True)

        # Back button row (title centered)
        nav = tk.Frame(outer, bg=BG_ROOT, padx=20, pady=14)
        nav.pack(fill=tk.X)
        ttk.Button(nav, text='← Back', command=self.show_login_screen,
                   style='TButton', width=8).pack(side=tk.LEFT)
        tk.Label(nav, text='Register New Account',
                 font=('Segoe UI', 13, 'bold'),
                 bg=BG_ROOT, fg=TEXT_PRI).pack(side=tk.LEFT, expand=True, anchor='center')

        # Card
        card_holder = tk.Frame(outer, bg=BG_ROOT)
        card_holder.pack(expand=True)

        card = tk.Frame(card_holder, bg=BG_CARD, relief='flat', bd=0)
        card.pack(padx=20, pady=10)

        tk.Frame(card, bg=ACCENT, height=3).pack(fill=tk.X)

        inner = tk.Frame(card, bg=BG_CARD, padx=40, pady=30)
        inner.pack()

        def field(label, show=None):
            section_label(inner, label).pack(anchor='w', pady=(10, 3))
            e = dark_entry(inner, width=30, font=FONT_ENTRY, show=show or '')
            e.pack(fill=tk.X, pady=(0, 4), ipady=7)
            return e

        self.reg_username = field('Username *')
        self.reg_fullname = field('Full Name (optional)')
        self.reg_password = field('Password *  (min 6 characters)', show='*')
        self.reg_confirm  = field('Confirm Password *', show='*')

        separator(inner, color=BORDER_ACC)

        btn_row = tk.Frame(inner, bg=BG_CARD)
        btn_row.pack(pady=(15, 0))
        ttk.Button(btn_row, text='Create Account', command=self.register_user,
                   style='Action.TButton', width=16).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row, text='Cancel', command=self.show_login_screen,
                   style='TButton', width=10).pack(side=tk.LEFT)

        self.reg_username.focus()

    def register_user(self):
        username = self.reg_username.get().strip()
        fullname = self.reg_fullname.get().strip()
        password = self.reg_password.get()
        confirm  = self.reg_confirm.get()

        if not username:
            messagebox.showerror("Error", "Username is required")
            return
        if not password:
            messagebox.showerror("Error", "Password is required")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        result = self.user_manager.register_user(
            username=username, password=password, full_name=fullname)

        if result is True:
            messagebox.showinfo(
                "Account Created",
                f"User '{username}' registered successfully!\n\n"
                "Your keys and certificate have been generated.\n"
                "You can now log in.")
            self.show_login_screen()
        else:
            messagebox.showerror("Registration Failed", result)

    def show_user_list(self):
        users = self.user_manager.list_users()
        if not users:
            messagebox.showinfo("Users", "No users registered yet.")
            return
        user_list = "\n".join(f"  •  {u}" for u in users)
        messagebox.showinfo("Registered Users",
                            f"Total: {len(users)}\n\n{user_list}")

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        user_record = self.user_manager.authenticate_user(username, password)
        if not user_record:
            messagebox.showerror(
                "Authentication Failed",
                "Invalid username or password.\n\nPlease try again or register.")
            return

        user_dir = self.user_manager.get_user_dir(username)
        self.key_manager = KeyManager(user_dir=str(user_dir))

        if not self.key_manager.load_keystore(password):
            messagebox.showerror("Error",
                                 "Failed to load encryption keys.\n"
                                 "Your keystore may be corrupted.")
            return

        self.crypto_manager = CryptoManager(self.key_manager)
        self.diary_storage  = DiaryStorage(user_dir=str(user_dir))
        self.current_user   = user_record
        self.is_authenticated = True

        self.show_main_screen()

    # ─────────────────────────────────────────────────────────────────────────
    # MAIN SCREEN
    # ─────────────────────────────────────────────────────────────────────────
    def show_main_screen(self):
        self.clear_window()

        root_frame = tk.Frame(self.root, bg=BG_ROOT)
        root_frame.pack(fill=tk.BOTH, expand=True)

        # ── Top bar ──────────────────────────────────────────────────────────
        topbar = tk.Frame(root_frame, bg='#060A10', height=54)
        topbar.pack(fill=tk.X)
        topbar.pack_propagate(False)

        # Left — brand
        brand = tk.Frame(topbar, bg='#060A10')
        brand.pack(side=tk.LEFT, padx=18, pady=8)
        tk.Label(brand, text='🔐', font=('Segoe UI', 18),
                 bg='#060A10', fg=ACCENT).pack(side=tk.LEFT)
        tk.Label(brand, text=' CryptDiary',
                 font=('Segoe UI', 13, 'bold'),
                 bg='#060A10', fg=TEXT_PRI).pack(side=tk.LEFT)

        # Thin vertical divider
        tk.Frame(topbar, bg=BORDER_ACC, width=1).pack(side=tk.LEFT, fill=tk.Y, pady=10)

        tk.Label(topbar,
                 text=f"  {self.current_user['username']}",
                 font=('Consolas', 10),
                 bg='#060A10', fg=TEXT_SEC).pack(side=tk.LEFT, padx=10)

        # Right — action buttons (ttk)
        right_bar = tk.Frame(topbar, bg='#060A10')
        right_bar.pack(side=tk.RIGHT, padx=12, pady=8)

        def topbtn(txt, cmd, accent=False):
            style = 'Action.TButton' if accent else 'TButton'
            ttk.Button(right_bar, text=txt, command=cmd,
                       style=style, width=10 if accent else 9).pack(side=tk.LEFT, padx=3)

        topbtn('+ New Entry', self.new_entry, accent=True)
        topbtn('View Certs',  self.show_certificates_viewer)
        topbtn('Profile',     self.show_profile)
        topbtn('Switch User', self.switch_user)
        topbtn('Logout',      self.logout)

        # Accent underline
        tk.Frame(root_frame, bg=ACCENT, height=2).pack(fill=tk.X)

        # ── Content area ─────────────────────────────────────────────────────
        content = tk.Frame(root_frame, bg=BG_ROOT)
        content.pack(fill=tk.BOTH, expand=True)

        # ── Left panel — entry list ───────────────────────────────────────────
        left_panel = tk.Frame(content, bg=BG_CARD, width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)

        # Panel header
        panel_head = tk.Frame(left_panel, bg=BG_ELEVATED, pady=10, padx=14)
        panel_head.pack(fill=tk.X)
        tk.Label(panel_head, text='ENTRIES', font=('Segoe UI', 9, 'bold'),
                 bg=BG_ELEVATED, fg=ACCENT).pack(anchor='w')

        # Search
        search_frame = tk.Frame(left_panel, bg=BG_CARD, padx=10, pady=8)
        search_frame.pack(fill=tk.X)

        search_row = tk.Frame(search_frame, bg=BG_INPUT, relief='flat',
                              highlightthickness=1, highlightbackground=BORDER_ACC,
                              highlightcolor=ACCENT)
        search_row.pack(fill=tk.X)

        tk.Label(search_row, text='🔍', font=('Segoe UI', 10),
                 bg=BG_INPUT, fg=TEXT_MUTED).pack(side=tk.LEFT, padx=6, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *a: self.refresh_entry_list())
        search_e = tk.Entry(search_row, textvariable=self.search_var,
                            bg=BG_INPUT, fg=TEXT_PRI,
                            insertbackground=ACCENT,
                            relief='flat', font=('Segoe UI', 10),
                            highlightthickness=0)
        search_e.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        # Listbox
        list_wrap = tk.Frame(left_panel, bg=BG_CARD, padx=8, pady=4)
        list_wrap.pack(fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(list_wrap, bg=BG_ELEVATED,
                          troughcolor=BG_INPUT, activebackground=ACCENT_DIM,
                          highlightthickness=0, bd=0)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.entry_listbox = tk.Listbox(
            list_wrap,
            yscrollcommand=sb.set,
            bg=BG_CARD,
            fg=TEXT_PRI,
            selectbackground=BG_SEL,
            selectforeground=ACCENT,
            activestyle='none',
            relief='flat',
            highlightthickness=0,
            font=('Segoe UI', 10),
            cursor='hand2',
            borderwidth=0)
        self.entry_listbox.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self.entry_listbox.yview)
        self.entry_listbox.bind('<<ListboxSelect>>', self.on_entry_select)

        # Thin divider between panels
        tk.Frame(content, bg=BORDER_ACC, width=1).pack(side=tk.LEFT, fill=tk.Y)

        # ── Right panel — editor ──────────────────────────────────────────────
        right_panel = tk.Frame(content, bg=BG_ROOT)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        editor_wrap = tk.Frame(right_panel, bg=BG_ROOT, padx=20, pady=16)
        editor_wrap.pack(fill=tk.BOTH, expand=True)

        # Title field row
        title_row = tk.Frame(editor_wrap, bg=BG_ROOT)
        title_row.pack(fill=tk.X, pady=(0, 12))

        tk.Label(title_row, text='TITLE', font=('Segoe UI', 8, 'bold'),
                 bg=BG_ROOT, fg=ACCENT).pack(anchor='w', pady=(0, 4))

        self.title_entry = tk.Entry(title_row,
                                    bg=BG_INPUT, fg=TEXT_PRI,
                                    insertbackground=ACCENT,
                                    selectbackground=BG_SEL,
                                    selectforeground=ACCENT,
                                    relief='flat',
                                    highlightthickness=1,
                                    highlightcolor=ACCENT,
                                    highlightbackground=BORDER_ACC,
                                    font=('Segoe UI', 13),
                                    bd=0)
        self.title_entry.pack(fill=tk.X, ipady=9)

        # Content label
        tk.Label(editor_wrap, text='CONTENT', font=('Segoe UI', 8, 'bold'),
                 bg=BG_ROOT, fg=ACCENT).pack(anchor='w', pady=(6, 4))

        self.content_text = dark_text(editor_wrap,
                                       wrap=tk.WORD,
                                       font=('Segoe UI', 11))
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Status row
        status_row = tk.Frame(editor_wrap, bg=BG_ROOT)
        status_row.pack(fill=tk.X, pady=(8, 0))

        self.signature_label = tk.Label(status_row, text='',
                                         font=('Consolas', 9),
                                         bg=BG_ROOT, fg=GREEN)
        self.signature_label.pack(side=tk.LEFT)

        self.revocation_label = tk.Label(status_row, text='',
                                          font=('Consolas', 9),
                                          bg=BG_ROOT, fg=GREEN)
        self.revocation_label.pack(side=tk.LEFT, padx=(20, 0))

        # Action buttons (ttk)
        btn_bar = tk.Frame(editor_wrap, bg=BG_ROOT)
        btn_bar.pack(fill=tk.X, pady=(12, 0))

        tk.Frame(btn_bar, bg=BORDER_ACC, height=1).pack(fill=tk.X, pady=(0, 12))

        def ebtn(txt, cmd, style='TButton', w=10):
            ttk.Button(btn_bar, text=txt, command=cmd,
                       style=style, width=w).pack(side=tk.LEFT, padx=(0, 6))

        ebtn('💾 Save',     self.save_entry,           'Action.TButton', 10)
        ebtn('🗑 Delete',   self.delete_entry,          'Danger.TButton', 10)
        ebtn('↑ Export',   self.export_current_entry,   'TButton',       10)
        ebtn('↓ Import',   self.import_entry_dialog,    'TButton',       10)
        ebtn('✕ Clear',    self.clear_editor,            'TButton',       9)

        self.refresh_entry_list()

    # ─────────────────────────────────────────────────────────────────────────
    # CERTIFICATE VIEWER
    # ─────────────────────────────────────────────────────────────────────────
    def show_certificates_viewer(self):
        if not self.key_manager:
            messagebox.showerror("Error", "No key manager available.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Certificates & Keys  ·  {self.current_user['username']}")
        win.geometry("720x620")
        win.configure(bg=BG_ROOT)
        win.transient(self.root)
        win.grab_set()
        win.resizable(True, True)

        tk.Frame(win, bg=ACCENT, height=3).pack(fill=tk.X)

        # Header
        header = tk.Frame(win, bg='#060A10', padx=20, pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text='🔐  Cryptographic Materials',
                 font=('Segoe UI', 14, 'bold'),
                 bg='#060A10', fg=TEXT_PRI).pack(side=tk.LEFT)
        tk.Label(header, text=f"  /  {self.current_user['username']}",
                 font=('Consolas', 10),
                 bg='#060A10', fg=TEXT_SEC).pack(side=tk.LEFT)
        tk.Frame(win, bg=BORDER_ACC, height=1).pack(fill=tk.X)

        # Notebook
        nb_frame = tk.Frame(win, bg=BG_ROOT, padx=15, pady=10)
        nb_frame.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(nb_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        def tab_frame():
            f = tk.Frame(notebook, bg=BG_CARD, padx=14, pady=12)
            return f

        cert_frame    = tab_frame()
        pubkey_frame  = tab_frame()
        privkey_frame = tab_frame()
        revoke_frame  = tab_frame()

        notebook.add(cert_frame,    text='📜  Certificate')
        notebook.add(pubkey_frame,  text='🔑  Public Key')
        notebook.add(privkey_frame, text='⚫  Private Key')
        notebook.add(revoke_frame,  text='🚫  Revocation')

        # ── Certificate Tab ───────────────────────────────────────────────────
        if self.key_manager.certificate:
            cert_details = self.key_manager.get_certificate_details()
            cert_pem     = self.key_manager.export_certificate_pem()

            grid_frame = tk.Frame(cert_frame, bg=BG_ELEVATED,
                                  padx=14, pady=12,
                                  relief='flat',
                                  highlightthickness=1,
                                  highlightbackground=BORDER_ACC)
            grid_frame.pack(fill=tk.X, pady=(0, 10))

            tk.Label(grid_frame, text='CERTIFICATE INFORMATION',
                     font=('Segoe UI', 8, 'bold'),
                     bg=BG_ELEVATED, fg=ACCENT).grid(
                row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))

            for i, (k, v) in enumerate(cert_details.items(), start=1):
                tk.Label(grid_frame, text=f"{k.replace('_', ' ').title()}:",
                         font=('Segoe UI', 9, 'bold'),
                         bg=BG_ELEVATED, fg=TEXT_SEC).grid(
                    row=i, column=0, sticky='w', pady=3, padx=(0, 14))
                tk.Label(grid_frame, text=str(v),
                         font=('Consolas', 9),
                         bg=BG_ELEVATED, fg=TEXT_PRI).grid(
                    row=i, column=1, sticky='w', pady=3)

            self._pem_block(cert_frame, cert_pem, 'CERTIFICATE PEM', 'Certificate')
        else:
            tk.Label(cert_frame, text='No certificate available',
                     font=FONT_UI, bg=BG_CARD, fg=TEXT_SEC).pack(pady=30)

        # ── Public Key Tab ────────────────────────────────────────────────────
        if self.key_manager.public_key:
            pubkey_details = self.key_manager.get_public_key_details()
            pubkey_pem     = self.key_manager.export_public_key_pem()

            grid_frame = tk.Frame(pubkey_frame, bg=BG_ELEVATED,
                                  padx=14, pady=12,
                                  highlightthickness=1,
                                  highlightbackground=BORDER_ACC)
            grid_frame.pack(fill=tk.X, pady=(0, 10))

            tk.Label(grid_frame, text='PUBLIC KEY INFORMATION',
                     font=('Segoe UI', 8, 'bold'),
                     bg=BG_ELEVATED, fg=ACCENT).grid(
                row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))

            for i, (k, v) in enumerate(
                    {kk: vv for kk, vv in pubkey_details.items() if kk != 'pem'}.items(),
                    start=1):
                tk.Label(grid_frame, text=f"{k.replace('_', ' ').title()}:",
                         font=('Segoe UI', 9, 'bold'),
                         bg=BG_ELEVATED, fg=TEXT_SEC).grid(
                    row=i, column=0, sticky='w', pady=3, padx=(0, 14))
                tk.Label(grid_frame, text=str(v),
                         font=('Consolas', 9),
                         bg=BG_ELEVATED, fg=TEXT_PRI).grid(
                    row=i, column=1, sticky='w', pady=3)

            self._pem_block(pubkey_frame, pubkey_pem, 'PUBLIC KEY PEM', 'Public Key')
        else:
            tk.Label(pubkey_frame, text='No public key available',
                     font=FONT_UI, bg=BG_CARD, fg=TEXT_SEC).pack(pady=30)

        # ── Private Key Tab ───────────────────────────────────────────────────
        if self.key_manager.private_key:
            warn_frame = tk.Frame(privkey_frame, bg='#1A0A0E',
                                  padx=14, pady=10,
                                  highlightthickness=1,
                                  highlightbackground='#4A1520')
            warn_frame.pack(fill=tk.X, pady=(0, 12))
            tk.Label(warn_frame, text='⚠  NEVER SHARE YOUR PRIVATE KEY',
                     font=('Segoe UI', 10, 'bold'),
                     bg='#1A0A0E', fg=RED).pack(anchor='w')
            tk.Label(warn_frame,
                     text='Shown here for educational purposes only.',
                     font=FONT_SMALL, bg='#1A0A0E', fg=ORANGE).pack(anchor='w')

            pass_row = tk.Frame(privkey_frame, bg=BG_CARD)
            pass_row.pack(fill=tk.X, pady=(0, 10))
            tk.Label(pass_row, text='Encrypt with password (optional):',
                     font=FONT_SMALL, bg=BG_CARD, fg=TEXT_SEC).pack(side=tk.LEFT, padx=(0, 8))
            privkey_password = dark_entry(pass_row, show='*', width=18)
            privkey_password.pack(side=tk.LEFT, padx=(0, 8), ipady=5)

            pem_frame = tk.Frame(privkey_frame, bg=BG_CARD)
            pem_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(pem_frame,
                     text="Enter password and click 'Show Private Key'",
                     font=('Segoe UI', 9, 'italic'),
                     bg=BG_CARD, fg=TEXT_MUTED).pack(pady=20)

            def show_private_key():
                password = privkey_password.get() or None
                try:
                    privkey_pem = self.key_manager.export_private_key_pem(password)
                    for w in pem_frame.winfo_children():
                        w.destroy()
                    pt = dark_text(pem_frame, height=12, font=FONT_MONO)
                    pt.pack(fill=tk.BOTH, expand=True)
                    pt.insert('1.0', privkey_pem)
                    ttk.Button(pem_frame, text='Copy to Clipboard',
                               command=lambda: self.copy_to_clipboard(privkey_pem, 'Private Key'),
                               style='TButton', width=18).pack(pady=6)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export private key: {e}")

            ttk.Button(pass_row, text='Show Private Key',
                       command=show_private_key,
                       style='Danger.TButton', width=15).pack(side=tk.LEFT)
        else:
            tk.Label(privkey_frame, text='No private key available',
                     font=FONT_UI, bg=BG_CARD, fg=TEXT_SEC).pack(pady=30)

        # ── Revocation Tab ────────────────────────────────────────────────────
        revoked_list = self.key_manager.get_revoked_certificates()

        cur_frame = tk.Frame(revoke_frame, bg=BG_ELEVATED,
                             padx=14, pady=12,
                             highlightthickness=1,
                             highlightbackground=BORDER_ACC)
        cur_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(cur_frame, text='CURRENT CERTIFICATE STATUS',
                 font=('Segoe UI', 8, 'bold'),
                 bg=BG_ELEVATED, fg=ACCENT).pack(anchor='w', pady=(0, 6))

        if self.key_manager.certificate:
            serial     = self.key_manager.get_certificate_serial()
            is_revoked = self.key_manager.is_revoked(serial)
            tk.Label(cur_frame, text=f'Serial: {serial}',
                     font=FONT_MONO, bg=BG_ELEVATED, fg=TEXT_SEC).pack(anchor='w', pady=2)
            if is_revoked:
                tk.Label(cur_frame, text='Status:  ❌  REVOKED',
                         font=('Segoe UI', 10, 'bold'),
                         bg=BG_ELEVATED, fg=RED).pack(anchor='w', pady=4)
            else:
                tk.Label(cur_frame, text='Status:  ✅  ACTIVE',
                         font=('Segoe UI', 10, 'bold'),
                         bg=BG_ELEVATED, fg=GREEN).pack(anchor='w', pady=4)

        rev_list_frame = tk.Frame(revoke_frame, bg=BG_CARD,
                                   highlightthickness=1,
                                   highlightbackground=BORDER_ACC)
        rev_list_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(rev_list_frame, text='GLOBALLY REVOKED CERTIFICATES',
                 font=('Segoe UI', 8, 'bold'),
                 bg=BG_CARD, fg=ACCENT,
                 padx=10, pady=8).pack(anchor='w')

        if revoked_list:
            cols = ('serial', 'revoked_by', 'timestamp')
            tree = ttk.Treeview(rev_list_frame, columns=cols,
                                show='headings', height=7)
            tree.heading('serial',     text='Certificate Serial')
            tree.heading('revoked_by', text='Revoked By')
            tree.heading('timestamp',  text='Revocation Time')
            tree.column('serial',     width=200)
            tree.column('revoked_by', width=100)
            tree.column('timestamp',  width=200)
            for cert in revoked_list:
                tree.insert('', 'end',
                            values=(cert['serial'][-16:],
                                    cert['revoked_by'],
                                    cert['timestamp'][:19]))
            rsb = ttk.Scrollbar(rev_list_frame, orient=tk.VERTICAL,
                                command=tree.yview)
            rsb.pack(side=tk.RIGHT, fill=tk.Y)
            tree.configure(yscrollcommand=rsb.set)
            tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        else:
            tk.Label(rev_list_frame,
                     text='No revoked certificates in the global list.',
                     font=('Segoe UI', 9, 'italic'),
                     bg=BG_CARD, fg=TEXT_MUTED).pack(pady=20)

        # Close
        tk.Frame(win, bg=BORDER_ACC, height=1).pack(fill=tk.X, pady=(6, 0))
        close_bar = tk.Frame(win, bg=BG_ROOT, pady=10)
        close_bar.pack(fill=tk.X)
        ttk.Button(close_bar, text='Close', command=win.destroy,
                   style='TButton', width=10).pack(side=tk.RIGHT, padx=20)

    def _pem_block(self, parent, pem_text, label, copy_label):
        """Helper: render a PEM block with copy button."""
        tk.Label(parent, text=label, font=('Segoe UI', 8, 'bold'),
                 bg=BG_CARD, fg=ACCENT).pack(anchor='w', pady=(6, 4))
        pt = dark_text(parent, height=9, font=FONT_MONO)
        pt.pack(fill=tk.BOTH, expand=True)
        pt.insert('1.0', pem_text)
        pt.config(state='disabled')
        ttk.Button(parent, text='Copy to Clipboard',
                   command=lambda: self.copy_to_clipboard(pem_text, copy_label),
                   style='TButton', width=18).pack(pady=6, anchor='w')

    def copy_to_clipboard(self, text, item_type):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", f"{item_type} copied to clipboard!")

    # ─────────────────────────────────────────────────────────────────────────
    # PROFILE (ENLARGED)
    # ─────────────────────────────────────────────────────────────────────────
    def show_profile(self):
        user_info = self.user_manager.get_user_info(self.current_user['username'])

        win = tk.Toplevel(self.root)
        win.title("User Profile")
        # Increased window size for better visibility of revocation option
        win.geometry("550x720")
        win.configure(bg=BG_ROOT)
        win.transient(self.root)
        win.grab_set()
        win.resizable(True, True)  # allow resizing

        tk.Frame(win, bg=ACCENT, height=3).pack(fill=tk.X)

        header = tk.Frame(win, bg='#060A10', padx=20, pady=14)
        header.pack(fill=tk.X)
        tk.Label(header, text='👤  User Profile',
                 font=('Segoe UI', 14, 'bold'),
                 bg='#060A10', fg=TEXT_PRI).pack(side=tk.LEFT)
        tk.Frame(win, bg=BORDER_ACC, height=1).pack(fill=tk.X)

        scroll_outer = tk.Frame(win, bg=BG_ROOT)
        scroll_outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        def section(title):
            tk.Label(scroll_outer, text=title.upper(),
                     font=('Segoe UI', 8, 'bold'),
                     bg=BG_ROOT, fg=ACCENT).pack(anchor='w', pady=(10, 4))
            f = tk.Frame(scroll_outer, bg=BG_ELEVATED,
                         padx=14, pady=12,
                         highlightthickness=1,
                         highlightbackground=BORDER_ACC)
            f.pack(fill=tk.X)
            return f

        def row(parent, label, value):
            r = tk.Frame(parent, bg=BG_ELEVATED)
            r.pack(fill=tk.X, pady=3)
            tk.Label(r, text=label, font=('Segoe UI', 9),
                     bg=BG_ELEVATED, fg=TEXT_SEC, width=16, anchor='w').pack(side=tk.LEFT)
            tk.Label(r, text=value, font=('Segoe UI', 9, 'bold'),
                     bg=BG_ELEVATED, fg=TEXT_PRI).pack(side=tk.LEFT, padx=8)

        # Personal info
        pi = section('Personal Information')
        row(pi, 'Username',    user_info['username'])
        row(pi, 'Full Name',   user_info.get('full_name', 'Not set'))
        row(pi, 'Member Since', user_info['created'][:10])

        # Certificate info
        ci = section('Certificate')
        if self.key_manager and self.key_manager.certificate:
            cert_serial = str(self.key_manager.certificate.serial_number)
            is_rev = self.key_manager.is_revoked(cert_serial)
            row(ci, 'Serial (last 12)', cert_serial[-12:])
            row(ci, 'Valid Until',
                str(self.key_manager.certificate.not_valid_after.date()))
            status_row_f = tk.Frame(ci, bg=BG_ELEVATED)
            status_row_f.pack(fill=tk.X, pady=3)
            tk.Label(status_row_f, text='Status', font=('Segoe UI', 9),
                     bg=BG_ELEVATED, fg=TEXT_SEC, width=16, anchor='w').pack(side=tk.LEFT)
            if is_rev:
                tk.Label(status_row_f, text='❌  REVOKED',
                         font=('Segoe UI', 9, 'bold'),
                         bg=BG_ELEVATED, fg=RED).pack(side=tk.LEFT, padx=8)
            else:
                tk.Label(status_row_f, text='✅  ACTIVE',
                         font=('Segoe UI', 9, 'bold'),
                         bg=BG_ELEVATED, fg=GREEN).pack(side=tk.LEFT, padx=8)
            ttk.Button(ci, text='View Full Certificate',
                       command=self.show_certificates_viewer,
                       style='TButton', width=20).pack(anchor='w', pady=(8, 0))
        else:
            tk.Label(ci, text='No certificate available',
                     font=FONT_UI, bg=BG_ELEVATED, fg=ORANGE).pack(pady=8)

        # Actions
        actions_label = section('Account Actions')

        def action_btn(parent, icon, title, desc, cmd, style='TButton'):
            f = tk.Frame(parent, bg=BG_ELEVATED)
            f.pack(fill=tk.X, pady=4)
            ttk.Button(f, text=f'{icon}  {title}', command=cmd,
                       style=style, width=22).pack(anchor='w')
            tk.Label(f, text=f'  {desc}',
                     font=FONT_SMALL, bg=BG_ELEVATED, fg=TEXT_MUTED).pack(anchor='w', pady=(2, 0))

        action_btn(actions_label, '🔑', 'Change Password',
                   'Update your account password',
                   lambda: self.change_password(win), 'TButton')
        action_btn(actions_label, '✏', 'Update Full Name',
                   'Modify your display name',
                   lambda: self.update_profile(win), 'TButton')
        action_btn(actions_label, '🔐', 'View Certificates & Keys',
                   'Inspect certificate and key details',
                   self.show_certificates_viewer, 'TButton')

        tk.Frame(actions_label, bg=BORDER_ACC, height=1).pack(fill=tk.X, pady=8)

        action_btn(actions_label, '⚠', 'Revoke Certificate',
                   'WARNING: Invalidates ALL your signatures!',
                   lambda: self.revoke_own_certificate(win),
                   style='Danger.TButton')

        revoked_list = self.key_manager.get_revoked_certificates() if self.key_manager else []
        if revoked_list:
            tk.Label(scroll_outer,
                     text=f'📋  {len(revoked_list)} globally revoked certificate(s)',
                     font=FONT_SMALL, bg=BG_ROOT, fg=TEXT_MUTED).pack(anchor='w', pady=8)

        tk.Frame(win, bg=BORDER_ACC, height=1).pack(fill=tk.X)
        close_bar = tk.Frame(win, bg=BG_ROOT, pady=10)
        close_bar.pack(fill=tk.X)
        ttk.Button(close_bar, text='Close', command=win.destroy,
                   style='TButton', width=10).pack(side=tk.RIGHT, padx=20)

    def revoke_own_certificate(self, parent_window):
        if not self.key_manager or not self.key_manager.certificate:
            messagebox.showerror("Error", "No certificate loaded.")
            return

        serial = str(self.key_manager.certificate.serial_number)
        if self.key_manager.is_revoked(serial):
            messagebox.showinfo("Already Revoked", "This certificate is already revoked.")
            return

        confirm_window = tk.Toplevel(parent_window)
        confirm_window.title("Confirm Revocation")
        confirm_window.geometry("420x300")
        confirm_window.configure(bg=BG_ROOT)
        confirm_window.transient(parent_window)
        confirm_window.grab_set()
        confirm_window.resizable(False, False)

        tk.Frame(confirm_window, bg=RED, height=3).pack(fill=tk.X)

        frame = tk.Frame(confirm_window, bg=BG_ROOT, padx=28, pady=24)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='⚠  CERTIFICATE REVOCATION',
                 font=('Segoe UI', 13, 'bold'),
                 bg=BG_ROOT, fg=RED).pack(pady=(0, 12))

        warn_box = tk.Frame(frame, bg='#1A0A0E', padx=14, pady=12,
                            highlightthickness=1, highlightbackground='#4A1520')
        warn_box.pack(fill=tk.X)

        for line in ['• This action cannot be undone',
                     '• Invalidates ALL your past signatures',
                     '• Makes new signatures untrusted',
                     '• May affect shared entries']:
            tk.Label(warn_box, text=line, font=('Segoe UI', 9),
                     bg='#1A0A0E', fg=ORANGE, anchor='w').pack(anchor='w', pady=2)

        btn_row = tk.Frame(frame, bg=BG_ROOT)
        btn_row.pack(pady=(20, 0))

        def do_revoke():
            username = self.current_user['username']
            self.key_manager.revoke_certificate(serial, username)
            messagebox.showinfo("Certificate Revoked",
                                "Your certificate has been revoked.\n\n"
                                "All future verifications will reflect this.",
                                parent=parent_window)
            confirm_window.destroy()
            parent_window.destroy()
            self.show_profile()

        ttk.Button(btn_row, text='Yes, Revoke',
                   command=do_revoke,
                   style='Danger.TButton', width=14).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(btn_row, text='Cancel',
                   command=confirm_window.destroy,
                   style='TButton', width=10).pack(side=tk.LEFT)

    def change_password(self, parent):
        dialog = tk.Toplevel(parent)
        dialog.title("Change Password")
        dialog.geometry("420x320")
        dialog.configure(bg=BG_ROOT)
        dialog.transient(parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Frame(dialog, bg=ACCENT, height=3).pack(fill=tk.X)

        frame = tk.Frame(dialog, bg=BG_ROOT, padx=30, pady=24)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='🔑  Change Password',
                 font=('Segoe UI', 13, 'bold'),
                 bg=BG_ROOT, fg=TEXT_PRI).pack(pady=(0, 18))

        def fld(lbl, **kw):
            tk.Label(frame, text=lbl, font=FONT_SMALL,
                     bg=BG_ROOT, fg=TEXT_SEC).pack(anchor='w', pady=(8, 2))
            e = dark_entry(frame, show='*', font=FONT_ENTRY, **kw)
            e.pack(fill=tk.X, ipady=7)
            return e

        old_pass     = fld('Current Password')
        new_pass     = fld('New Password')
        confirm_pass = fld('Confirm New Password')

        def do_change():
            old_p = old_pass.get()
            new_p = new_pass.get()
            conf  = confirm_pass.get()
            if not all([old_p, new_p, conf]):
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return
            if new_p != conf:
                messagebox.showerror("Error", "New passwords do not match", parent=dialog)
                return
            if len(new_p) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters", parent=dialog)
                return
            result = self.user_manager.change_password(
                self.current_user['username'], old_p, new_p)
            if result is True:
                messagebox.showinfo("Success", "Password changed successfully!", parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("Error", result, parent=dialog)

        ttk.Button(frame, text='Update Password', command=do_change,
                   style='Action.TButton', width=16).pack(pady=(18, 0))

    def update_profile(self, parent):
        dialog = tk.Toplevel(parent)
        dialog.title("Update Full Name")
        dialog.geometry("400x220")
        dialog.configure(bg=BG_ROOT)
        dialog.transient(parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Frame(dialog, bg=ACCENT, height=3).pack(fill=tk.X)

        frame = tk.Frame(dialog, bg=BG_ROOT, padx=30, pady=24)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='✏  Update Full Name',
                 font=('Segoe UI', 13, 'bold'),
                 bg=BG_ROOT, fg=TEXT_PRI).pack(pady=(0, 18))

        user_info = self.user_manager.get_user_info(self.current_user['username'])

        tk.Label(frame, text='Full Name', font=FONT_SMALL,
                 bg=BG_ROOT, fg=TEXT_SEC).pack(anchor='w', pady=(0, 4))
        name_entry = dark_entry(frame, font=FONT_ENTRY)
        name_entry.insert(0, user_info.get('full_name', ''))
        name_entry.pack(fill=tk.X, ipady=7)

        def do_update():
            fullname = name_entry.get().strip()
            if self.user_manager.update_user_info(
                    self.current_user['username'], full_name=fullname):
                messagebox.showinfo("Success", "Full name updated!", parent=dialog)
                dialog.destroy()
                parent.destroy()
                self.show_profile()
            else:
                messagebox.showerror("Error", "Failed to update profile", parent=dialog)

        ttk.Button(frame, text='Save Changes', command=do_update,
                   style='Action.TButton', width=15).pack(pady=(18, 0))

    # ─────────────────────────────────────────────────────────────────────────
    # DIARY ENTRY OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def refresh_entry_list(self):
        self.entry_listbox.delete(0, tk.END)
        search_query = self.search_var.get() if hasattr(self, 'search_var') else ''
        entries = (self.diary_storage.search_entries(search_query)
                   if search_query else self.diary_storage.list_entries())

        for i, entry in enumerate(entries):
            created = datetime.fromisoformat(entry['created']).strftime('%Y-%m-%d  %H:%M')
            self.entry_listbox.insert(tk.END, f'  {entry["title"]}')
            # Alternate row shade
            if i % 2 == 0:
                self.entry_listbox.itemconfig(i, bg='#0C1220', fg=TEXT_PRI)
            else:
                self.entry_listbox.itemconfig(i, bg='#0A0F1A', fg=TEXT_PRI)

        self.entry_data = entries

    def on_entry_select(self, event):
        selection = self.entry_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        entry_metadata = self.entry_data[index]
        if not self.verify_password():
            return
        self.load_entry(entry_metadata['id'])

    def verify_password(self):
        password = simpledialog.askstring(
            "Password Required",
            "Enter your password to view this entry:",
            show='*', parent=self.root)
        if password is None:
            return False
        user_record = self.user_manager.authenticate_user(
            self.current_user['username'], password)
        if user_record:
            return True
        messagebox.showerror("Error", "Incorrect password.")
        return False

    def load_entry(self, entry_id):
        metadata, encrypted_data = self.diary_storage.load_entry(entry_id)
        if not metadata:
            messagebox.showerror("Error", "Failed to load entry")
            return
        try:
            plaintext, is_valid, is_revoked = self.crypto_manager.verify_and_decrypt(encrypted_data)

            self.current_entry_id = entry_id
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, metadata['title'])
            self.content_text.delete('1.0', tk.END)
            self.content_text.insert('1.0', plaintext)

            if is_valid:
                self.signature_label.config(
                    text='  ✓  Signature verified', fg=GREEN)
            else:
                self.signature_label.config(
                    text='  ⚠  Signature invalid', fg=ORANGE)

            if is_revoked:
                self.revocation_label.config(
                    text='  ❌  Certificate REVOKED', fg=RED)
            else:
                self.revocation_label.config(
                    text='  ✓  Certificate active', fg=GREEN)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt entry: {e}")

    def new_entry(self):
        self.clear_editor()
        self.current_entry_id = None

    def save_entry(self):
        title   = self.title_entry.get().strip()
        content = self.content_text.get('1.0', tk.END).strip()

        if not title:
            messagebox.showerror("Error", "Please enter a title")
            return
        if not content:
            messagebox.showerror("Error", "Please enter content")
            return

        try:
            if self.key_manager.certificate:
                cert_serial = str(self.key_manager.certificate.serial_number)
                if self.key_manager.is_revoked(cert_serial):
                    if not messagebox.askyesno(
                            "Certificate Revoked",
                            "Your certificate is revoked!\n\n"
                            "Entries saved now will have invalid signatures.\n"
                            "Continue anyway?"):
                        return

            encrypted_data = self.crypto_manager.encrypt_and_sign(content)

            if self.current_entry_id:
                self.diary_storage.update_entry(
                    self.current_entry_id, title=title, encrypted_data=encrypted_data)
                messagebox.showinfo("Saved", "Entry updated successfully")
            else:
                entry_id = self.diary_storage.save_entry(title, encrypted_data)
                self.current_entry_id = entry_id
                messagebox.showinfo("Saved", "Entry saved successfully")

            self.refresh_entry_list()
            self.signature_label.config(
                text='  ✓  Encrypted and signed', fg=GREEN)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")

    def delete_entry(self):
        if not self.current_entry_id:
            messagebox.showwarning("Warning", "No entry selected")
            return
        if not self.verify_password():
            return
        if messagebox.askyesno("Confirm Delete",
                               "Are you sure you want to delete this entry?"):
            try:
                self.diary_storage.delete_entry(self.current_entry_id)
                self.clear_editor()
                self.refresh_entry_list()
                messagebox.showinfo("Deleted", "Entry deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete entry: {e}")

    def export_current_entry(self):
        if not self.current_entry_id:
            messagebox.showwarning("Warning", "No entry selected to export.")
            return
        if not self.verify_password():
            return
        metadata, encrypted_data = self.diary_storage.load_entry(self.current_entry_id)
        if not metadata:
            messagebox.showerror("Error", "Could not load entry.")
            return
        try:
            package = self.crypto_manager.export_entry(
                self.current_entry_id, metadata, encrypted_data)
            filename = filedialog.asksaveasfilename(
                defaultextension=".cdpkg",
                filetypes=[("CryptDiary Package", "*.cdpkg"), ("All files", "*.*")])
            if filename:
                with open(filename, 'w') as f:
                    json.dump(package, f, indent=2)
                messagebox.showinfo("Exported", "Entry exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def import_entry_dialog(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CryptDiary Package", "*.cdpkg"), ("All files", "*.*")])
        if not filename:
            return
        try:
            with open(filename, 'r') as f:
                package = json.load(f)

            metadata, encrypted_data, sig_valid, is_revoked, cert = \
                self.crypto_manager.import_entry(package)

            status        = "✓ Valid"   if sig_valid   else "✗ Invalid"
            revoked_status = "✓ Active"  if not is_revoked else "❌ REVOKED"

            msg  = f"📝  {metadata['title']}\n"
            msg += f"👤  From: {metadata['imported_from']}\n"
            msg += f"📅  Created: {metadata['created'][:10]}\n"
            msg += f"🔏  Signature: {status}\n"
            msg += f"🔐  Certificate: {revoked_status}\n"
            if not sig_valid:
                msg += "\n⚠  WARNING: Signature is invalid!"
            if is_revoked:
                msg += "\n⚠  WARNING: Certificate has been revoked!"

            messagebox.showinfo("Import Result", msg)

            if messagebox.askyesno("Save Entry", "Save this imported entry?"):
                if not self.verify_password():
                    return
                try:
                    plaintext   = self.crypto_manager.decrypt_entry(encrypted_data)
                    new_encrypted = self.crypto_manager.encrypt_and_sign(plaintext)
                    title = f"[Imported] {metadata['title']}"
                    self.diary_storage.save_entry(title, new_encrypted)
                    self.refresh_entry_list()
                    messagebox.showinfo("Success",
                                        "Entry saved and re-encrypted for you.")
                except Exception:
                    messagebox.showerror(
                        "Decryption Failed",
                        "Could not decrypt the imported entry.\n"
                        "It may be encrypted for another user.\n\n"
                        "Signature verification still demonstrates authentication.")
        except Exception as e:
            messagebox.showerror("Import Failed", str(e))

    def clear_editor(self):
        self.current_entry_id = None
        self.title_entry.delete(0, tk.END)
        self.content_text.delete('1.0', tk.END)
        self.signature_label.config(text='')
        self.revocation_label.config(text='')

    # ─────────────────────────────────────────────────────────────────────────
    # SESSION MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────
    def switch_user(self):
        if messagebox.askyesno("Switch User",
                               "Switch to a different account?"):
            self.logout()

    def logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.is_authenticated  = False
            self.current_user      = None
            self.key_manager       = None
            self.crypto_manager    = None
            self.diary_storage     = None
            self.show_login_screen()


def main():
    root = tk.Tk()
    app  = CryptDiaryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

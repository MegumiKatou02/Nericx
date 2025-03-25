import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from datetime import datetime
import webbrowser
from PIL import Image, ImageTk
import io
import json
import config.config
import re

class OsuUserTab(ttk.Frame):
    def __init__(self, master, db_manager, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.db_manager = db_manager
        self.app = app
        self.access_token = None
        self.token_expires = None
        self.current_user_data = None
        self.current_user_id = None
        self.create_widgets()
        self.authenticate()

    def authenticate(self):
        try:
            auth_url = "https://osu.ppy.sh/oauth/token"
            data = {
                "client_id": config.config.OSU_CLIENT_ID,
                "client_secret": config.config.OSU_CLIENT_SECRET,
                "grant_type": "client_credentials",
                "scope": "public"
            }
            response = requests.post(auth_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires = datetime.now().timestamp() + token_data["expires_in"]
            print("Authenticated successfully with osu! API v2")
        except Exception as e:
            messagebox.showerror("Authentication Failed", f"Could not authenticate with osu! API: {str(e)}")

    def create_widgets(self):
        search_frame = ttk.LabelFrame(self, text="Tìm kiếm trên osu!")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_frame, text="Username hoặc ID:").grid(row=0, column=0, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_user)
        search_btn.grid(row=0, column=2, padx=5, pady=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_player_info_tab()
        self.create_top_scores_tab()
        self.create_recent_beatmaps_tab()

    def create_player_info_tab(self):
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Thông tin người chơi")

        self.avatar_label = ttk.Label(self.results_frame)
        self.avatar_label.grid(row=0, column=0, rowspan=5, padx=10, pady=10)

        self.info_labels = {
            "username": ttk.Label(self.results_frame, text="Username: ", font=('Helvetica', 10, 'bold')),
            "rank": ttk.Label(self.results_frame, text="Global Rank: "),
            "pp": ttk.Label(self.results_frame, text="Performance Points: "),
            "accuracy": ttk.Label(self.results_frame, text="Accuracy: "),
            "playcount": ttk.Label(self.results_frame, text="Play Count: "),
            "country": ttk.Label(self.results_frame, text="Country: ")
        }

        for i, (key, label) in enumerate(self.info_labels.items()):
            label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)

        btn_frame = ttk.Frame(self.results_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.profile_btn = ttk.Button(
            btn_frame,
            text="Xem Profile Đầy Đủ",
            command=self.open_profile,
            state=tk.DISABLED
        )
        self.profile_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(
            btn_frame,
            text="Xuất Thông Tin Người Chơi (JSON)",
            command=self.export_user_data,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)

    def create_top_scores_tab(self):
        self.scores_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scores_frame, text="Top Scores")

        self.scores_tree = ttk.Treeview(self.scores_frame, columns=("Beatmap", "Score", "PP", "Accuracy"), show="headings")
        self.scores_tree.heading("Beatmap", text="Beatmap")
        self.scores_tree.heading("Score", text="Score")
        self.scores_tree.heading("PP", text="PP")
        self.scores_tree.heading("Accuracy", text="Accuracy")

        self.scores_tree.column("Beatmap", width=200)
        self.scores_tree.column("Score", width=100)
        self.scores_tree.column("PP", width=80)
        self.scores_tree.column("Accuracy", width=80)

        self.scores_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scores_tree.bind("<Double-1>", self.open_beatmap_from_top_scores)

    def create_recent_beatmaps_tab(self):
        self.recent_beatmaps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recent_beatmaps_frame, text="Beatmaps gần đây")

        self.recent_beatmaps_tree = ttk.Treeview(self.recent_beatmaps_frame, 
            columns=("Beatmap", "Difficulty", "PP", "Accuracy", "Score", "Date"), 
            show="headings"
        )
        self.recent_beatmaps_tree.heading("Beatmap", text="Beatmap")
        self.recent_beatmaps_tree.heading("Difficulty", text="Difficulty")
        self.recent_beatmaps_tree.heading("PP", text="PP")
        self.recent_beatmaps_tree.heading("Accuracy", text="Accuracy")
        self.recent_beatmaps_tree.heading("Score", text="Score")
        self.recent_beatmaps_tree.heading("Date", text="Played Date")

        self.recent_beatmaps_tree.column("Beatmap", width=200)
        self.recent_beatmaps_tree.column("Difficulty", width=100)
        self.recent_beatmaps_tree.column("PP", width=80)
        self.recent_beatmaps_tree.column("Accuracy", width=80)
        self.recent_beatmaps_tree.column("Score", width=100)
        self.recent_beatmaps_tree.column("Date", width=150)

        self.recent_beatmaps_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.recent_beatmaps_tree.bind("<Double-1>", self.open_beatmap_from_recent)

    def open_beatmap_from_top_scores(self, event):
        selected_item = self.scores_tree.selection()
        if not selected_item:
            return

        item_data = self.scores_tree.item(selected_item[0])
        beatmap_name = item_data["values"][0]

        if not hasattr(self, 'top_scores_data'):
            return
        
        for score in self.top_scores_data:
            expected_name = f"{score['beatmapset']['title']}"
            if expected_name == beatmap_name:
                beatmap_id = score['beatmap']['id']
                webbrowser.open(f"https://osu.ppy.sh/beatmaps/{beatmap_id}")
                break

    def open_beatmap_from_recent(self, event):
        selected_item = self.recent_beatmaps_tree.selection()
        if not selected_item:
            return

        item_data = self.recent_beatmaps_tree.item(selected_item[0])
        beatmap_name = item_data["values"][0] 

        if not hasattr(self, 'recent_scores_data'):
            return

        for score in self.recent_scores_data:
            if f"{score['beatmapset']['title']} [{score['beatmapset']['artist']}]" == beatmap_name:
                beatmap_id = score['beatmap']['id']
                webbrowser.open(f"https://osu.ppy.sh/beatmaps/{beatmap_id}")
                break

    def search_user(self):
        if not self.access_token:
            messagebox.showerror("Error", "Not authenticated with osu! API")
            return

        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Yêu cầu có username hoặc ID")
            return

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            url = f"https://osu.ppy.sh/api/v2/users/{query}"

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            self.current_user_data = user_data
            self.display_user_info(user_data)
            self.load_user_scores()
            self.load_recent_beatmaps() 

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                messagebox.showerror("Error", "Không tìm thấy người chơi")
            else:
                messagebox.showerror("API Error", f"Error fetching user data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_recent_beatmaps(self):
        if not hasattr(self, 'current_user_id') or not self.current_user_id or not self.access_token:
            return

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            url = f"https://osu.ppy.sh/api/v2/users/{self.current_user_id}/scores/recent"
            params = {
                "limit": 20,
                "include_fails": 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            recent_scores = response.json()
            self.recent_scores_data = recent_scores 
            
            self.recent_beatmaps_tree.delete(*self.recent_beatmaps_tree.get_children())
            
            for score in recent_scores:
                beatmap_info = score.get('beatmap', {})
                beatmapset_info = score.get('beatmapset', {})
                
                created_at = score.get('created_at')
                if created_at:
                    try:
                        created_at = created_at.replace('Z', '+00:00') 
                        date_str = datetime.fromisoformat(created_at).strftime("%d-%m-%Y %H:%M")
                    except ValueError:
                        date_str = "N/A"
                else:
                    date_str = "N/A"
                    
                self.recent_beatmaps_tree.insert("", "end", values=(
                    f"{beatmapset_info.get('title', 'Unknown')} [{beatmapset_info.get('artist', '')}]",
                    beatmap_info.get('version', 'N/A'),
                    f"{score.get('pp', 0):.2f}" if score.get('pp') else "N/A",
                    f"{score.get('accuracy', 0) * 100:.2f}%" if score.get('accuracy') else "N/A",
                    f"{score.get('score', 0):,}",
                    date_str
                ))
        except Exception as e:
            print(f"Error getting recent beatmaps: {e}")
            messagebox.showerror("Recent Beatmaps Error", f"Could not fetch recent beatmaps: {str(e)}")

    def display_user_info(self, user_data):
        try:
            avatar_url = user_data.get("avatar_url")
            if avatar_url:
                response = requests.get(avatar_url)
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((128, 128), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.avatar_label.config(image=photo)
                self.avatar_label.image = photo
            else:
                self.avatar_label.config(image='', text='No avatar')
        except Exception as e:
            print(f"Error loading avatar: {e}")
            self.avatar_label.config(image='', text='Error loading avatar')

        stats = user_data.get("statistics", {})
        
        info_values = {
            "username": user_data.get("username", "N/A"),
            "rank": f"#{stats.get('global_rank', 'N/A')}",
            "pp": f"{stats.get('pp', 0):.2f} pp",
            "accuracy": f"{stats.get('hit_accuracy', 0):.2f}%",
            "playcount": f"{stats.get('play_count', 0):,}",
            "country": f"{user_data.get('country', {}).get('name', 'N/A')} (#{stats.get('country_rank', 'N/A')})"
        }

        for key, label in self.info_labels.items():
            label.config(text=f"{label.cget('text').split(':')[0]}: {info_values[key]}")

        if user_data.get("id"):
            self.current_user_id = user_data["id"]
            self.profile_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
        else:
            self.profile_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.DISABLED)

    def open_profile(self):
        if hasattr(self, 'current_user_id') and self.current_user_id:
            webbrowser.open(f"https://osu.ppy.sh/users/{self.current_user_id}")

    def export_user_data(self):
        if not self.current_user_data:
            messagebox.showwarning("Warning", "No user data to export")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_user_data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Export Successful", f"User data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export user data: {str(e)}")

    def load_user_scores(self):
        if not hasattr(self, 'current_user_id') or not self.current_user_id or not self.access_token:
            return

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            url = f"https://osu.ppy.sh/api/v2/users/{self.current_user_id}/scores/best"
            params = {"limit": 20}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            scores = response.json()
            self.top_scores_data = scores 
            
            self.scores_tree.delete(*self.scores_tree.get_children())
            
            for score in scores:
                beatmap = score.get('beatmapset', {}).get('title', 'Unknown Beatmap')
                self.scores_tree.insert("", "end", values=(
                    beatmap,
                    f"{score.get('score', 0):,}",
                    f"{score.get('pp', 0):.2f}",
                    f"{score.get('accuracy', 0) * 100:.2f}%",
                ))
        except Exception as e:
            print(f"Error getting scores: {e}")
            messagebox.showerror("Scores Error", f"Could not fetch user scores: {str(e)}")
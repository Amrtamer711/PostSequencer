import cv2
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import os
import shutil
import webbrowser
from datetime import datetime
from collections import Counter

class ArtworkSequencer:
	def __init__(self):
		self.coords_side1 = []
		self.coords_side2 = []
		self.current_side = 1
		self.mode = None
		self.num_Artworks = 8
		self.img = None
		self.img_display = None
		self.window_name = "Artwork Sequencer - Click lamp posts in order"
		self.current_index = 1
		self.use_images = False
		self.artwork_icons = []  # Display-sized icons
		self.artwork_icons_full = []  # Original loaded icons (full quality)
		self.artwork_icon_paths = []  # Original file paths when available
		self.artwork_icon_size = 128
		self.display_scale_x = 1.0
		self.display_scale_y = 1.0
		self.icon_scale_ratio = 0.03  # ~3% of min dimension
		self.road_image_path = None
		self.show_images_on_canvas = False  # Draw only numbers by default
		self.placements = []  # unified placements list: [{x,y,s1_num,s2_num,s1_icon,s2_icon}]
		self._overlay_win = None
	
	def setup_gui(self):
		root = tk.Tk()
		root.title("Artwork Setup Configuration")
		root.geometry("500x460")
		
		# Main container
		main_container = tk.Frame(root)
		main_container.pack(fill='both', expand=True, padx=30, pady=30)
		
		# Title
		tk.Label(main_container, text="Artwork Sequencing Setup", 
				font=("Arial", 24, "bold")).pack(pady=(0, 30))
		
		# Road type section
		road_section = tk.Frame(main_container)
		road_section.pack(pady=15)
		
		tk.Label(road_section, text="Select road type:", 
				font=("Arial", 14)).pack(pady=(0, 10))
		
		self.road_type = tk.StringVar(value="single")
		
		radio_container = tk.Frame(road_section)
		radio_container.pack()
		
		single_radio = tk.Radiobutton(radio_container, text="Single Way", 
								  variable=self.road_type, value="single", 
								  font=("Arial", 13))
		single_radio.pack(side=tk.LEFT, padx=15)
		
		two_radio = tk.Radiobutton(radio_container, text="Two Way", 
								variable=self.road_type, value="two", 
								font=("Arial", 13))
		two_radio.pack(side=tk.LEFT, padx=15)
		
		# Artwork count section
		Artwork_section = tk.Frame(main_container)
		Artwork_section.pack(pady=20)
		
		tk.Label(Artwork_section, text="Number of unique Artworks:", 
				font=("Arial", 14)).pack(pady=(0, 10))
		
		self.Artwork_entry = tk.Entry(Artwork_section, font=("Arial", 16), 
										width=8, justify='center', relief=tk.SOLID, bd=1)
		self.Artwork_entry.insert(0, "8")
		self.Artwork_entry.pack()
		
		# Buttons row
		button_row = tk.Frame(main_container)
		button_row.pack(pady=(30, 0))
		
		start_btn = tk.Button(button_row, text="START", 
							 command=self.start_sequencing, 
							 font=("Arial", 18, "bold"),
							 width=12, height=2, 
							 relief=tk.GROOVE, bd=2)
		start_btn.pack(side='left', padx=8)
		
		pics_btn = tk.Button(button_row, text="ADD PICTURES", 
							command=self.start_images_flow, 
							font=("Arial", 14, "bold"),
							width=16, height=2, 
							relief=tk.GROOVE, bd=2)
		pics_btn.pack(side='left', padx=8)
		
		# Center the window
		root.update_idletasks()
		x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
		y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
		root.geometry(f'+{x}+{y}')
		
		self.root = root
		root.mainloop()
	
	def start_images_flow(self):
		"""Begin the image-based artwork configuration flow."""
		try:
			self.num_Artworks = int(self.Artwork_entry.get())
			if self.num_Artworks < 1:
				raise ValueError
		except ValueError:
			messagebox.showerror("Error", "Please enter a valid number of Artworks (minimum 1)")
			return
		self.mode = self.road_type.get()
		self.use_images = True
		# Close initial setup window
		self.root.destroy()
		# Open image selection UI
		self.configure_artwork_images()
	
	def configure_artwork_images(self):
		"""Second screen: add images for each Artwork index using a + button."""
		self.artwork_icons = []
		self.artwork_icons_full = []
		self.artwork_icon_paths = []
		window = tk.Tk()
		window.title("Select Artwork Images")
		window.geometry("520x480")
		
		container = tk.Frame(window)
		container.pack(fill='both', expand=True, padx=20, pady=20)
		
		tk.Label(container, text=f"Add {self.num_Artworks} images to use instead of numbers", 
				 font=("Arial", 14, "bold")).pack(anchor='w')
		self.imgs_status_var = tk.StringVar(value=f"0 / {self.num_Artworks} selected")
		tk.Label(container, textvariable=self.imgs_status_var, font=("Arial", 11)).pack(anchor='w', pady=(4, 12))
		
		list_frame = tk.Frame(container, relief=tk.SOLID, bd=1)
		list_frame.pack(fill='both', expand=True)
		
		self.images_listbox = tk.Listbox(list_frame, font=("Arial", 12))
		self.images_listbox.pack(fill='both', expand=True)
		
		controls = tk.Frame(container)
		controls.pack(fill='x', pady=(12, 0))
		
		add_btn = tk.Button(controls, text="+ Add Image(s)", font=("Arial", 12), width=14, relief=tk.GROOVE, bd=2,
							 command=self._on_add_artwork_images)
		add_btn.pack(side='left')
		
		clear_btn = tk.Button(controls, text="Clear All", font=("Arial", 12), width=10, relief=tk.GROOVE, bd=2,
							  command=self._on_clear_artwork_images)
		clear_btn.pack(side='left', padx=10)
		
		self.continue_btn = tk.Button(container, text="Continue", font=("Arial", 14, "bold"),
									 width=16, height=1, relief=tk.GROOVE, bd=2,
									 state=tk.DISABLED,
									 command=lambda: self._on_finish_artwork_images(window))
		self.continue_btn.pack(pady=(16, 0))
		
		# Center
		window.update_idletasks()
		x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
		y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
		window.geometry(f'+{x}+{y}')
		window.mainloop()
	
	def _on_add_artwork_images(self):
		if len(self.artwork_icons) >= self.num_Artworks:
			return
		paths = filedialog.askopenfilenames(
			title="Select image files",
			filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp")]
		)
		if not paths:
			return
		for path in paths:
			if len(self.artwork_icons) >= self.num_Artworks:
				break
			icon = cv2.imread(path, cv2.IMREAD_UNCHANGED)
			if icon is None:
				continue
			# Keep original-quality icon; display-sized icons will be created later
			self.artwork_icons_full.append(icon)
			self.artwork_icon_paths.append(path)
			# Maintain same length in display list (placeholder) to match counts
			self.artwork_icons.append(icon)
			base = os.path.basename(path)
			self.images_listbox.insert(tk.END, f"Artwork #{len(self.artwork_icons)}: {base}")
		self._update_images_status()
	
	def _on_clear_artwork_images(self):
		self.artwork_icons = []
		self.artwork_icons_full = []
		self.artwork_icon_paths = []
		self.images_listbox.delete(0, tk.END)
		self._update_images_status()
	
	def _update_images_status(self):
		self.imgs_status_var.set(f"{len(self.artwork_icons)} / {self.num_Artworks} selected")
		if len(self.artwork_icons) == self.num_Artworks:
			self.continue_btn.config(state=tk.NORMAL)
		else:
			self.continue_btn.config(state=tk.DISABLED)
	
	def _on_finish_artwork_images(self, window):
		if len(self.artwork_icons) != self.num_Artworks:
			return
		window.destroy()
		# Proceed to sequencing (will ask for the road image next)
		self.start_sequencing()
	
	def start_sequencing(self):
		# If coming from images flow, num_Artworks is already set and the Entry widget
		# may have been destroyed. Only read from Entry when not using images.
		if not self.use_images:
			try:
				self.num_Artworks = int(self.Artwork_entry.get())
				if self.num_Artworks < 1:
					raise ValueError
			except ValueError:
				messagebox.showerror("Error", "Please enter a valid number of Artworks (minimum 1)")
				return
		
		self.mode = self.road_type.get()
		
		# Close the setup window if it exists
		if hasattr(self, 'root') and self.root:
			try:
				self.root.destroy()
			except Exception:
				pass
		
		# Ensure a Tk context exists for file dialogs
		temp_root = None
		if tk._default_root is None:
			temp_root = tk.Tk()
			temp_root.withdraw()
		
		file_path = filedialog.askopenfilename(
			title="Select the road image",
			filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
		)
		
		# Destroy temporary root if we created one
		if temp_root is not None:
			try:
				temp_root.destroy()
			except Exception:
				pass
		
		if not file_path:
			return
		
		self.img = cv2.imread(file_path)
		if self.img is None:
			messagebox.showerror("Error", "Could not load the image")
			return
		self.road_image_path = file_path
		
		# Immediately export and open the HTML Sequencer editor
		index_path = self.export_editor()
		try:
			webbrowser.open(f"file://{index_path}")
		except Exception:
			pass
		return
	
	def click_event(self, event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			orig_x = int(round(x / self.display_scale_x))
			orig_y = int(round(y / self.display_scale_y))
			idx = self._find_nearest_placement(orig_x, orig_y, radius_px=20)
			self._open_placement_dialog(orig_x, orig_y, idx)
			self._redraw_display_overlay()
			cv2.imshow(self.window_name, self.img_display)
	
	def run_sequencing(self):
		# Not used in HTML-based editing flow; kept for compatibility if needed.
		cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
		cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
		cv2.imshow(self.window_name, self.img_display)
		cv2.setMouseCallback(self.window_name, self.click_event)
		
		if self.mode == "single":
			print("\nSINGLE WAY MODE")
			print("Click on lamp posts in sequence. Press ENTER when done.")
			self.draw_instruction("Press Enter to finish")
		else:
			print("\nTWO WAY MODE - SIDE 1 (Blue markers)")
			print("Click on lamp posts for the first side in sequence.")
			print("Press ENTER to switch to the second side.")
			print("After finishing SIDE 2, press ENTER again to end.")
			self.draw_instruction("Side 1 — Press Enter to switch to Side 2")
		
		while True:
			key = cv2.waitKey(1) & 0xFF
			
			if key in (13, 10):  # ENTER key
				if self.mode == "two" and self.current_side == 1:
					self.current_side = 2
					print("\nSwitched to SIDE 2 (Red markers)")
					print("Click on lamp posts for the second side in sequence.")
					print("Press ENTER to finish.")
					self.draw_instruction("Side 2 — Press Enter to finish")
				else:
					break
		
		cv2.destroyAllWindows()
		self.save_and_display_results()
	
	def draw_instruction(self, text: str) -> None:
		"""Draw a subtle instruction banner at the top of the display image."""
		if self.img_display is None:
			return
		overlay = self.img_display.copy()
		height, width = overlay.shape[:2]
		banner_height = 34
		cv2.rectangle(overlay, (0, 0), (width, banner_height), (255, 255, 255), -1)
		cv2.putText(overlay, text, (10, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
		self.img_display = overlay
		cv2.imshow(self.window_name, self.img_display)
	
	def get_output_dir(self):
		"""Return a stable output directory in the user's Documents folder."""
		documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
		output_dir = os.path.join(documents_dir, "Artwork Sequencer Outputs")
		os.makedirs(output_dir, exist_ok=True)
		return output_dir
	
	def save_and_display_results(self):
		# Create a clean version without dots for saving
		img_clean = self.img.copy()
		
		# Draw final boxed rectangles from placements (numbers or pictures selected)
		box_w = max(16, int(min(self.img.shape[0], self.img.shape[1]) * 0.015))
		box_h = box_w
		for p in self.placements:
			x = p['x']; y = p['y']
			if self.mode == 'single':
				# Single small box centered
				self._draw_box_with_label(img_clean, x, y, box_w, box_h, (255,0,0), str(p.get('s1_num') or p.get('s1_icon') or ''))
			else:
				# Two adjacent boxes centered around (x,y)
				half = box_w // 2
				# left (side1, blue)
				self._draw_box_with_label(img_clean, x - half, y, box_w, box_h, (255,0,0), str(p.get('s1_num') or p.get('s1_icon') or ''))
				# right (side2, red)
				self._draw_box_with_label(img_clean, x + half, y, box_w, box_h, (0,0,255), str(p.get('s2_num') or p.get('s2_icon') or ''))
		
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		output_dir = self.get_output_dir()
		filename = f"Artwork_sequence_{timestamp}.png"
		full_path = os.path.join(output_dir, filename)
		cv2.imwrite(full_path, img_clean)
		print(f"\nImage saved as: {full_path}")
		
		# Display the version with dots (self.img_display)
		cv2.imshow("Final Result - Artwork Sequence", self.img_display)
		
		# Show the summary popup (this will keep the image window open)
		self.show_summary()
		
		# Close all OpenCV windows after summary is closed
		cv2.destroyAllWindows()
	
	def _resize_icon_to_max(self, icon, max_edge: int):
		h, w = icon.shape[:2]
		scale = max_edge / max(h, w)
		if scale == 1.0:
			return icon
		new_w = max(1, int(round(w * scale)))
		new_h = max(1, int(round(h * scale)))
		return cv2.resize(icon, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
	
	def _make_display_icons(self, screen_w: int, screen_h: int, target_size: int) -> None:
		if not self.artwork_icons_full:
			return
		resized = []
		for icon_full in self.artwork_icons_full:
			resized.append(self._resize_icon_to_max(icon_full, target_size))
		self.artwork_icons = resized
	
	def _overlay_icon_center(self, base_img, icon_img, cx: int, cy: int, offset=(0, 0), border_color=None) -> None:
		"""Overlay icon_img centered at (cx, cy) on base_img, with optional offset and colored border.
		border_color expects BGR tuple (e.g., blue (255,0,0) or red (0,0,255))."""
		ih, iw = icon_img.shape[:2]
		ox, oy = offset
		cx_adj = cx + int(ox)
		cy_adj = cy + int(oy)
		x1 = int(cx_adj - iw / 2)
		y1 = int(cy_adj - ih / 2)
		x2 = x1 + iw
		y2 = y1 + ih
		H, W = base_img.shape[:2]
		# Clip to base image bounds
		if x1 >= W or y1 >= H or x2 <= 0 or y2 <= 0:
			return
		bx1 = max(0, x1)
		by1 = max(0, y1)
		bx2 = min(W, x2)
		by2 = min(H, y2)
		ix1 = bx1 - x1
		iy1 = by1 - y1
		ix2 = ix1 + (bx2 - bx1)
		iy2 = iy1 + (by2 - by1)
		roi = base_img[by1:by2, bx1:bx2]
		icon_crop = icon_img[iy1:iy2, ix1:ix2]
		if icon_crop.shape[2] == 4:
			# BGRA with alpha blending
			b, g, r, a = cv2.split(icon_crop)
			alpha = a.astype(float) / 255.0
			alpha = cv2.merge([alpha, alpha, alpha])
			fore = cv2.merge([b.astype(float), g.astype(float), r.astype(float)])
			back = roi.astype(float)
			blended = cv2.add(fore * alpha, back * (1 - alpha))
			roi[:] = blended.astype(roi.dtype)
		else:
			roi[:] = icon_crop
		# Optional border
		if border_color is not None:
			cv2.rectangle(base_img, (bx1, by1), (bx2 - 1, by2 - 1), border_color, thickness=2)
	
	def show_summary(self):
		root = tk.Tk()
		root.title("Artwork Requirements Summary")
		
		# Main container
		main_container = tk.Frame(root)
		main_container.pack(fill='both', expand=True, padx=24, pady=20)
		
		# Title
		tk.Label(main_container, text="Artwork Requirements Summary", 
				font=("Arial", 20, "bold")).pack(anchor='w', pady=(0, 10))
		
		# Project summary small block
		meta_frame = tk.Frame(main_container)
		meta_frame.pack(fill='x', pady=(0, 12))
		
		def add_meta(label_text, value_text):
			row = tk.Frame(meta_frame)
			row.pack(anchor='w')
			tk.Label(row, text=label_text, font=("Arial", 12)).pack(side='left')
			tk.Label(row, text=value_text, font=("Arial", 12, "bold"), padx=8).pack(side='left')
		
		if self.mode == "single":
			add_meta("Road Type:", "Single Way")
			add_meta("Unique Artworks:", str(self.num_Artworks))
			add_meta("Total Lamp Posts:", str(len(self.coords_side1)))
		else:
			add_meta("Road Type:", "Two Way")
			add_meta("Unique Artworks:", str(self.num_Artworks))
			add_meta("Side 1 Lamp Posts:", str(len(self.coords_side1)))
			add_meta("Side 2 Lamp Posts:", str(len(self.coords_side2)))
			add_meta("Total Lamp Posts:", str(len(self.coords_side1) + len(self.coords_side2)))
		
		# Table container
		table_container = tk.Frame(main_container)
		table_container.pack(fill='both', expand=True)
		
		columns_single = ("Artwork", "Count")
		columns_two = ("Artwork", "Total", "Side 1", "Side 2")
		
		# Determine table height based on data size, with a reasonable cap
		if self.mode == "single":
			desired_rows = max(5, min(self.num_Artworks, 18))
			labels = [((i % self.num_Artworks) + 1) for i in range(len(self.coords_side1))]
			counter = Counter(labels)
			tree = ttk.Treeview(table_container, columns=columns_single, show="headings", height=desired_rows)
			tree.heading("Artwork", text="Artwork")
			tree.heading("Count", text="Count")
			tree.column("Artwork", width=180, anchor='w', stretch=True)
			tree.column("Count", width=100, anchor='w', stretch=False)
			for n in range(1, self.num_Artworks + 1):
				tree.insert('', 'end', values=(f"Artwork #{n}", counter.get(n, 0)))
		else:
			desired_rows = max(5, min(self.num_Artworks, 18))
			labels1 = [((i % self.num_Artworks) + 1) for i in range(len(self.coords_side1))]
			labels2 = [((i % self.num_Artworks) + 1) for i in range(len(self.coords_side2))]
			counter1 = Counter(labels1)
			counter2 = Counter(labels2)
			tree = ttk.Treeview(table_container, columns=columns_two, show="headings", height=desired_rows)
			tree.heading("Artwork", text="Artwork")
			tree.heading("Total", text="Total")
			tree.heading("Side 1", text="Side 1")
			tree.heading("Side 2", text="Side 2")
			tree.column("Artwork", width=220, anchor='w', stretch=True)
			tree.column("Total", width=80, anchor='w', stretch=False)
			tree.column("Side 1", width=80, anchor='w', stretch=False)
			tree.column("Side 2", width=80, anchor='w', stretch=False)
			for n in range(1, self.num_Artworks + 1):
				total = counter1.get(n, 0) + counter2.get(n, 0)
				tree.insert('', 'end', values=(f"Artwork #{n}", total, counter1.get(n, 0), counter2.get(n, 0)))
		
		# Scrollbar for table
		vsb = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
		tree.configure(yscrollcommand=vsb.set)
		tree.pack(side='left', fill='both', expand=True)
		vsb.pack(side='left', fill='y')
		
		# Buttons centered under the table
		footer = tk.Frame(main_container)
		footer.pack(fill='x', pady=(12, 0))
		
		buttons_row = tk.Frame(footer)
		buttons_row.pack()
		
		export_btn = tk.Button(buttons_row, text="Export Viewer", 
							 command=self.export_viewer, 
							 font=("Arial", 12),
							 width=14, height=2, 
							 relief=tk.GROOVE, bd=2)
		export_btn.pack(side='left', padx=8)
		
		editor_btn = tk.Button(buttons_row, text="Export Sequencer", 
							 command=self.export_editor, 
							 font=("Arial", 12),
							 width=16, height=2, 
							 relief=tk.GROOVE, bd=2)
		editor_btn.pack(side='left', padx=8)
		
		save_btn = tk.Button(buttons_row, text="Save Report", 
						  command=lambda: self.save_report(), 
						  font=("Arial", 12),
						  width=12, height=2, 
						  relief=tk.GROOVE, bd=2)
		save_btn.pack(side='left', padx=8)
		
		close_btn = tk.Button(buttons_row, text="Done", 
							 command=root.destroy, 
							 font=("Arial", 12),
							 width=12, height=2, 
							 relief=tk.GROOVE, bd=2)
		close_btn.pack(side='left', padx=8)
		
		# Center the window to screen without forcing size
		root.update_idletasks()
		x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
		y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
		root.geometry(f'+{x}+{y}')
		
		root.mainloop()
	
	def save_report(self):
		"""Save a text report of the Artwork requirements"""
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		output_dir = self.get_output_dir()
		filename = f"Artwork_report_{timestamp}.txt"
		full_path = os.path.join(output_dir, filename)
		
		with open(full_path, 'w') as f:
			f.write("Artwork SEQUENCING REPORT\n")
			f.write("=" * 50 + "\n")
			f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
			f.write(f"Road Type: {'Single Way' if self.mode == 'single' else 'Two Way'}\n")
			f.write(f"Unique Artworks: {self.num_Artworks}\n")
			f.write("\n")
			
			if self.mode == "single":
				labels = [((i % self.num_Artworks) + 1) for i in range(len(self.coords_side1))]
				counter = Counter(labels)
				
				f.write(f"Total Lamp Posts: {len(self.coords_side1)}\n")
				f.write("\nArtwork Requirements:\n")
				f.write("-" * 30 + "\n")
				
				for Artwork_num in range(1, self.num_Artworks + 1):
					count = counter.get(Artwork_num, 0)
					f.write(f"Artwork #{Artwork_num}: {count} copies\n")
			else:
				labels1 = [((i % self.num_Artworks) + 1) for i in range(len(self.coords_side1))]
				labels2 = [((i % self.num_Artworks) + 1) for i in range(len(self.coords_side2))]
				counter1 = Counter(labels1)
				counter2 = Counter(labels2)
				
				f.write(f"Side 1 Lamp Posts: {len(self.coords_side1)}\n")
				f.write(f"Side 2 Lamp Posts: {len(self.coords_side2)}\n")
				f.write(f"Total Lamp Posts: {len(self.coords_side1) + len(self.coords_side2)}\n")
				f.write("\nArtwork Requirements:\n")
				f.write("-" * 50 + "\n")
				
				for Artwork_num in range(1, self.num_Artworks + 1):
					total = counter1.get(Artwork_num, 0) + counter2.get(Artwork_num, 0)
					side1_count = counter1.get(Artwork_num, 0)
					side2_count = counter2.get(Artwork_num, 0)
					f.write(f"Artwork #{Artwork_num}: {total} copies (Side 1: {side1_count}, Side 2: {side2_count})\n")
		
		messagebox.showinfo("Report Saved", f"Report saved as {full_path}")
	
	def export_viewer(self):
		# ... existing code for viewer export (omitted for brevity in this snippet)...
		pass
	
	def export_editor(self):
		"""Export an interactive HTML sequencer/editor with connected rectangle inputs."""
		if self.img is None:
			messagebox.showerror("Error", "No image loaded")
			return None
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		base_dir = os.path.join(self.get_output_dir(), f"Sequencer_{timestamp}")
		assets_dir = os.path.join(base_dir, "assets")
		icons_dir = os.path.join(assets_dir, "icons")
		os.makedirs(icons_dir, exist_ok=True)
		
		# Save road image
		road_out = os.path.join(assets_dir, "road.png")
		cv2.imwrite(road_out, self.img)
		
		# Save icon thumbs (for listing) if in picture mode
		choices = []
		if self.use_images and self.artwork_icons_full:
			for i in range(self.num_Artworks):
				out_path = os.path.join(icons_dir, f"icon_{i+1}.png")
				if i < len(self.artwork_icon_paths) and os.path.isfile(self.artwork_icon_paths[i]):
					shutil.copy2(self.artwork_icon_paths[i], out_path)
				else:
					cv2.imwrite(out_path, self.artwork_icons_full[i % len(self.artwork_icons_full)])
				choices.append({"id": i+1, "path": f"assets/icons/icon_{i+1}.png", "name": os.path.basename(self.artwork_icon_paths[i]) if i < len(self.artwork_icon_paths) else f"Artwork {i+1}"})
		
		import json
		data = {
			"image": "assets/road.png",
			"imageSize": {"width": int(self.img.shape[1]), "height": int(self.img.shape[0])},
			"mode": self.mode,
			"numArtworks": self.num_Artworks,
			"useImages": self.use_images,
			"choices": choices,
			"placements": self.placements,
		}
		data_json = json.dumps(data)
		
		index_html = """<!doctype html><html><head><meta charset=\"utf-8\"/><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/><title>Artwork Sequencer</title><style>
 html,body{height:100%;margin:0;overflow:hidden;font-family:Arial,Helvetica,sans-serif}
 #wrap{display:flex;height:100vh}
 #stage{position:relative;flex:1;background:#000;cursor:crosshair}
 #img{width:100%;height:100%;object-fit:contain;display:block}
 #markers{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}
 .marker{position:absolute;border:2px solid #000;background:#fff;width:28px;height:14px;display:flex;cursor:pointer;pointer-events:auto}
 .marker .sq{flex:1;border-right:1px solid #000;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:9px;color:#fff}
 .marker .sq:last-child{border-right:0}
 .marker .sq.side1{border-color:#0033AA;background:#0066FF}
 .marker .sq.side2{border-color:#AA0000;background:#FF3333}
 /* Keep halves colored even when active; use outline for focus */
 .marker .sq.active{outline:2px solid #ffffff; outline-offset:-2px}
 #overlay{position:absolute;display:none;border:2px solid #000;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.2);padding:4px}
 #overlay .row{display:flex;gap:6px}
 #overlay input{width:40px;text-align:center}
 #side{width:340px;border-left:1px solid #ddd;padding:10px;box-sizing:border-box;display:flex;flex-direction:column}
 #side h3{margin:4px 0 10px}
 #choices{flex:1;overflow:auto;border:1px solid #eee}
 .choice{display:flex;align-items:center;gap:8px;padding:6px 8px;border-bottom:1px solid #f1f1f1;cursor:pointer}
 .choice:hover{background:#f5f5f5}
 .choice img{width:36px;height:36px;object-fit:contain;border:1px solid #ddd}
 #preview{border-top:1px solid #ddd;padding-top:8px}
 #preview img{max-width:100%;max-height:30vh;object-fit:contain;border:1px solid #ccc}
 #info{font-size:12px;color:#666;margin-bottom:8px}
 #btns{display:flex;gap:8px;margin-top:8px}
 button{cursor:pointer}
 </style></head><body><div id=\"wrap\"><div id=\"stage\"><img id=\"img\"><div id=\"markers\"></div><div id=\"overlay\"></div></div><div id=\"side\"><h3>Sequencer</h3><div id=\"info\"></div><div id=\"choices\"></div><div id=\"preview\"><img id=\"prevImg\"></div><div id=\"btns\"><button id=\"download\">Download placements.json</button><button id=\"final\">Download final.png</button><button id=\"finish\">Finish</button></div></div></div><script>
 const DATA=__DATA__;
 const img=document.getElementById('img');
 const markers=document.getElementById('markers');
 const overlay=document.getElementById('overlay');
 const info=document.getElementById('info');
 const choicesBox=document.getElementById('choices');
 const prevImg=document.getElementById('prevImg');
 img.src=DATA.image;
 let natW=DATA.imageSize.width, natH=DATA.imageSize.height;
 let placements=Array.isArray(DATA.placements)?DATA.placements:[];
 let activeP=null; let activeSide=1;
 let isDragging=false, dragMoved=false, dragStartX=0, dragStartY=0, pStartX=0, pStartY=0;
 const markerW=28, markerH=14;
 info.textContent = (DATA.mode==='two'?'Two Way':'Single Way')+' — '+(DATA.useImages?'Picture mode':'Numbers mode');
 function px(x){return (x/natW)*img.clientWidth}
 function py(y){return (y/natH)*img.clientHeight}
 function nearestPlacement(x,y){let best=null,bestD=12;for(const p of placements){const d=Math.hypot(px(p.x)-px(x),py(p.y)-py(y));if(d<bestD){best=p;bestD=d;}}return best;}
 function ensurePlacement(x,y){let p=nearestPlacement(x,y);if(!p){p={x,y,s1_num:null,s2_num:null,s1_icon:null,s2_icon:null};placements.push(p);}return p;}
 function selectPlacement(p){activeP=p; activeSide=1; redraw(); if(DATA.useImages) buildChoices();}
 function selectSide(side){activeSide=side; redraw();}
 function redraw(){markers.innerHTML='';for(const p of placements){const m=document.createElement('div');m.className='marker';m.style.left=(px(p.x)-markerW/2)+'px';m.style.top=(py(p.y)-markerH/2)+'px';const s1=document.createElement('div');s1.className='sq side1'+(activeP===p&&activeSide===1?' active':'');s1.textContent=(p.s1_num||p.s1_icon||'');const s2=document.createElement('div');s2.className='sq side2'+(activeP===p&&activeSide===2?' active':'');if(DATA.mode==='two'){s2.textContent=(p.s2_num||p.s2_icon||'');}m.appendChild(s1); if(DATA.mode==='two') m.appendChild(s2);
  // Dragging support on whole rectangle
  m.onmousedown=(e)=>{e.preventDefault(); isDragging=true; dragMoved=false; dragStartX=e.clientX; dragStartY=e.clientY; pStartX=p.x; pStartY=p.y; selectPlacement(p); const onMove=(ev)=>{if(!isDragging) return; const dx=ev.clientX-dragStartX; const dy=ev.clientY-dragStartY; if(Math.abs(dx)>2||Math.abs(dy)>2) dragMoved=true; const dxImg=dx*natW/img.clientWidth; const dyImg=dy*natH/img.clientHeight; p.x=Math.max(0,Math.min(natW, Math.round(pStartX+dxImg))); p.y=Math.max(0,Math.min(natH, Math.round(pStartY+dyImg))); redraw();}; const onUp=(ev)=>{window.removeEventListener('mousemove',onMove); window.removeEventListener('mouseup',onUp); isDragging=false;}; window.addEventListener('mousemove',onMove); window.addEventListener('mouseup',onUp); };
  // Click handlers per half for precise editing
  s1.onclick=(e)=>{e.stopPropagation(); if(dragMoved) return; selectPlacement(p); selectSide(1); if(!DATA.useImages) openInlineEditor(p,1,m); else buildChoices();};
  if(DATA.mode==='two'){ s2.onclick=(e)=>{e.stopPropagation(); if(dragMoved) return; selectPlacement(p); selectSide(2); if(!DATA.useImages) openInlineEditor(p,2,m); else buildChoices();}; }
  s1.onmouseenter=()=>hoverPreview(p,1); if(DATA.mode==='two') s2.onmouseenter=()=>hoverPreview(p,2);
  s1.onmouseleave=()=>hoverPreview(null,0); if(DATA.mode==='two') s2.onmouseleave=()=>hoverPreview(null,0);
  markers.appendChild(m);} }
 function hoverPreview(p,side){if(!p||!DATA.useImages){prevImg.removeAttribute('src');return;}const id=(side===1?p.s1_icon:p.s2_icon);if(!id){prevImg.removeAttribute('src');return;}const ch=DATA.choices.find(c=>c.id===id);if(ch) prevImg.src=ch.path;}
 function openInlineEditor(p,side,markerEl){if(DATA.useImages) return; // numbers only
 const rect=markerEl.getBoundingClientRect();overlay.style.display='block';overlay.innerHTML='';const row=document.createElement('div');row.className='row';if(DATA.mode==='single'){const i=document.createElement('input');i.value=p.s1_num||'';i.onkeydown=(e)=>{if(e.key==='Enter'){p.s1_num=parseInt(i.value)||null;overlay.style.display='none';redraw();}};row.appendChild(i); setTimeout(()=>i.focus(),0);} else {const i1=document.createElement('input');const i2=document.createElement('input');i1.value=p.s1_num||'';i2.value=p.s2_num||'';const commit=()=>{p.s1_num=parseInt(i1.value)||null;p.s2_num=parseInt(i2.value)||null;overlay.style.display='none';redraw();};i1.onkeydown=(e)=>{if(e.key==='Enter') commit();};i2.onkeydown=(e)=>{if(e.key==='Enter') commit();};row.appendChild(i1);row.appendChild(i2); setTimeout(()=>{(side===1?i1:i2).focus()},0);}overlay.appendChild(row);const farRight=(rect.left<window.innerWidth/2);overlay.style.left=(rect.left+(farRight?rect.width+8:-overlay.clientWidth-8))+'px';overlay.style.top=(rect.top+rect.height/2-overlay.clientHeight/2)+'px';}
 function buildChoices(){choicesBox.innerHTML='';if(!DATA.useImages){choicesBox.innerHTML='<div style=\"padding:6px;color:#666\">Numbers mode: click a box to edit.</div>';return;}for(const c of DATA.choices){const row=document.createElement('div');row.className='choice';const im=document.createElement('img');im.src=c.path;const lab=document.createElement('div');lab.textContent=c.id+' - '+c.name;row.appendChild(im);row.appendChild(lab);row.onclick=()=>{if(!activeP) return; if(activeSide===1){activeP.s1_icon=c.id;} else {activeP.s2_icon=c.id;} redraw();};choicesBox.appendChild(row);} }
 img.addEventListener('click',(e)=>{const r=img.getBoundingClientRect();const rx=(e.clientX-r.left)/r.width;const ry=(e.clientY-r.top)/r.height;const x=Math.round(rx*natW);const y=Math.round(ry*natH);const p=ensurePlacement(x,y);selectPlacement(p);});
 window.addEventListener('resize',()=>redraw());
 document.getElementById('download').onclick=()=>{const blob=new Blob([JSON.stringify({mode:DATA.mode,numArtworks:DATA.numArtworks,useImages:DATA.useImages,placements})],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='placements.json';a.click();};
 document.getElementById('final').onclick=()=>{const c=document.createElement('canvas');c.width=natW; c.height=natH; const ctx=c.getContext('2d');const imgEl=new Image();imgEl.onload=()=>{ctx.drawImage(imgEl,0,0,natW,natH);const boxW=Math.max(16,Math.round(Math.min(natW,natH)*0.015));const boxH=boxW;for(const p of placements){const x=p.x, y=p.y;if(DATA.mode==='single'){drawBox(ctx,x,y,boxW,boxH,'#0000FF',String(p.s1_num||p.s1_icon||''));}else{const half=Math.floor(boxW/2);drawBox(ctx,x-half,y,boxW,boxH,'#0000FF',String(p.s1_num||p.s1_icon||''));drawBox(ctx,x+half,y,boxW,boxH,'#FF0000',String(p.s2_num||p.s2_icon||''));}}const link=document.createElement('a');link.href=c.toDataURL('image/png');link.download='final.png';link.click();};imgEl.src=DATA.image;};
 document.getElementById('finish').onclick=()=>{window.close();};
 function drawBox(ctx,cx,cy,w,h,color,text){const x=cx-Math.round(w/2), y=cy-Math.round(h/2);ctx.strokeStyle=color;ctx.lineWidth=2;ctx.strokeRect(x,y,w,h);ctx.font='bold 12px Arial';ctx.fillStyle=color;ctx.fillText(text,x+3,y+h-4);}
 img.onload=()=>{redraw(); buildChoices();};
 </script></body></html>"""
		index_html = index_html.replace("__DATA__", data_json)
		os.makedirs(base_dir, exist_ok=True)
		index_path = os.path.join(base_dir, "index.html")
		with open(index_path, "w") as f:
			f.write(index_html)
		messagebox.showinfo("Sequencer Exported", f"Interactive sequencer exported to\n{base_dir}\nOpen index.html in a browser.")
		return index_path

if __name__ == "__main__":
	sequencer = ArtworkSequencer()
	sequencer.setup_gui()
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

class MetadataCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Metadata Cleaner")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Configure style
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('Title.TLabel', font=('Arial', 12, 'bold'))

        # Source folders
        self.source_folders = []

        # Create main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create all GUI elements once
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="Photo Metadata Cleaner",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Source Folders Section
        source_frame = ttk.LabelFrame(
            self.main_frame,
            text="Source Folders",
            padding="10"
        )
        source_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.source_listbox = tk.Listbox(
            source_frame,
            height=8,
            selectmode=tk.MULTIPLE,
            font=('Arial', 9)
        )
        self.source_listbox.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(source_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        add_button = ttk.Button(
            button_frame,
            text="Add Folder",
            command=self.add_source_folder
        )
        add_button.pack(side=tk.LEFT, padx=2)

        remove_button = ttk.Button(
            button_frame,
            text="Remove Selected",
            command=self.remove_selected_sources
        )
        remove_button.pack(side=tk.LEFT, padx=2)

        # Destination Folder Section
        dest_frame = ttk.LabelFrame(
            self.main_frame,
            text="Destination Folder",
            padding="10"
        )
        dest_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(
            dest_frame,
            textvariable=self.dest_var,
            state='readonly',
            font=('Arial', 9)
        )
        dest_entry.pack(fill=tk.X, expand=True)

        dest_button = ttk.Button(
            dest_frame,
            text="Select Destination",
            command=self.select_destination
        )
        dest_button.pack(pady=(5, 0))

        # Process Section
        process_frame = ttk.Frame(self.main_frame)
        process_frame.grid(row=3, column=0, pady=10)

        self.process_button = ttk.Button(
            process_frame,
            text="Clean and Move Photos",
            command=self.process_images,
            style='TButton'
        )
        self.process_button.pack()

        # Status Section
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=4, column=0, sticky="ew")

        self.status_var = tk.StringVar(value="Ready to clean photos")
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5
        )
        status_label.pack(fill=tk.X)

        # Progress Bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress.grid(row=5, column=0, sticky="ew", pady=(5, 0))

    def add_source_folder(self):
        folder = filedialog.askdirectory(
            mustexist=True,
            title="Select Folder"
        )
        if folder and folder not in self.source_folders:
            self.source_folders.append(folder)
            self.source_listbox.insert(tk.END, folder)

    def remove_selected_sources(self):
        selected = self.source_listbox.curselection()
        for index in reversed(selected):
            self.source_folders.pop(index)
            self.source_listbox.delete(index)

    def select_destination(self):
        folder = filedialog.askdirectory(
            mustexist=True,
            title="Select Destination Folder"
        )
        if folder:
            self.dest_var.set(folder)

    def process_images(self):
        if not self.source_folders:
            messagebox.showerror("Error", "Please select at least one source folder")
            return

        dest_folder = self.dest_var.get()
        if not dest_folder:
            messagebox.showerror("Error", "Please select a destination folder")
            return

        supported_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif')
        total_files = 0

        for source_folder in self.source_folders:
            for root, _, files in os.walk(source_folder):
                for filename in files:
                    if filename.lower().endswith(supported_extensions):
                        total_files += 1

        if total_files == 0:
            messagebox.showinfo("Info", "No image files found in the selected folders")
            return

        self.process_button.config(state=tk.DISABLED)
        self.progress['maximum'] = total_files
        processed_files = 0
        errors = 0

        os.makedirs(dest_folder, exist_ok=True)

        for source_folder in self.source_folders:
            for root, _, files in os.walk(source_folder):
                for filename in files:
                    if filename.lower().endswith(supported_extensions):
                        file_path = os.path.join(root, filename)

                        try:
                            with Image.open(file_path) as img:
                                # Remove metadata
                                if img.format == 'PNG':
                                    new_img = Image.new(img.mode, img.size)
                                    new_img.putdata(list(img.getdata()))
                                    save_kwargs = {}
                                elif img.format == 'JPEG':
                                    new_img = img.copy()
                                    save_kwargs = {'quality': 95}
                                    if 'exif' in img.info:
                                        save_kwargs['exif'] = b""
                                else:
                                    new_img = img.copy()
                                    save_kwargs = {}

                                # Destination path
                                rel_path = os.path.relpath(root, source_folder)
                                dest_subfolder = os.path.join(dest_folder, rel_path)
                                os.makedirs(dest_subfolder, exist_ok=True)
                                new_filepath = os.path.join(dest_subfolder, filename)

                                try:
                                    new_img.save(new_filepath, **save_kwargs)
                                except Exception as save_err:
                                    errors += 1
                                    print(f"Failed to save {filename}: {save_err}")
                                    continue

                                processed_files += 1
                                self.progress['value'] = processed_files

                                # Only update UI occasionally
                                if processed_files % 10 == 0 or processed_files == total_files:
                                    self.status_var.set(
                                        f"Processing: {processed_files}/{total_files} files | "
                                        f"Errors: {errors} | Current: {filename[:25]}"
                                    )
                                    self.root.update_idletasks()

                        except Exception as e:
                            errors += 1
                            print(f"Error processing {filename}: {str(e)}")

        messagebox.showinfo(
            "Complete",
            f"Processing complete!\n\n"
            f"Total images processed: {processed_files}\n"
            f"Errors encountered: {errors}"
        )
        self.status_var.set("Ready to clean photos")
        self.progress['value'] = 0
        self.process_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = MetadataCleanerApp(root)
    root.mainloop()

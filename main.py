import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# --- State ---
imported_files = []
output_dir = ""
photo_ref = None
aspect_ratio = 1.0
lock_active = False
_updating = False

def process_file(input_path, output_path, out_w, out_h):
    try:
        img = Image.open(input_path).convert("RGBA")
        resized = img.resize((out_w, out_h), Image.NEAREST)
        resized.save(output_path, "PNG")
        return True
    except Exception:
        return False

def update_viewport(img):
    global photo_ref
    root.update_idletasks()
    vw = max(viewport.winfo_width(), 10)
    vh = max(viewport.winfo_height(), 10)
    w, h = img.size
    scale = min(vw / w, vh / h)
    display_w = max(1, int(w * scale))
    display_h = max(1, int(h * scale))
    thumb = img.resize((display_w, display_h), Image.NEAREST)
    photo_ref = ImageTk.PhotoImage(thumb)
    viewport.delete("all")
    viewport.create_image(vw // 2, vh // 2, anchor="center", image=photo_ref)
    if len(imported_files) > 1:
        viewport.create_text(
            vw - 6, vh - 6, anchor="se",
            text=f"+{len(imported_files) - 1} more",
            fill="#aaaaaa", font=("Arial", 9),
        )

def on_import():
    global imported_files, aspect_ratio
    files = filedialog.askopenfilenames(
        title="Select Image(s)",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
    )
    if not files:
        return
    imported_files = list(files)
    try:
        img = Image.open(imported_files[0])
        w, h = img.size
        aspect_ratio = w / h if h else 1.0
        res_var.set(f"Current Resolution:  {w} x {h}")
        update_viewport(img)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open image:\n{e}")

def toggle_lock():
    global lock_active, aspect_ratio
    lock_active = not lock_active
    if lock_active:
        try:
            w = int(var_width.get())
            h = int(var_height.get())
            if w > 0 and h > 0:
                aspect_ratio = w / h
        except ValueError:
            pass
        lock_btn.config(text="Unlock", relief=tk.SUNKEN, bg="#4a90d9", fg="white")
    else:
        lock_btn.config(text="Lock", relief=tk.RAISED, bg=default_btn_bg, fg=default_btn_fg)

def on_width_trace(*_):
    global _updating
    if _updating or not lock_active:
        return
    try:
        w = int(var_width.get())
        if w > 0:
            _updating = True
            var_height.set(str(round(w / aspect_ratio)))
            _updating = False
    except (ValueError, ZeroDivisionError):
        _updating = False

def on_height_trace(*_):
    global _updating
    if _updating or not lock_active:
        return
    try:
        h = int(var_height.get())
        if h > 0:
            _updating = True
            var_width.set(str(round(h * aspect_ratio)))
            _updating = False
    except (ValueError, ZeroDivisionError):
        _updating = False

def on_set_output():
    global output_dir
    folder = filedialog.askdirectory(title="Select Export Destination")
    if folder:
        output_dir = folder
        out_dir_var.set(f"{output_dir}")

def on_convert():
    if not imported_files:
        messagebox.showwarning("Warning", "Import image(s) first.")
        return
    if not output_dir:
        messagebox.showwarning("Warning", "Set an output directory first.")
        return
    try:
        out_w = int(var_width.get())
        out_h = int(var_height.get())
        if out_w <= 0 or out_h <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Warning", "Enter a valid width and height.")
        return

    count = 0
    for path in imported_files:
        stem = os.path.splitext(os.path.basename(path))[0]
        out_path = os.path.join(output_dir, f"{stem}_{out_w}x{out_h}.png")
        if process_file(path, out_path, out_w, out_h):
            count += 1

    messagebox.showinfo("Done", f"Converted {count} of {len(imported_files)} file(s).")

# --- GUI ---
root = tk.Tk()
root.title("Skin Conversion Tool")
root.geometry("520x560")
root.minsize(420, 480)

# Capture default button colors after root exists
_tmp_btn = tk.Button(root)
default_btn_bg = _tmp_btn.cget("bg")
default_btn_fg = _tmp_btn.cget("fg")
_tmp_btn.destroy()

# Top bar: Import button
top_bar = tk.Frame(root, padx=10, pady=6)
top_bar.pack(fill=tk.X)

tk.Button(top_bar, text="Import", width=10, command=on_import).pack(side=tk.LEFT)
tk.Button(top_bar, text="Output", width=10, command=on_set_output).pack(side=tk.LEFT, padx=(6, 0))

out_dir_var = tk.StringVar(value="No output directory set")
tk.Label(top_bar, textvariable=out_dir_var, anchor="w", fg="#555555").pack(side=tk.LEFT, padx=(10, 0))

# Viewport
vp_frame = tk.Frame(root, padx=10)
vp_frame.pack(fill=tk.BOTH, expand=True)

viewport = tk.Canvas(vp_frame, bg="#1a1a1a", highlightthickness=1, highlightbackground="#555555")
viewport.pack(fill=tk.BOTH, expand=True)

# Current resolution
res_var = tk.StringVar(value="Current Resolution:  —")
tk.Label(root, textvariable=res_var, anchor="w", padx=12, pady=4).pack(fill=tk.X)

# Separator
tk.Frame(root, height=1, bg="#cccccc").pack(fill=tk.X, padx=10)

# Output resolution controls
ctrl_frame = tk.Frame(root, padx=10, pady=8)
ctrl_frame.pack(fill=tk.X)

tk.Label(ctrl_frame, text="Output Resolution:").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 6))

tk.Label(ctrl_frame, text="W:").grid(row=1, column=0, sticky="e")
var_width = tk.StringVar(value="2048")
tk.Entry(ctrl_frame, textvariable=var_width, width=8).grid(row=1, column=1, padx=(2, 8))

lock_btn = tk.Button(ctrl_frame, text="Lock", width=9, command=toggle_lock)
lock_btn.grid(row=1, column=2, padx=4)

tk.Label(ctrl_frame, text="H:").grid(row=1, column=3, sticky="e")
var_height = tk.StringVar(value="2048")
tk.Entry(ctrl_frame, textvariable=var_height, width=8).grid(row=1, column=4, padx=(2, 0))

var_width.trace_add("write", on_width_trace)
var_height.trace_add("write", on_height_trace)

# Convert button
tk.Button(root, text="Convert", height=2, command=on_convert).pack(fill=tk.X, padx=10, pady=(4, 10))

root.mainloop()
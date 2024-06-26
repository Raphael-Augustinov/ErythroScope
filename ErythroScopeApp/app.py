import os
import shutil
import cv2
import numpy as np
import threading
from tkinter import filedialog, messagebox, Canvas
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps
from tkinterdnd2 import TkinterDnD, DND_FILES

# Set the appearance mode to light
ctk.set_appearance_mode("light")

# Initialize the customtkinter application with TkinterDnD for drag-and-drop
app = TkinterDnD.Tk()

# Set the window title
app.title("ErythroScope")

# Set the window size
app.geometry("750x780")

# Prevent the window from being resizable
app.resizable(False, False)

# Add a simple label to the window
label = ctk.CTkLabel(app, text="Upload or drag & drop images", font=("Inter", 20))
label.place(x=78, y=34)

# Create the "images" directory if it doesn't exist
images_dir = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(images_dir, exist_ok=True)

# List to store the placeholders
placeholders = []
uploaded_filenames = []  # Track uploaded filenames
filename_labels = []  # Track filename labels
current_placeholder_index = 0  # Track the next available placeholder index

# Maximum number of images that can be uploaded
MAX_IMAGES = 6

# Allowed file types
ALLOWED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp')

# Coordinates for placeholders
placeholder_coordinates = [(78, 86), (300, 86), (522, 86), (78, 259), (300, 259), (522, 259)]


def load_model():
    # Path to your model and config file
    model_weights_path = "./model_v3/model_final.pth"
    config_path = "./model_v3/config.yaml"

    # Load the configuration file
    cfg = get_cfg()
    cfg.merge_from_file(config_path)
    cfg.MODEL.WEIGHTS = model_weights_path
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
    cfg.MODEL.DEVICE = "cpu"  # Use CPU

    # Initialize the predictor
    predictor = DefaultPredictor(cfg)
    return predictor


def analyze_image(predictor, image_path):
    image = cv2.imread(image_path)
    outputs = predictor(image)
    pred_classes = outputs["instances"].pred_classes.to("cpu").numpy()
    return pred_classes


def create_image_placeholder(x_image, y_image):
    placeholder_frame = ctk.CTkFrame(
        app,
        width=140,
        height=140,
        corner_radius=8,
        fg_color="lightgray"  # Set the background color to light gray
    )
    placeholder_frame.place(x=x_image, y=y_image)
    placeholders.append(placeholder_frame)
    return placeholder_frame


def clear_images():
    global current_placeholder_index
    for placeholder in placeholders:
        # Clear the content in the placeholder
        for widget in placeholder.winfo_children():
            widget.destroy()
        placeholder.configure(fg_color="lightgray")  # Reset to placeholder color
    current_placeholder_index = 0  # Reset the index
    uploaded_filenames.clear()  # Clear the filenames list

    # Clear the filename labels
    for filename_label in filename_labels:
        filename_label.destroy()
    filename_labels.clear()

    # Clear the list of images under the "Analyze images" button
    for widget in app.winfo_children():
        if isinstance(widget, ctk.CTkLabel) and widget.winfo_y() >= 490:
            widget.destroy()
        if hasattr(widget, 'is_line_widget') and widget.is_line_widget:
            widget.destroy()

    # Clear the images directory without deleting it
    for filename in os.listdir(images_dir):
        file_path = os.path.join(images_dir, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)


def show_confirmation_dialog():
    result = messagebox.askquestion("Deleting uploaded images", "Are you sure you want to delete all uploaded images?",
                                    icon='warning')
    if result == 'yes':
        clear_images()


def select_files():
    if len(uploaded_filenames) >= MAX_IMAGES:
        messagebox.showinfo("Limit Exceeded", "You have already uploaded the maximum number of images (6).")
        return

    filetypes = [
        ("Image files", "*.png *.jpg *.jpeg *.bmp"),
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg *.jpeg"),
        ("Bitmap files", "*.bmp")
    ]
    filenames = filedialog.askopenfilenames(title="Select files", filetypes=filetypes)

    if filenames:
        handle_files(filenames)


def handle_files(filenames):
    new_filenames = []
    for filename in filenames:
        if not filename.lower().endswith(ALLOWED_EXTENSIONS):
            messagebox.showinfo("Invalid File Type",
                                f"The file {os.path.basename(filename)} is not a supported image file.")
            continue
        if os.path.basename(filename) in uploaded_filenames:
            messagebox.showinfo("Duplicate File", f"The file {os.path.basename(filename)} has already been uploaded.")
            continue
        new_filenames.append(filename)

    total_images_after_upload = len(uploaded_filenames) + len(new_filenames)
    if total_images_after_upload > MAX_IMAGES:
        allowed_files = MAX_IMAGES - len(uploaded_filenames)
        new_filenames = new_filenames[:allowed_files]
        messagebox.showinfo("Limit Exceeded",
                            f"You can only upload {allowed_files} more images. Only the first {allowed_files} images have been uploaded.")

    if new_filenames:
        print("Selected files:", new_filenames)
        for filename in new_filenames:
            dest_path = os.path.join(images_dir, os.path.basename(filename))
            shutil.copy2(filename, dest_path)  # Copy the file to the images directory
        display_images(new_filenames)


def display_images(filenames):
    global current_placeholder_index
    for filename in filenames:
        if current_placeholder_index >= len(placeholders):
            break
        # Open the image and resize it to fit the placeholder
        img = Image.open(filename)
        img = img.resize((140, 140), Image.LANCZOS)

        # Create a mask for rounded corners
        mask = Image.new('L', (140, 140), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((0, 0, 140, 140), radius=8, fill=255)
        img = ImageOps.fit(img, (140, 140))
        img.putalpha(mask)

        # Convert the image to CTkImage with correct size
        img_tk = ctk.CTkImage(light_image=img, size=(140, 140))

        # Clear previous content in placeholder
        for widget in placeholders[current_placeholder_index].winfo_children():
            widget.destroy()

        # Create a label to display the image
        image_label = ctk.CTkLabel(placeholders[current_placeholder_index], image=img_tk, text="")
        image_label.image = img_tk  # Keep a reference to avoid garbage collection
        image_label.pack(expand=True)

        # Display the filename under the image
        image_x, image_y = placeholder_coordinates[current_placeholder_index]
        filename_label = ctk.CTkLabel(app, text=os.path.basename(filename), font=("Inter", 12), text_color="black")
        filename_label.place(x=image_x + 12, y=image_y + 142)
        filename_labels.append(filename_label)

        # Store the filename
        uploaded_filenames.append(os.path.basename(filename))  # Store just the file name

        # Increment the placeholder index
        current_placeholder_index += 1

    # Print the list of uploaded filenames
    print("Uploaded filenames:", uploaded_filenames)


def display_uploaded_images():
    y_position = 490
    for i, filename in enumerate(uploaded_filenames):
        image_label = ctk.CTkLabel(app, text=f"Image {i + 1}: {filename}", font=("Inter", 12), text_color="black")
        image_label.place(x=78, y=y_position)
        y_position += 25


def on_drop(event):
    if len(uploaded_filenames) >= MAX_IMAGES:
        messagebox.showinfo("Limit Exceeded", "You have already uploaded the maximum number of images (6).")
        return

    # Get the dropped files
    dropped_files = app.tk.splitlist(event.data)

    # Check file types
    valid_files = []
    for file in dropped_files:
        if not file.lower().endswith(ALLOWED_EXTENSIONS):
            messagebox.showinfo("Invalid File Type",
                                f"The file {os.path.basename(file)} is not a supported image file.")
        else:
            valid_files.append(file)

    if valid_files:
        handle_files(valid_files)


# Add a button to select files
button = ctk.CTkButton(
    app,
    text="Select files",
    font=("Inter", 14),
    width=140,
    height=31,
    corner_radius=8,
    fg_color="black",  # Background color
    text_color="white",  # Text color
    hover_color="#333333",
    command=select_files
)
button.place(x=522, y=31)


def display_result(result, list_of_categories_and_numbers):
    tick_image = Image.open(r'C:\Users\rapha\PycharmProjects\testapp\assets\icons8-tick-50.png')
    tick_image = tick_image.resize((30, 30), Image.LANCZOS)  # Resize if necessary

    # Convert the image to CTkImage
    tick_image_ctk = ctk.CTkImage(light_image=tick_image, size=(30, 30))

    # Create a label to display the tick icon
    tick_label = ctk.CTkLabel(app, image=tick_image_ctk, text="")
    tick_label.place(x=320, y=688)

    label1 = ctk.CTkLabel(app, text="Result:", font=("Inter", 20))
    label1.place(x=358, y=689)

    label2 = ctk.CTkLabel(app, text=result, font=("Inter", 20))
    label2.place(x=267, y=725)

    title = ctk.CTkLabel(app, text="Title", font=("Inter", 14), text_color="#5F5F5F")
    title.place(x=100, y=502)
    number = ctk.CTkLabel(app, text="Number", font=("Inter", 14), text_color="#5F5F5F")
    number.place(x=278, y=502)

    title1 = ctk.CTkLabel(app, text="Title", font=("Inter", 14), text_color="#5F5F5F")
    title1.place(x=420, y=502)
    number1 = ctk.CTkLabel(app, text="Number", font=("Inter", 14), text_color="#5F5F5F")
    number1.place(x=598, y=502)

    canvas = Canvas(app, width=256, height=1, bg="#C5C5C5")
    canvas.is_line_widget = True
    canvas.place(x=90, y=526)

    canvas1 = Canvas(app, width=256, height=1, bg="#C5C5C5")
    canvas1.is_line_widget = True
    canvas1.place(x=410, y=526)

    start_y = 502
    addition_x = 0
    count = 0
    for cell in list_of_categories_and_numbers:
        cell_name, cell_number = cell
        if count == 3:
            start_y = 502
            addition_x = 320
        cell_name_label = ctk.CTkLabel(app, text=cell_name, font=("Inter", 14), text_color="black")
        cell_name_label.place(x=100 + addition_x, y=start_y + 44)
        cell_number_label = ctk.CTkLabel(app, text=cell_number, font=("Inter", 14), text_color="black")
        cell_number_label.place(x=278 + addition_x, y=start_y + 44)
        canvas = Canvas(app, width=256, height=1, bg="#C5C5C5", highlightthickness=0)
        canvas.is_line_widget = True
        canvas.place(x=90 + addition_x, y=start_y + 70)
        start_y += 44
        count += 1



def analyze_images_thread():
    # Add loading icon
    loading_label = ctk.CTkLabel(app, text="Analyzing...", font=("Inter", 14))
    loading_label.place(x=338, y=561)

    # Call the analysis function
    predictor = load_model()

    class_counts = {}
    total_cells = 0  # Total number of cells detected

    for filename in uploaded_filenames:
        image_path = os.path.join(images_dir, filename)
        pred_classes = analyze_image(predictor, image_path)

        unique, counts = np.unique(pred_classes, return_counts=True)
        total_cells += sum(counts)  # Update the total number of cells detected

        for class_id, count in zip(unique, counts):
            if class_id in class_counts:
                class_counts[class_id] += count
            else:
                class_counts[class_id] = count

    class_names = ["ovalocytes", "codocytes", "normal cells", "dacriocyte", "schistocyte", "anulocyte"]

    list_of_tuples = [(class_names[i], str(class_counts.get(i, 0))) for i in range(len(class_names))]

    # Determine result text based on the number of normal cells
    normal_cells_count = class_counts.get(2, 0)  # Assuming class 0 is "Normal cells"
    if total_cells == 0:
        result_text = "No cells detected, try again!"
    elif (normal_cells_count / total_cells) < 0.8:
        result_text = "Iron deficiency anemia!"
    else:
        result_text = "No anemia detected!"

    display_result(result_text, list_of_tuples)

    # Remove loading icon
    loading_label.destroy()

def analyze_images():
    # Run the analysis in a separate thread
    threading.Thread(target=analyze_images_thread).start()


# Add the "Analyze images" button
button2 = ctk.CTkButton(
    app,
    text="Analyze images",
    font=("Inter", 14),
    width=181,
    height=31,
    corner_radius=8,
    fg_color="black",  # Background color
    text_color="white",  # Text color
    hover_color="#333333",
    command=analyze_images
)
button2.place(x=78, y=433)

# Add the "Clear" button to clear images
button3 = ctk.CTkButton(
    app,
    text="Clear",
    font=("Inter", 14),
    width=181,
    height=31,
    corner_radius=8,
    fg_color="#c0c0c0",  # Background color
    text_color="black",  # Text color
    hover_color="#a7a7a7",
    command=show_confirmation_dialog
)
button3.place(x=481, y=433)

# Create image placeholders using predefined coordinates
for x, y in placeholder_coordinates:
    create_image_placeholder(x, y)

# list_of_tuples = [("Normal cells", "589"), ("Ovalocytes", "167"), ("Target cells", "89")]
# display_result("Iron deficiency anemia", list_of_tuples)

# Bind the drop event
app.drop_target_register(DND_FILES)
app.dnd_bind('<<Drop>>', on_drop)


def on_closing():
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)
    app.destroy()


app.protocol("WM_DELETE_WINDOW", on_closing)

# Run the application
app.mainloop()

import json
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import customtkinter as ctk

import numpy as np
import os
import threading

from stl import mesh
from functools import partial

from Controller.Gen.noisethingy import *
from Controller.Gen.noise_mesh_gen import *
from Controller.ObGen.PlaceObjects import *
splash_root = ctk.CTk()
splash_root.geometry("300x200")
splash_root.overrideredirect(True)

    # FRAME FOR TITLE LABEL
frame_splash = ctk.CTkFrame(splash_root, fg_color="#62a5d9")
frame_splash.grid(row=0, column=0, columnspan=6, padx=10, pady=(10, 20), sticky="ew")
frame_splash.columnconfigure(0, weight=1)

    # TITLE LABEL
splash_label = ctk.CTkLabel(
    frame_splash,
    text="MeshScape is Loading",
    font=ctk.CTkFont(size=18, weight="bold"),
    text_color="white",
)
splash_label.grid(row=0, column=0, pady=(10, 10))
# splash_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

# MAIN WINDOW
root = ctk.CTk()
root.title("MeshScape")
root.geometry("1366x768")
ctk.set_appearance_mode("light")
root.columnconfigure(0, weight=1)

def main_window():

    def add_objects_to_mesh(): 

        num_rocks = int(rocks_slider.get())
        points_per_rock = int(rocks_point_slider.get())
        rock_scale_min = float(rocks_min_slider.get() / 100)
        rock_scale_max = float(rocks_max_slider.get() / 100)
        
        num_trees = int(trees_slider.get())
        tree_scale = float(trees_scale_slider.get() / 100)

        num_mushrooms = int(mushroom_slider.get())
        mushroom_scale = float(mushroom_scale_slider.get() / 100)

        num_anthills = int(volcano_slider.get())
        anthill_scale = float(volcano_scale_slider.get() / 100)

        num_sticks = int(sticks_slider.get())
        stick_scale = float(sticks_scale_slider.get() / 100)
        
        num_bushes = int(bushes_slider.get())
        bushes_scale = float(bushes_scale_slider.get() / 50)

        if (add_trees_switch.get() == "off"):
            num_trees = 0
        if (add_rocks_switch.get() == "off"):
            num_rocks = 0
        if (add_sticks_switch.get() == "off"):
            num_sticks = 0
        if (add_bushes_switch.get() == "off"):
            num_bushes = 0
        if (add_volcano_switch.get() == "off"):
            num_anthills = 0
        if (add_mushroom_switch.get() == "off"):
            num_mushrooms = 0

        combined_mesh = place_objects_on_terrain('exported_mesh.stl', num_rocks, points_per_rock, 
                                                rock_scale_min, rock_scale_max, num_trees, 
                                                tree_scale, num_mushrooms, mushroom_scale, 
                                                num_anthills, anthill_scale, num_sticks, 
                                                stick_scale, num_bushes, bushes_scale)
        
        root.after(0, save_combined_mesh, combined_mesh)

    def generate_noise():
        def run_long_task():
            try:
                progress_bar.set(0)

                noise_image_location = export_image(
                    int(width_slider.get()),
                    int(height_slider.get()),
                    int(scale_slider.get()),
                    int(octaves_slider.get()),
                    int(persistence_slider.get()),
                    int(lacunarity_slider.get()),
                    np.random.randint(0, 100),
                    noise_type_dropdown.get(),
                )
                
                progress_bar.set(0.3)
                generate_mesh_noise(
                    int(resolution_factor_slider.get()),
                    float(base_elevation_slider.get()/200),
                    float((max_height_slider.get()-min_height_slider.get())/200),
                    float(min_height_slider.get()/200),
                    noise_image_location
                )
                progress_bar.set(0.6)
                
                root.after(50, add_objects_to_mesh)
                progress_bar.set(0.8)

                root.after(50, run_visualization)

                progress_bar.set(1.0)
                root.after(50, partial(show_completion_message))

            except Exception as e:
                root.after(0, messagebox.showerror, "Error", f"An error occurred: {str(e)}")
                root.after(1000, lambda: progress_bar.set(0))

        threading.Thread(target=run_long_task).start()

    def show_completion_message():
        messagebox.showinfo("Success", "Mesh creation is complete!")
        root.after(0, lambda: progress_bar.set(0))

    def update_slider_label(label, text, value):
        label.configure(text=f"{text}: {int(value)}")
        update_object_count()


    def toggle_visibility(
        switch_variable, *slider_and_labels, frame
    ):
        if switch_variable.get() == "on":
            for i in range(0, len(slider_and_labels), 2):
                slider_label, slider = slider_and_labels[i], slider_and_labels[i+1]
                slider_label.grid(row=1 + i, column=0, padx=(10, 0), pady=(0, 10), sticky="w")
                slider.grid(row=1 + i, column=1, padx=10, pady=(0, 10), sticky="ew")
            frame.configure(fg_color="#d1d1d1")
        else:
            for i in range(0, len(slider_and_labels), 2):
                slider_label, slider = slider_and_labels[i], slider_and_labels[i+1]
                slider_label.grid_forget()
                slider.grid_forget()
            frame.configure(fg_color="#dfe1e1")


    # Save preset function
    def save_preset():
        # Get all parameter values
        preset_data = {
            "noise_type": noise_type_dropdown.get(),
            "width": width_slider.get(),
            "height": height_slider.get(),
            "scale": scale_slider.get(),
            "octaves": octaves_slider.get(),
            "persistence": persistence_slider.get(),
            "lacunarity": lacunarity_slider.get(),
            "resolution_factor": resolution_factor_slider.get(),
            "base_elevation": base_elevation_slider.get(),
            "min_height": min_height_slider.get(),
            "max_height": max_height_slider.get(),
            "add_trees": add_trees_switch.get(),
            "trees_density": trees_slider.get(),
            "trees_scale": trees_scale_slider.get(),
            "add_rocks": add_rocks_switch.get(),
            "rocks_min": rocks_min_slider.get(),
            "rocks_max": rocks_max_slider.get(),
            "rocks_point": rocks_point_slider.get(),
            "rocks_density": rocks_slider.get(),
            "add_sticks": add_sticks_switch.get(),
            "sticks_density": sticks_slider.get(),
            "sticks_scale": sticks_scale_slider.get(),
            "add_bushes": add_bushes_switch.get(),
            "bushes_scale": bushes_scale_slider.get(),
            "bushes_density": bushes_slider.get(),
            "add_volcano": add_volcano_switch.get(),
            "volcano_scale": volcano_scale_slider.get(),
            "volcano_density": volcano_slider.get(),
            "add_mushroom": add_mushroom_switch.get(),
            "mushroom_scale": mushroom_scale_slider.get(),
            "mushroom_density": mushroom_slider.get(),
        }
        # Open a file dialog for saving
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            with open(file_path, "w") as f:
                json.dump(preset_data, f)
            # Update the option menu
            preset_name = os.path.basename(file_path)[:-5]
            presets_optionmenu.configure(
                values=presets_optionmenu.cget("values") + [preset_name]
            )
            presets_optionmenu.set(preset_name)

    # Load preset function
    def load_preset():
        # Open a file dialog for loading
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                preset_data = json.load(f)
            # Update all parameter values
            noise_type_dropdown.set(preset_data["noise_type"])
            width_slider.set(preset_data["width"])
            height_slider.set(preset_data["height"])
            scale_slider.set(preset_data["scale"])
            octaves_slider.set(preset_data["octaves"])
            persistence_slider.set(preset_data["persistence"])
            lacunarity_slider.set(preset_data["lacunarity"])
            resolution_factor_slider.set(preset_data["resolution_factor"])
            base_elevation_slider.set(preset_data["base_elevation"])
            min_height_slider.set(preset_data["min_height"])
            max_height_slider.set(preset_data["max_height"])
            
            # Update the labels
            update_slider_label(width_label, "Mesh Width", preset_data["width"])
            update_slider_label(height_label, "Mesh Height", preset_data["height"])
            update_slider_label(scale_label, "Zoom Scale", preset_data["scale"])
            update_slider_label(octaves_label, "Octaves", preset_data["octaves"])
            update_slider_label(persistence_label, "Persistence", preset_data["persistence"])
            update_slider_label(lacunarity_label, "Lacunarity", preset_data["lacunarity"])
            update_slider_label(resolution_factor_label, "Resolution Factor", preset_data["resolution_factor"])
            update_slider_label(base_elevation_label, "Base Elevation", preset_data["base_elevation"])
            update_slider_label(min_height_label, "Min Height", preset_data["min_height"])
            update_slider_label(max_height_label, "Max Height", preset_data["max_height"])
            
            # Update the option menu
            preset_name = os.path.basename(file_path)[:-5]
            presets_optionmenu.configure(
                values=presets_optionmenu.cget("values") + [preset_name]
            )
            presets_optionmenu.set(preset_name)


    def toggle_trees_visibility(*args):
        toggle_visibility(
            add_trees_switch,
            trees_slider,trees_slider_label,
            trees_scale_slider,trees_scale_slider_label,
            frame = frame_trees,
        )

    def toggle_rocks_visibility(*args):
        toggle_visibility(
            add_rocks_switch,
            rocks_slider,rocks_slider_label,
            rocks_point_slider, rocks_point_slider_label,
            rocks_min_slider, rocks_min_slider_label,
            rocks_max_slider, rocks_max_slider_label,
            frame = frame_rocks,
        )


    def toggle_sticks_visibility(*args):
        toggle_visibility(
            add_sticks_switch,
            sticks_slider, sticks_slider_label,
            sticks_scale_slider, sticks_scale_slider_label,
            frame = frame_sticks,
        )

    def toggle_bushes_visibility(*args):
        toggle_visibility(
            add_bushes_switch,
            bushes_slider, bushes_slider_label,
            bushes_scale_slider, bushes_scale_slider_label,
            frame = frame_bushes,
        )

    def toggle_volcanos_visibility(*args):
        toggle_visibility(
            add_volcano_switch,
            volcano_slider, volcano_slider_label,
            volcano_scale_slider, volcano_scale_slider_label,
            frame = frame_volcanos,
        )


    def toggle_mushrooms_visibility(*args):
        toggle_visibility(
            add_mushroom_switch,
            mushroom_slider, mushroom_slider_label,
            mushroom_scale_slider, mushroom_scale_slider_label,
            frame = frame_mushrooms,
        )

    # MAIN WINDOW
    root = ctk.CTk()
    root.title("MeshScape")
    root.geometry("1366x768")
    ctk.set_appearance_mode("light")
    root.columnconfigure(0, weight=1)

    # Left Section
    left_section = ctk.CTkFrame(root)
    left_section.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    root.rowconfigure(0, weight=1)

    # Set the minimum width for the left section
    left_section.grid_columnconfigure(0, weight=1)

    #PROGRESS BAR
    progress_bar = ctk.CTkProgressBar(left_section, width=300)
    progress_bar.grid(row=4, column=0, columnspan=2, pady=(15, 15))
    progress_bar.set(0)

    # FRAME FOR TITLE LABEL
    frame_title = ctk.CTkFrame(left_section, fg_color="#62a5d9")
    frame_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 20), sticky="ew")
    frame_title.columnconfigure(0, weight=1)

    # TITLE LABEL
    title_label = ctk.CTkLabel(
        frame_title,
        text="MeshScape",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="white",
    )
    title_label.grid(row=0, column=0, pady=(10, 10))

    # PRESETS DROPDOWN MENU
    presets_label = ctk.CTkLabel(left_section, text="Preset:")
    presets_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

    presets_optionmenu = ctk.CTkOptionMenu(
        left_section,
        values=["Default"],
        width=200,
        fg_color="#b9bdbd",
        button_color="#9ca2a2",
        button_hover_color="#838b8b",
    )
    presets_optionmenu.grid(row=1, column=0, padx=(70, 10), pady=(10, 0), sticky="w")

    # SAVE PRESET BUTTON
    create_preset_button = ctk.CTkButton(
        left_section,
        text="Save",
        command=save_preset,
        width=50,
        fg_color="#9ca2a2",
        hover_color="#838b8b",
    )
    create_preset_button.grid(row=1, column=0, padx=(285, 0), pady=(10, 0), sticky="w")

    # LOAD PRESET BUTTON
    load_preset_button = ctk.CTkButton(
        left_section,
        text="Load",
        command=load_preset,
        width=50,
        fg_color="#9ca2a2",
        hover_color="#838b8b",
    )
    load_preset_button.grid(row=1, column=0, padx=(340, 0), pady=(10, 0), sticky="w")

    ############################################################################################################

    # TABVIEW
    tabview = ctk.CTkTabview(
        left_section,
        fg_color="#f2f3f3",
        segmented_button_fg_color="#9ca2a2",
        segmented_button_selected_color="#62a5d9",
        segmented_button_selected_hover_color="#4e84ae",
        segmented_button_unselected_color="#9ca2a2",
        segmented_button_unselected_hover_color="#838b8b",
    )
    tabview.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10)

    tabview.add("Noise")
    tabview.add("Terrain")
    tabview.add("Objects")

    tabview.set("Noise")

    tabview.tab("Noise").columnconfigure(0, weight=1)
    tabview.tab("Terrain").columnconfigure(0, weight=1)
    tabview.tab("Objects").columnconfigure(0, weight=1)

    ############################################################################################################

    # Visualization function

    def visualize_stl():
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import art3d
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from stl import mesh
            import matplotlib
            
            plt.switch_backend('agg')
            matplotlib.use("TkAgg")

            # Load the mesh
            your_mesh = mesh.Mesh.from_file('combined_terrain_with_objects.stl')

            # Simplify the mesh by taking every nth face (adjust the value of n for more/less simplification)
            n = 2
            simplified_vectors = your_mesh.vectors[::n]

            # Create the plot
            fig = plt.Figure(figsize=(5, 5))
            ax = fig.add_subplot(111, projection='3d')
            
            # Plot the simplified mesh
            poly3d = art3d.Poly3DCollection(simplified_vectors, alpha=0.5, edgecolor='k', linewidth=0.1)
            ax.add_collection3d(poly3d)
            
            # Auto scale to the mesh size
            scale = np.concatenate([your_mesh.min_, your_mesh.max_])
            ax.auto_scale_xyz(scale, scale, scale)

            # Set the view angle
            ax.view_init(elev=30, azim=45)
            
            # Hide axes for better visualization
            ax.set_axis_off()

            # Clear existing canvas if it exists
            for widget in frame_visualisation.winfo_children():
                widget.destroy()

            # Create a new canvas
            canvas = FigureCanvasTkAgg(fig, master=frame_visualisation)
            canvas.draw()
            widget = canvas.get_tk_widget()
            widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        except Exception as e:
            print(e)

        # Function to run the visualization in the main thread
    def run_visualization():
        root.after(100, visualize_stl)

    # Setup right section and frame visualization
    right_section = ctk.CTkFrame(root, fg_color="#dbdbdb")
    right_section.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
    right_section.columnconfigure(0, weight=1)

    frame_visualisation = ctk.CTkFrame(right_section, width=190, height=560, fg_color="white")
    frame_visualisation.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
    frame_visualisation.columnconfigure(0, weight=1)

    root.after(100, run_visualization)

    ############################################################################################################

    # FRAME_BASE_OBJECTS
    frame_base_objects = ctk.CTkScrollableFrame(
        tabview.tab("Objects"), height=400, fg_color="#f2f3f3"
    )
    frame_base_objects.grid(row=0, column=0, sticky="ew")
    frame_base_objects.columnconfigure(0, weight=1)

    # FRAME_TREES
    frame_trees = ctk.CTkFrame(
        frame_base_objects, border_width=0, fg_color="#dfe1e1", corner_radius=20
    )
    frame_trees.grid(row=0, column=0, sticky="ew")

    # FRAME_ROCKS
    frame_rocks = ctk.CTkFrame(
        frame_base_objects, border_width=0, fg_color="#dfe1e1", corner_radius=20
    )
    frame_rocks.grid(row=1, column=0, pady=(10, 0), sticky="ew")

    # FRAME_STICKS
    frame_sticks = ctk.CTkFrame(
        frame_base_objects, border_width=0, fg_color="#dfe1e1", corner_radius=20
    )
    frame_sticks.grid(row=2, column=0, pady=(10, 0), sticky="ew")

    # FRAME_BUSHES
    frame_bushes = ctk.CTkFrame(
        frame_base_objects, border_width=0, fg_color="#dfe1e1", corner_radius=20
    )
    frame_bushes.grid(row=3, column=0, pady=(10, 0), sticky="ew")

    # FRAME_VOLCANOES
    frame_volcanos = ctk.CTkFrame(
        frame_base_objects, border_width=0, fg_color="#dfe1e1", corner_radius=20
    )
    frame_volcanos.grid(row=4, column=0, pady=(10, 0), sticky="ew")

    # FRAME_MUSHROOMS
    frame_mushrooms = ctk.CTkFrame(
        frame_base_objects, border_width=0, fg_color="#dfe1e1", corner_radius=20
    )
    frame_mushrooms.grid(row=5, column=0, pady=(10, 10), sticky="ew")

    ############################################################################################################

    # ENABLE/DISABLE TREES SWITCH
    add_trees_switch = ctk.StringVar(value="off")
    add_trees_switch.trace_add(
        "write", toggle_trees_visibility
    )  # bind toggle_slider_visibility function to switch variable
    trees_switch = ctk.CTkSwitch(
        frame_trees,
        text="Trees",
        command=toggle_trees_visibility,
        variable=add_trees_switch,
        onvalue="on",
        offvalue="off",
    )
    trees_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # TREE SLIDERS
    trees_slider_label = ctk.CTkLabel(
        frame_trees, text="Density: 30", width=125, anchor="w"
    )
    trees_slider = ctk.CTkSlider(
        frame_trees,
        from_=0,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(trees_slider_label, "Density", value),
    )
    trees_slider.set(30)

    # TREE SCALE SLIDERS
    trees_scale_slider_label = ctk.CTkLabel(
        frame_trees, text="Scale: 10", width=125, anchor="w"
    )
    trees_scale_slider = ctk.CTkSlider(
        frame_trees,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(trees_scale_slider_label, "Scale", value),
    )
    trees_scale_slider.set(10)

    ############################################################################################################

    # ENABLE/DISABLE ADD ROCKS BUTTON
    add_rocks_switch = ctk.StringVar(value="off")
    add_rocks_switch.trace_add(
        "write", toggle_rocks_visibility
    )  # bind toggle_slider_visibility function to switch variable
    rocks_switch = ctk.CTkSwitch(
        frame_rocks,
        text="Rocks",
        command=toggle_rocks_visibility,
        variable=add_rocks_switch,
        onvalue="on",
        offvalue="off",
    )
    rocks_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # ROCKS SLIDERS
    rocks_slider_label = ctk.CTkLabel(
        frame_rocks, text="Density: 15", width=125, anchor="w"
    )
    rocks_slider = ctk.CTkSlider(
        frame_rocks,
        from_=0,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(rocks_slider_label, "Density", value),
    )
    rocks_slider.set(15)

    # ROCKS MIN SLIDERS
    rocks_min_slider_label = ctk.CTkLabel(
        frame_rocks, text="Min Size: 10", width=125, anchor="w"
    )
    rocks_min_slider = ctk.CTkSlider(
        frame_rocks,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(rocks_min_slider_label, "Min", value),
    )
    rocks_min_slider.set(10)

    # ROCKS MAX SLIDERS
    rocks_max_slider_label = ctk.CTkLabel(
        frame_rocks, text="Max Size: 15", width=125, anchor="w"
    )
    rocks_max_slider = ctk.CTkSlider(
        frame_rocks,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(rocks_max_slider_label, "Max", value),
    )
    rocks_max_slider.set(15)

    # ROCKS POINT SLIDERS
    rocks_point_slider_label = ctk.CTkLabel(
        frame_rocks, text="Points: 1000", width=125, anchor="w"
    )
    rocks_point_slider = ctk.CTkSlider(
        frame_rocks,
        from_=10,
        to=10000,
        width=330,  # make scalable to window
        number_of_steps=9990,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(rocks_point_slider_label, "Points", value),
    )
    rocks_point_slider.set(1000)

    ############################################################################################################

    # ENABLE/DISABLE ADD STICKS BUTTON
    add_sticks_switch = ctk.StringVar(value="off")
    add_sticks_switch.trace_add(
        "write", toggle_sticks_visibility
    )  # bind toggle_slider_visibility function to switch variable
    sticks_switch = ctk.CTkSwitch(
        frame_sticks,
        text="Sticks",
        command=toggle_sticks_visibility,
        variable=add_sticks_switch,
        onvalue="on",
        offvalue="off",
    )
    sticks_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # STICKS SLIDERS
    sticks_slider_label = ctk.CTkLabel(
        frame_sticks, text="Density: 50", width=125, anchor="w"
    )
    sticks_slider = ctk.CTkSlider(
        frame_sticks,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(sticks_slider_label, "Density", value),
    )
    sticks_slider.set(50)

    # STICK SCALE SLIDERS
    sticks_scale_slider_label = ctk.CTkLabel(
        frame_sticks, text="Scale: 10", width=125, anchor="w"
    )
    sticks_scale_slider = ctk.CTkSlider(
        frame_sticks,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(sticks_scale_slider_label, "Scale", value),
    )
    sticks_scale_slider.set(10)

    ############################################################################################################

    # ENABLE/DISABLE ADD BUSHES BUTTON
    add_bushes_switch = ctk.StringVar(value="off")
    add_bushes_switch.trace_add(
        "write", toggle_bushes_visibility
    )  # bind toggle_slider_visibility function to switch variable
    bushes_switch = ctk.CTkSwitch(
        frame_bushes,
        text="Bushes",
        command=toggle_bushes_visibility,
        variable=add_bushes_switch,
        onvalue="on",
        offvalue="off",
    )
    bushes_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # BUSHES SLIDERS
    bushes_slider_label = ctk.CTkLabel(
        frame_bushes, text="Density: 50", width=125, anchor="w"
    )
    bushes_slider = ctk.CTkSlider(
        frame_bushes,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(bushes_slider_label, "Density", value),
    )
    bushes_slider.set(50)

    # STICK SCALE SLIDERS
    bushes_scale_slider_label = ctk.CTkLabel(
        frame_bushes, text="Scale: 50", width=125, anchor="w"
    )
    bushes_scale_slider = ctk.CTkSlider(
        frame_bushes,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(bushes_scale_slider_label, "Scale", value),
    )
    bushes_scale_slider.set(50)

    ############################################################################################################

    # ENABLE/DISABLE ADD VOLCANO SWITCH
    add_volcano_switch = ctk.StringVar(value="off")
    add_volcano_switch.trace_add(
        "write", toggle_volcanos_visibility
    )  # bind toggle_slider_visibility function to switch variable
    volcano_switch = ctk.CTkSwitch(
        frame_volcanos,
        text="Anthills and Mounds",
        command=toggle_volcanos_visibility,
        variable=add_volcano_switch,
        onvalue="on",
        offvalue="off",
    )
    volcano_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # VOLCANO SLIDERS
    volcano_slider_label = ctk.CTkLabel(
        frame_volcanos, text="Density: 10", width=125, anchor="w"
    )
    volcano_slider = ctk.CTkSlider(
        frame_volcanos,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(volcano_slider_label, "Density", value),
    )
    volcano_slider.set(10)

    # VOLCANO SCALE SLIDERS
    volcano_scale_slider_label = ctk.CTkLabel(
        frame_volcanos, text="Scale: 60", width=125, anchor="w"
    )
    volcano_scale_slider = ctk.CTkSlider(
        frame_volcanos,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(volcano_scale_slider_label, "Scale", value),
    )
    volcano_scale_slider.set(60)

    ############################################################################################################

    # ENABLE/DISABLE ADD MUSHROOM SWITCH
    add_mushroom_switch = ctk.StringVar(value="off")
    add_mushroom_switch.trace_add(
        "write", toggle_mushrooms_visibility
    )  # bind toggle_slider_visibility function to switch variable
    mushroom_switch = ctk.CTkSwitch(
        frame_mushrooms,
        text="Small Plants",
        command=toggle_mushrooms_visibility,
        variable=add_mushroom_switch,
        onvalue="on",
        offvalue="off",
    )
    mushroom_switch.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    # MUSHROOM SLIDERS
    mushroom_slider_label = ctk.CTkLabel(
        frame_mushrooms, text="Density: 15", width=125, anchor="w"
    )
    mushroom_slider = ctk.CTkSlider(
        frame_mushrooms,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(mushroom_slider_label, "Density", value),
    )
    mushroom_slider.set(15)

    # MUSHROOM SCALE SLIDERS
    mushroom_scale_slider_label = ctk.CTkLabel(
        frame_mushrooms, text="Scale: 10", width=125, anchor="w"
    )
    mushroom_scale_slider = ctk.CTkSlider(
        frame_mushrooms,
        from_=1,
        to=100,
        width=330,  # make scalable to window
        number_of_steps=99,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(mushroom_scale_slider_label, "Scale", value),
    )
    mushroom_scale_slider.set(10)

    ############################################################################################################

    #OBJECT COUNTER

    def update_object_count():
        num_rocks = int(rocks_slider.get())
        num_trees = int(trees_slider.get())
        num_mushrooms = int(mushroom_slider.get())
        num_anthills = int(volcano_slider.get())
        num_sticks = int(sticks_slider.get())
        num_bushes = int(bushes_slider.get())

        if (add_trees_switch.get() == "off"):
            num_trees = 0
        if (add_rocks_switch.get() == "off"):
            num_rocks = 0
        if (add_sticks_switch.get() == "off"):
            num_sticks = 0
        if (add_bushes_switch.get() == "off"):
            num_bushes = 0
        if (add_volcano_switch.get() == "off"):
            num_anthills = 0
        if (add_mushroom_switch.get() == "off"):
            num_mushrooms = 0
        
        total_objects = num_rocks + num_trees + num_mushrooms + num_anthills + num_sticks + num_bushes
        object_count_label.configure(text=f"Total Objects: {total_objects}")

    object_count_label = ctk.CTkLabel(right_section, text="Total Objects: 0", font=ctk.CTkFont(size=14, weight="bold"))
    object_count_label.grid(row=1, column=0, pady=(10, 10), padx=10, sticky="s")

    update_object_count()

    ############################################################################################################

    # FRAME_BASE_NOISE
    frame_base_noise = ctk.CTkScrollableFrame(
        tabview.tab("Noise"), height=350, fg_color="#f2f3f3"
    )
    frame_base_noise.grid(
        row=0,
        column=0,
        sticky="ew",
    )

    # NOISE TYPE
    noise_type_label = ctk.CTkLabel(
        frame_base_noise, width=135, text="Noise Type: ", anchor="w"
    )
    noise_type_label.grid(row=0, column=0, sticky="w")

    noise_type_dropdown = ctk.CTkOptionMenu(
        frame_base_noise,
        values=['Perlin', 'Simplex', 'Value', 'Cellular'],
        width=100,
        fg_color="#b9bdbd",
        button_color="#9ca2a2",
        button_hover_color="#838b8b",
    )
    noise_type_dropdown.grid(row=0, column=1, sticky="w", padx=(15, 0))
    noise_type_dropdown.set("Perlin")

    # WIDTH
    width_label = ctk.CTkLabel(
        frame_base_noise, text="Mesh Width: 15", width=135, anchor="w"
    )
    width_label.grid(row=1, column=0, sticky="w", pady=(20, 0))

    width_slider = ctk.CTkSlider(
        frame_base_noise,
        from_=10,
        to=50,
        width=400,
        number_of_steps=50,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(width_label, "Mesh Width", value),
    )
    width_slider.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(20, 0))
    width_slider.set(15)

    # HEIGHT
    height_label = ctk.CTkLabel(
        frame_base_noise, text="Mesh Height: 15", width=135, anchor="w"
    )
    height_label.grid(row=2, column=0, sticky="w")

    height_slider = ctk.CTkSlider(
        frame_base_noise,
        from_=10,
        to=50,
        width=400,
        number_of_steps=50,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(height_label, "Mesh Height", value),
    )
    height_slider.grid(row=2, column=1, sticky="w", padx=(10, 0))
    height_slider.set(15)

    # SCALE
    scale_label = ctk.CTkLabel(
        frame_base_noise, text="Zoom Scale: 100", width=135, anchor="w"
    )
    scale_label.grid(row=3, column=0, sticky="w", pady=(20, 0))

    scale_slider = ctk.CTkSlider(
        frame_base_noise,
        from_=100,
        to=1000,
        width=400,
        number_of_steps=9,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(scale_label, "Zoom Scale", value),
    )
    scale_slider.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(20, 0))
    scale_slider.set(100)

    # OCTAVES
    octaves_label = ctk.CTkLabel(frame_base_noise, text="Octaves: 5", width=135, anchor="w")
    octaves_label.grid(row=4, column=0, sticky="w", pady=(20, 0))

    octaves_slider = ctk.CTkSlider(
        frame_base_noise,
        from_=1,
        to=10,
        width=400,
        number_of_steps=9,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(octaves_label, "Octaves", value),
    )
    octaves_slider.grid(row=4, column=1, sticky="w", padx=(10, 0), pady=(20, 0))
    octaves_slider.set(5)

    # PERSISTENCE
    persistence_label = ctk.CTkLabel(
        frame_base_noise, text="Persistence: 5", width=135, anchor="w"
    )
    persistence_label.grid(row=5, column=0, sticky="w")

    persistence_slider = ctk.CTkSlider(
        frame_base_noise,
        from_=1,
        to=10,
        width=400,
        number_of_steps=9,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(persistence_label, "Persistence", value),
    )
    persistence_slider.grid(row=5, column=1, sticky="w", padx=(10, 0))
    persistence_slider.set(5)

    # LACUNARITY
    lacunarity_label = ctk.CTkLabel(
        frame_base_noise, text="Lacunarity: 5", width=135, anchor="w"
    )
    lacunarity_label.grid(row=6, column=0, sticky="w")

    lacunarity_slider = ctk.CTkSlider(
        frame_base_noise,
        from_=1,
        to=10,
        width=400,
        number_of_steps=9,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(lacunarity_label, "Lacunarity", value),
    )
    lacunarity_slider.grid(row=6, column=1, sticky="w", padx=(10, 0))
    lacunarity_slider.set(5)

    ############################################################################################################

    # FRAME_BASE_TERRAIN
    frame_base_terrain = ctk.CTkScrollableFrame(
        tabview.tab("Terrain"), height=350, fg_color="#f2f3f3"
    )
    frame_base_terrain.grid(
        row=0,
        column=0,
        sticky="ew",
    )

    # RESOLUTION FACTOR
    resolution_factor_label = ctk.CTkLabel(
        frame_base_terrain, text="Resolution Factor: 10", width=135, anchor="w"
    )
    resolution_factor_label.grid(row=0, column=0, sticky="w")

    resolution_factor_slider = ctk.CTkSlider(
        frame_base_terrain,
        from_=1,
        to=20,
        width=400,
        number_of_steps=20,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(
            resolution_factor_label, "Resolution Factor", value
        ),
    )
    resolution_factor_slider.grid(row=0, column=1, sticky="w", padx=(10, 0))
    resolution_factor_slider.set(10)

    # BASE ELEVATION
    base_elevation_label = ctk.CTkLabel(
        frame_base_terrain, text="Base Elevation: 200", width=135, anchor="w"
    )
    base_elevation_label.grid(row=1, column=0, sticky="w", pady=(20, 0))

    base_elevation_slider = ctk.CTkSlider(
        frame_base_terrain,
        from_=0,
        to=500,
        width=400,
        number_of_steps=100,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(
            base_elevation_label, "Base Elevation", value
        ),
    )
    base_elevation_slider.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(20, 0))
    base_elevation_slider.set(200)

    # MIN HEIGHT
    min_height_label = ctk.CTkLabel(
        frame_base_terrain, text="Min  Height: 100", width=135, anchor="w"
    )
    min_height_label.grid(row=2, column=0, sticky="w", pady=(20, 0))

    min_height_slider = ctk.CTkSlider(
        frame_base_terrain,
        from_=0,
        to=500,
        width=400,
        number_of_steps=100,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(min_height_label, "Min  Height", value),
    )
    min_height_slider.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(20, 0))
    min_height_slider.set(100)

    # MAX HEIGHT
    max_height_label = ctk.CTkLabel(
        frame_base_terrain, text="Max Height: 300", width=135, anchor="w"
    )
    max_height_label.grid(row=3, column=0, sticky="w")

    max_height_slider = ctk.CTkSlider(
        frame_base_terrain,
        from_=0,
        to=500,
        width=400,
        number_of_steps=100,
        button_color="#62a5d9",
        button_hover_color="#4e84ae",
        command=lambda value: update_slider_label(max_height_label, "Max Height", value),
    )
    max_height_slider.grid(row=3, column=1, sticky="w", padx=(10, 0))
    max_height_slider.set(300)

    ############################################################################################################

    # OBJECT FRAME CLICKABLE
    def bind_toggle_switch_and_cursor(frame, switch_variable, toggle_function):
        def toggle_frame_switch(event):
            # Toggle the switch value when the frame is clicked
            if switch_variable.get() == "on":
                switch_variable.set("off")
            else:
                switch_variable.set("on")
            toggle_function()

        frame.bind("<Button-1>", toggle_frame_switch)
        frame.configure(cursor="hand2")

    bind_toggle_switch_and_cursor(frame_trees, add_trees_switch, toggle_trees_visibility)
    bind_toggle_switch_and_cursor(frame_rocks, add_rocks_switch, toggle_rocks_visibility)
    bind_toggle_switch_and_cursor(frame_sticks, add_sticks_switch, toggle_sticks_visibility)
    bind_toggle_switch_and_cursor(frame_bushes, add_bushes_switch, toggle_bushes_visibility)
    bind_toggle_switch_and_cursor(frame_volcanos, add_volcano_switch, toggle_volcanos_visibility)
    bind_toggle_switch_and_cursor(frame_mushrooms, add_mushroom_switch, toggle_mushrooms_visibility)

    ############################################################################################################

    # GENERATE MESH BUTTON
    genmesh_button = ctk.CTkButton(
        left_section,
        text="Generate Mesh",
        width=200,
        height=40,
        fg_color="#62a5d9",
        hover_color="#4e84ae",
        command=generate_noise
    )
    genmesh_button.grid(row=3, column=0, columnspan=2, pady=(10, 10), sticky="s")
    left_section.rowconfigure(2, weight=1)
    root.withdraw()
    splash_root.after(4000, splash_root.destroy)
    root.after(4500, root.deiconify)
    root.mainloop()
    
splash_root.after(1000, main_window)
splash_root.mainloop()

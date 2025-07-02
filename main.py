import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
from PIL import Image, ImageTk
import io

WEATHER_API_KEY = 'a696a68c2ff9eefe7384910d20c44a08'
LOCATIONIQ_API_KEY = 'pk.e1c432909dbba7e4616d8856b7b56463'

current_lat = None
current_lon = None
loading_label = None

map_offset_x = 0
map_offset_y = 0

move_step = 0.5

def get_weather_and_map():
    global current_lat, current_lon, map_offset_x, map_offset_y

    city = entry_city.get()
    zoom = int(zoom_scale.get())

    if not city:
        messagebox.showerror("Input Error", "Please enter a city name.")
        return

    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        if weather_response.status_code != 200:
            messagebox.showerror("API Error", f"Weather error: {weather_data.get('message', 'Unknown error')}")
            return

        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        wind_speed = weather_data['wind']['speed']
        description = weather_data['weather'][0]['description'].capitalize()
        icon_code = weather_data['weather'][0]['icon']
        current_lat = weather_data['coord']['lat']
        current_lon = weather_data['coord']['lon']

        label_result.config(text=f"Weather in {city}:\n"
                                 f"Temperature: {temperature}°C\n"
                                 f"Condition: {description}\n"
                                 f"Humidity: {humidity}%\n"
                                 f"Pressure: {pressure} hPa\n"
                                 f"Wind Speed: {wind_speed} m/s")

        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_response = requests.get(icon_url)
        icon_data = icon_response.content
        icon_image = Image.open(io.BytesIO(icon_data))
        icon_image = icon_image.resize((80, 80))
        icon_photo = ImageTk.PhotoImage(icon_image)
        icon_label.config(image=icon_photo)
        icon_label.image = icon_photo

        map_offset_x = 0
        map_offset_y = 0

        load_map()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_map():
    global loading_label

    zoom = int(zoom_scale.get())

    if current_lat is None or current_lon is None:
        return

    loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    window.update_idletasks()

    try:
        center_lat = current_lat + map_offset_y
        center_lon = current_lon + map_offset_x

        map_url = f"https://maps.locationiq.com/v3/staticmap?key={LOCATIONIQ_API_KEY}&center={center_lat},{center_lon}&zoom={zoom}&size=600x400"
        map_response = requests.get(map_url)

        if map_response.status_code != 200:
            messagebox.showerror("API Error", "Failed to load map.")
            loading_label.place_forget()
            return

        map_data = map_response.content
        map_image = Image.open(io.BytesIO(map_data))
        map_image = map_image.resize((600, 400))
        map_photo = ImageTk.PhotoImage(map_image)

        map_label.config(image=map_photo)
        map_label.image = map_photo

    except Exception as e:
        messagebox.showerror("Error", str(e))

    loading_label.place_forget()

def on_mouse_wheel(event):
    zoom = int(zoom_scale.get())

    if event.delta > 0:
        if zoom < 18:
            zoom += 1
    else:
        if zoom > 1:
            zoom -= 1

    zoom_scale.set(zoom)
    load_map()

def move_map(direction):
    global map_offset_x, map_offset_y

    if direction == 'up':
        map_offset_y += move_step
    elif direction == 'down':
        map_offset_y -= move_step
    elif direction == 'left':
        map_offset_x -= move_step
    elif direction == 'right':
        map_offset_x += move_step

    load_map()

window = tk.Tk()
window.title("Weather and Map Dashboard with Smooth Zoom, Panning, and Loading")
window.geometry("800x1000")

tk.Label(window, text="Enter City:", font=('Arial', 14)).pack(pady=5)
entry_city = tk.Entry(window, width=30, font=('Arial', 14))
entry_city.pack(pady=5)

zoom_scale = tk.Scale(window, from_=1, to=18, orient=tk.HORIZONTAL, label="Map Zoom Level", font=('Arial', 12))
zoom_scale.set(12)
zoom_scale.pack(pady=5)

btn_search = tk.Button(window, text="Search Weather & Map", command=get_weather_and_map, font=('Arial', 14))
btn_search.pack(pady=10)

label_result = tk.Label(window, text="", font=('Arial', 14), justify='left')
label_result.pack(pady=10)

icon_label = tk.Label(window)
icon_label.pack()

map_label = tk.Label(window)
map_label.pack(pady=10)
map_label.bind("<MouseWheel>", on_mouse_wheel)

btn_frame = tk.Frame(window)
btn_frame.pack(pady=10)

btn_up = tk.Button(btn_frame, text="⬆", command=lambda: move_map('up'), width=5)
btn_up.grid(row=0, column=1, padx=5)

btn_left = tk.Button(btn_frame, text="⬅", command=lambda: move_map('left'), width=5)
btn_left.grid(row=1, column=0, padx=5)

btn_right = tk.Button(btn_frame, text="➡", command=lambda: move_map('right'), width=5)
btn_right.grid(row=1, column=2, padx=5)

btn_down = tk.Button(btn_frame, text="⬇", command=lambda: move_map('down'), width=5)
btn_down.grid(row=2, column=1, padx=5)

loading_label = tk.Label(window, text="Loading...", font=('Arial', 20), fg='red')

window.mainloop()

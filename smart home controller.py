import flet as ft
import datetime

# --- Data Models & State ---

class Device:
    def __init__(self, dev_id, name, dev_type, state, details_desc, icon):
        self.id = dev_id
        self.name = name
        self.type = dev_type
        self.state = state  # Can be "ON", "OFF", "LOCKED", "UNLOCKED", or a number/float
        self.details_desc = details_desc
        self.icon = icon

class AppState:
    def __init__(self):
        self.devices = {
            "light1": Device("light1", "Living Room", "light", "OFF", "Main light", ft.Icons.LIGHTBULB),
            "door1": Device("door1", "Front Door", "lock", "LOCKED", "Security Lock", ft.Icons.DOOR_FRONT_DOOR),
            "thermostat1": Device("thermostat1", "Thermostat", "thermostat", 22.0, "Climate Control", ft.Icons.THERMOSTAT),
            "fan1": Device("fan1", "Ceiling Fan", "fan", 0, "Ventilation", ft.Icons.WIND_POWER),
            "light2": Device("light2", "Kitchen", "light", "ON", "Spotlights", ft.Icons.LIGHTBULB_OUTLINE),
            "humidifier": Device("humidifier", "Humidifier", "fan", 1, "Air Quality", ft.Icons.WATER_DROP),
        }
        self.logs = [
            {"time": "08:12:32", "device": "light1", "action": "Turn ON", "user": "Amrit"},
            {"time": "08:13:23", "device": "light1", "action": "Turn OFF", "user": "Amrit"},
            {"time": "08:13:26", "device": "light1", "action": "Turn ON", "user": "Amrit"},
        ]

    def get_device(self, dev_id):
        return self.devices.get(dev_id)

    def toggle_device(self, dev_id):
        dev = self.devices.get(dev_id)
        if dev:
            if dev.type == "light":
                dev.state = "ON" if dev.state == "OFF" else "OFF"
            elif dev.type == "lock":
                dev.state = "LOCKED" if dev.state == "UNLOCKED" else "UNLOCKED"
            self.log_action(dev_id, f"Set to {dev.state}")

    def set_device_value(self, dev_id, value):
        dev = self.devices.get(dev_id)
        if dev:
            dev.state = value
            # self.log_action(dev_id, f"Set to {value}")

    def log_action(self, dev_id, action):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs.insert(0, {"time": now, "device": dev_id, "action": action, "user": "Amrit"})


app_state = AppState()

# --- Styles & Assets ---

# Colors
BG_GRADIENT = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=["#1A1A2E", "#16213E", "#0F3460"]
)
CARD_BG_COLOR = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
CARD_BORDER_COLOR = ft.Colors.with_opacity(0.2, ft.Colors.WHITE)
TEXT_COLOR = ft.Colors.WHITE
ACCENT_COLOR = ft.Colors.PINK_ACCENT

# --- Views ---

def main(page: ft.Page):
    page.title = "Smart Home Controller"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 1200
    page.window_height = 900
    page.bgcolor = "#1A1A2E" # Fallback

    def route_change(route):
        page.views.clear()
        
        # Main Background Container
        main_container = ft.Container(
            expand=True,
            gradient=BG_GRADIENT,
            padding=30,
            content=None # To be filled based on route
        )

        if page.route == "/":
            main_container.content = create_overview_view(page)
            page.views.append(
                ft.View(
                    "/",
                    [main_container],
                    padding=0
                )
            )
        elif page.route == "/stats":
            main_container.content = create_statistics_view(page)
            page.views.append(
                ft.View(
                    "/stats",
                    [main_container],
                    padding=0
                )
            )
        elif page.route.startswith("/details/"):
            dev_id = page.route.split("/")[-1]
            main_container.content = create_details_view(page, dev_id)
            page.views.append(
                ft.View(
                    f"/details/{dev_id}",
                    [main_container],
                    padding=0
                )
            )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

def get_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"

def create_overview_view(page):
    
    # Mutable control references
    status_texts = {}
    action_buttons = {}
    value_labels = {}
    icon_controls = {}

    def go_details(e):
        dev_id = e.control.data
        page.go(f"/details/{dev_id}")

    def toggle_click(e):
        dev_id = e.control.data
        app_state.toggle_device(dev_id)
        dev = app_state.get_device(dev_id)
        
        # Update UI
        if dev_id in status_texts:
            status_text = "ON" if dev.state == "ON" else "OFF"
            if dev.type == "lock":
                status_text = "LOCKED" if dev.state == "LOCKED" else "UNLOCKED"
            status_texts[dev_id].value = status_text
            
        if dev_id in icon_controls:
             # Toggle icon color based on device type and state
             if dev.type == "light":
                 icon_controls[dev_id].color = ft.Colors.GREEN if dev.state == "ON" else ft.Colors.GREY_700
             elif dev.type == "lock":
                 icon_controls[dev_id].color = ft.Colors.GREEN if dev.state == "UNLOCKED" else ft.Colors.RED
             
        page.update()

    def slider_change(e):
        dev_id = e.control.data
        val = e.control.value
        app_state.set_device_value(dev_id, val)
        dev = app_state.get_device(dev_id)

        if dev_id in value_labels:
            val_text = f"{int(dev.state)}°C" if dev.type == "thermostat" else f"{int(dev.state)}"
            value_labels[dev_id].value = val_text
            
        page.update()

    # --- Components ---

    def build_weather_card():
        return ft.Container(
            width=300,
            padding=20,
            border_radius=20,
            gradient=ft.LinearGradient(
                colors=[ft.Colors.PURPLE_700, ft.Colors.PINK_600],
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
            ),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.LOCATION_ON, color="white", size=16),
                            ft.Text("Kuopio, Finland", color="white", size=14, weight=ft.FontWeight.W_500),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("-10°", size=40, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text("Partly Cloudy", color="white70", size=14),
                                ],
                                spacing=0
                            ),
                            ft.Icon(ft.Icons.CLOUD, color="white", size=50),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.Text("H: -2° L: -12°", color="white70", size=12),
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ]
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, "black"),
                offset=ft.Offset(0, 5),
            )
        )

    def build_device_card(dev_id, is_slider=False, min_val=0, max_val=100, divisions=10):
        dev = app_state.get_device(dev_id)
        
        # State Logic
        is_active = dev.state in ["ON", "UNLOCKED"]
        # Set icon color based on device type and state
        if dev.type == "light":
            icon_color = ft.Colors.GREEN if dev.state == "ON" else ft.Colors.GREY_700
        elif dev.type == "lock":
            icon_color = ft.Colors.GREEN if dev.state == "UNLOCKED" else ft.Colors.RED
        else:
            icon_color = ACCENT_COLOR if is_active else ft.Colors.WHITE54
        
        # Icon
        icon = ft.Icon(dev.icon, size=30, color=icon_color)
        icon_controls[dev_id] = icon

        # Status Text
        status_str = str(dev.state)
        if dev.type == "thermostat":
            status_str = f"{int(dev.state)}°C"
        elif dev.type == "fan" and is_slider:
            status_str = f"{int(dev.state)}"
            
        txt_status = ft.Text(status_str, size=14, color="white70")
        if not is_slider:
            status_texts[dev_id] = txt_status
        else:
            value_labels[dev_id] = txt_status

        # Controls
        control_element = None
        if is_slider:
            control_element = ft.Slider(
                min=min_val, max=max_val, divisions=divisions, value=dev.state,
                active_color=ACCENT_COLOR, thumb_color="white",
                data=dev_id, on_change=slider_change
            )
        else:
            control_element = ft.Switch(
                value=is_active,
                active_color=ACCENT_COLOR,
                data=dev_id,
                on_change=toggle_click
            )

        return ft.Container(
            bgcolor=CARD_BG_COLOR,
            border=ft.border.all(1, CARD_BORDER_COLOR),
            border_radius=20,
            padding=15,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=icon,
                                padding=10,
                                bgcolor=ft.Colors.with_opacity(0.1, "white"),
                                border_radius=10
                            ),
                            ft.IconButton(ft.Icons.MORE_VERT, icon_color="white54", data=dev_id, on_click=go_details)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Container(height=10),
                    ft.Text(dev.name, size=16, weight=ft.FontWeight.W_600, color="white"),
                    txt_status,
                    ft.Container(height=5),
                    control_element
                ],
            )
        )

    # --- Layout Construction ---

    greeting_text = ft.Column(
        [
            ft.Text(f"{get_greeting()},", size=16, color="white70"),
            ft.Text("Amrit Singh", size=28, weight=ft.FontWeight.BOLD, color="white"),
        ],
        spacing=2
    )

    # Left Side: Greeting + Devices Grid
    left_content = ft.Column(
        [
            greeting_text,
            ft.Container(height=20),
            ft.Text("My Devices", size=20, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=10),
            ft.ResponsiveRow(
                [
                    ft.Column([build_device_card("light1")], col={"sm": 6, "md": 4}),
                    ft.Column([build_device_card("door1")], col={"sm": 6, "md": 4}),
                    ft.Column([build_device_card("light2")], col={"sm": 6, "md": 4}),
                    ft.Column([build_device_card("thermostat1", True, 16, 30, 14)], col={"sm": 12, "md": 6}),
                    ft.Column([build_device_card("fan1", True, 0, 3, 3)], col={"sm": 12, "md": 6}),
                ],
                run_spacing=20,
            )
        ],
        expand=True,
        scroll=ft.ScrollMode.HIDDEN
    )

    # Right Side: Weather + Stats Button + Extra
    right_content = ft.Column(
        [
            build_weather_card(),
            ft.Container(height=20),
            ft.Container(
                width=300,
                padding=20,
                bgcolor=CARD_BG_COLOR,
                border=ft.border.all(1, CARD_BORDER_COLOR),
                border_radius=20,
                content=ft.Column(
                    [
                        ft.Text("Quick Actions", size=16, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "View Statistics",
                            icon=ft.Icons.BAR_CHART,
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE),
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                            on_click=lambda _: page.go("/stats"),
                            width=260
                        ),
                        ft.Container(height=10),
                         ft.ElevatedButton(
                            "Security Log",
                            icon=ft.Icons.SECURITY,
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.RED),
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                            on_click=lambda _: page.go("/stats"), # Reusing stats for now
                            width=260
                        )
                    ]
                )
            )
        ],
        alignment=ft.MainAxisAlignment.START
    )

    return ft.Row(
        [
            left_content,
            ft.VerticalDivider(width=1, color="white10"),
            right_content
        ],
        expand=True,
        spacing=30,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

def create_statistics_view(page):
    # Reusing similar logic but styled
    
    data_points = [
        ft.LineChartDataPoint(0, 3),
        ft.LineChartDataPoint(2, 5),
        ft.LineChartDataPoint(4, 4),
        ft.LineChartDataPoint(6, 2),
        ft.LineChartDataPoint(8, 6),
        ft.LineChartDataPoint(10, 5),
    ]

    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=data_points,
                stroke_width=3,
                color=ACCENT_COLOR,
                curved=True,
                stroke_cap_round=True,
                below_line_bgcolor=ft.Colors.with_opacity(0.2, ACCENT_COLOR),
            )
        ],
        border=ft.border.all(0, ft.Colors.TRANSPARENT),
        left_axis=ft.ChartAxis(labels_size=0),
        bottom_axis=ft.ChartAxis(labels_size=0),
        tooltip_bgcolor=ft.Colors.with_opacity(0.8, "black"),
        min_y=0, max_y=8, min_x=0, max_x=10,
        expand=True,
    )

    rows = []
    for log in app_state.logs:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(log["time"], color="white70")),
                    ft.DataCell(ft.Text(log["device"], color="white70")),
                    ft.DataCell(ft.Text(log["action"], color="white70")),
                ]
            )
        )

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time", color="white", weight="bold")),
            ft.DataColumn(ft.Text("Device", color="white", weight="bold")),
            ft.DataColumn(ft.Text("Action", color="white", weight="bold")),
        ],
        rows=rows,
        border=ft.border.all(1, "white10"),
        heading_row_color=ft.Colors.with_opacity(0.1, "white"),
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: page.go("/")),
                    ft.Text("Statistics & Logs", size=24, weight="bold", color="white"),
                ]
            ),
            ft.Container(height=20),
            ft.Text("Power Consumption", size=18, color="white"),
            ft.Container(
                content=chart,
                height=250,
                bgcolor=CARD_BG_COLOR,
                border_radius=20,
                padding=20,
                border=ft.border.all(1, CARD_BORDER_COLOR)
            ),
            ft.Container(height=20),
            ft.Text("Recent Activity", size=18, color="white"),
            ft.Container(
                content=data_table,
                bgcolor=CARD_BG_COLOR,
                border_radius=20,
                padding=10,
                border=ft.border.all(1, CARD_BORDER_COLOR)
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

def create_details_view(page, dev_id):
    dev = app_state.get_device(dev_id)
    if not dev:
        return ft.Text("Device not found", color="red")

    return ft.Container(
        padding=40,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: page.go("/")),
                        ft.Text(dev.name, size=28, weight="bold", color="white"),
                    ]
                ),
                ft.Container(height=20),
                ft.Container(
                    padding=40,
                    bgcolor=CARD_BG_COLOR,
                    border_radius=20,
                    border=ft.border.all(1, CARD_BORDER_COLOR),
                    content=ft.Column(
                        [
                            ft.Icon(dev.icon, size=60, color=ACCENT_COLOR),
                            ft.Container(height=20),
                            ft.Text(f"Type: {dev.type.upper()}", size=16, color="white70"),
                            ft.Text(f"Current State: {dev.state}", size=20, weight="bold", color="white"),
                            ft.Container(height=20),
                            ft.Text(dev.details_desc, color="white54"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center
                )
            ]
        )
    )

if __name__ == "__main__":
    ft.app(target=main)

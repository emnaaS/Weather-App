import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGraphicsOpacityEffect)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve)
from PyQt5.QtGui import QPainter, QLinearGradient, QColor

#QPainter draws directly onto the window
#QLinearGradient defines a gradient between two colors
#QColor represents a color
#QGraphicsOpacityEffect lets you control the transparency of a widget
#QPropertyAnimation animates a value over time
#QEasingCurve controls the speed curve of that animation

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self._bg_top = QColor("#00FFEF")  # default top color (turquoise blue), shown before any city is searched
        self._bg_bottom = QColor("#16213E")  # default bottom color (navy blue)
        self.city_label = QLabel("Enter City Name:", self)
        self.city_input = QLineEdit(self) #input box
        self.get_weather_button = QPushButton("Get Weather", self) #add button
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.opacity_effect = QGraphicsOpacityEffect()  # creates an opacity "filter" that can be attached to a widget
        self.temperature_label.setGraphicsEffect(self.opacity_effect) # attaches that filter to your temperature label
        self.opacity_effect.setOpacity(0) # starts it fully invisible (0 = invisible, 1 = fully visible)
        self.initUI()

    def initUI(self): #user interface
        self.setWindowTitle("Weather App")
        vbox = QVBoxLayout() #vertical layout manager to handle all the widgets
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)
        self.setLayout(vbox)
        #align horizontally
        self.city_label.setAlignment(Qt.AlignCenter)
        #we will do the same for the rest but the weather button as it will take the width of the window
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        #we will apply styles
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        #style sheet
        self.setStyleSheet("""
            QPushButton{
            font-family: calibri; color: #080884;
            }
            QLabel{
            font-family: calibri; 
            }
            QLabel#city_label{
            font-size: 40px;
            font-style: italic;
            color: #080884;
            }
            QLineEdit#city_input{  /*line edit widget*/
            font-size : 40px;
            }
            QPushButton#get_weather_button{
            font-size: 25px;
            font-weight: 500;
            }
            QLabel#temperature_label{
            font-size: 75px;
            }
            QLabel#emoji_label{
            font-size: 100px;
            font-family: segoe UI emoji;
            }
            QLabel#description_label{
            font-size: 50px;
            }
            
        """)

        #connect the button get weather to the methode
        self.get_weather_button.clicked.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)  # ✅ fires get_weather when Enter is pressed

    def get_weather(self):
        api_key = "your_api_key_here" 
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status() #raise an exception in case http error
            #what we will read
            data = response.json()

            #this means the city exits and everything works fine
            if data["cod"] == 200:
                self.display_weather(data)

        #HTTPError if cod is between 400 and 500
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad Request\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized\nInvalid API Key")
                case 403:
                    self.display_error("Forbidden\nAccess is denied")
                case 404:
                    self.display_error("Not found\nCity not found")
                case 500:
                    self.display_error("Internal server error\nPlease try again later")
                case 502:
                    self.display_error("Bad gateway\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout\nNo response from the server")
                case _:
                    self.display_error("HTTP error occurred\n{http_error}")

        #connection error exceptions
        except requests.exceptions.ConnectionError:
            self.display_error("Connection error\nPlease check your internet connection")

        #timeout exceptions
        except requests.exceptions.Timeout:
            self.display_error("Timeout error\nThe request timed out")

        #redirects error
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects\nPlease the URL")

        #any other error
        except requests.exceptions.RequestException as req_error:
            self.display_error("Request error\n{req_error}")

    def display_error(self , message):
        # ✅ reset background to default dark navy
        self._bg_top = QColor("#00FFEF")  # restores the default top color
        self._bg_bottom = QColor("#16213E")  # restores the default bottom color
        self.update()  # triggers paintEvent to repaint the window with the reset colors
        self.temperature_label.setStyleSheet("font-size: 30px; color:'#4c3228'; font-weight: 600;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()
        # ✅ same fade-in animation as in display_weather
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(0)  # starts invisible
        self.anim.setEndValue(1)  # fades to fully visible
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def display_weather(self, data):
        #running this displays within the data a dictionary called main that contains the temperature
        #print(data)
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15 #in celcius
        self.temperature_label.setText(f"{temperature_c:.0f}°C")
        #description
        description = data["weather"][0]["description"]
        self.description_label.setText(description)
        weather_id= data["weather"][0]["id"]

        if 200 <= weather_id <= 232:
            self._bg_top, self._bg_bottom = QColor("#1a1a2e"), QColor("#16213E")  # stormy: dark navy tones
        elif 500 <= weather_id <= 531:
            self._bg_top, self._bg_bottom = QColor("#2F4F6F"), QColor("#4682B4")  # rainy: steel blue tones
        elif 600 <= weather_id <= 622:
            self._bg_top, self._bg_bottom = QColor("#E0F0FF"), QColor("#B0D4F1")  # snowy: icy light blue
        elif weather_id == 800:
            self._bg_top, self._bg_bottom = QColor("#C6FCFF"), QColor("#0977DB")  # sunny: warm gold to orange
        else:
            self._bg_top, self._bg_bottom = QColor("#778899"), QColor("#B0C4DE")  # cloudy: muted gray-blue
        self.update()  # tells PyQt5 "the window needs to be redrawn", which triggers paintEvent with the new colors

        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity") # tells PyQt5 "animate the opacity property of this effect"
        self.anim.setDuration(600) #animation lasts 600 milliseconds (0.6 seconds)
        self.anim.setStartValue(0) #starts from invisible
        self.anim.setEndValue(1) #ends fully visible
        self.anim.setEasingCurve(QEasingCurve.OutCubic) #starts fast then slows down at the end, feels more natural than a linear fade
        self.anim.start() #actually triggers the animation

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height()) #creates a vertical gradient (top to bottom), the four numbers are: start x, start y, end x, end y
        gradient.setColorAt(0, self._bg_top) # sets the colour at the top of the gradient (position 0)
        gradient.setColorAt(1, self._bg_bottom) # sets the colour at the bottom (position 1)
        painter.fillRect(self.rect(), gradient) # fills the entire window rectangle with that gradient

    #a method that belongs to a class but doesn't require any data or method from that class
    @staticmethod
    def get_weather_emoji(weather_id):
        if 200 <= weather_id <= 232:
            return "⛈"
        elif 300 <= weather_id <= 321:
            return "☁️"
        elif 500 <= weather_id <= 531:
            return "🌧️"
        elif 600 <= weather_id <= 622:
            return "❄️"
        elif 700 <= weather_id <= 741:
            return "🌫️"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    weather_app= WeatherApp()
    weather_app.show() #displays the window but instant exit
    sys.exit(app.exec_()) #maintain the window until manual exit

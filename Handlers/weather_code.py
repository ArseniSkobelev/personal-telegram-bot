class WeatherCodeHandler():
    def __init__(self):
        pass

    def get_weather_status(self, weather_code):
        if weather_code == "0":
            return "clear sky"
        elif weather_code == "1" or weather_code == "2" or weather_code == "3":
            return "partly cloudy"
        elif weather_code == "51" or weather_code == "53" or weather_code == "55":
            return "drizzle"
        elif weather_code == "56" or weather_code == "57":
            return "freezing drizzle"
        elif weather_code == "61" or weather_code == "63" or weather_code == "65":
            return "rain"
        elif weather_code == "66" or weather_code == "67":
            return "freezing rain"
        elif weather_code == "71" or weather_code == "73" or weather_code == "75":
            return "snow fall"
        elif weather_code == "77":
            return "snow grains"
        elif weather_code == "80" or weather_code == "81" or weather_code == "82":
            return "rain showers"
        elif weather_code == "85" or weather_code == "86":
            return "snow showers"
        if weather_code == "95":
            return "thunderstorm"
        elif weather_code == "96" or weather_code == "99":
            return "thunderstorm"

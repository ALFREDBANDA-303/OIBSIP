"""
Weather service for the Voice Assistant.
"""

import requests
from dotenv import load_dotenv
import os


load_dotenv()


class WeatherService:
    """Retrieve current weather information."""

    def __init__(self, speech_manager):
        self.speech = speech_manager
        self.api_key = os.getenv("OPENWEATHER_API_KEY")

    def get_weather(self, city):
        """Get current weather for a city."""

        if not city:
            self.speech.speak(
                "Please tell me the city."
            )
            return

        if not self.api_key:
            self.speech.speak(
                "The weather service is not configured."
            )
            return

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
        )

        parameters = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
        }

        try:
            response = requests.get(
                url,
                params=parameters,
                timeout=10,
            )

            if response.status_code == 404:
                self.speech.speak(
                    f"I could not find weather information "
                    f"for {city}."
                )
                return

            response.raise_for_status()

            data = response.json()

            city_name = data["name"]
            temperature = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]

            message = (
                f"The weather in {city_name} is "
                f"{description}. "
                f"The temperature is {temperature:.1f} "
                f"degrees Celsius. "
                f"It feels like {feels_like:.1f} "
                f"degrees. "
                f"Humidity is {humidity} percent."
            )

            self.speech.speak(message)

        except requests.exceptions.Timeout:
            self.speech.speak(
                "The weather service took too long to respond."
            )

        except requests.exceptions.ConnectionError:
            self.speech.speak(
                "I cannot connect to the weather service. "
                "Please check your internet connection."
            )

        except requests.exceptions.RequestException:
            self.speech.speak(
                "I could not retrieve the weather information."
            )

        except KeyError:
            self.speech.speak(
                "The weather service returned unexpected information."
            )

        except Exception:
            self.speech.speak(
                "Something went wrong while getting the weather."
            )
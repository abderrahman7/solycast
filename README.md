# SolyCast ☀️

SolyCast is a Python-based solar energy forecasting dashboard designed to provide high-precision estimates of photovoltaic yield. By combining real-time meteorological data with fundamental solar geometry and atmospheric physics models, the application delivers actionable insights for solar energy management.

---

## 🚀 Features

*   **7-Day Energy Forecast:** Interactive dashboards showing hourly and daily solar radiation trends.
*   **Physics-Driven Modeling:** Implements the Hottel model for clear-sky transmittance and Spencer/Cooper equations for precise solar positioning.
*   **Real-Time API Integration:** Fetches localized weather data—including cloud cover, temperature, and irradiance—via the Open-Meteo API.
*   **Interactive Geospatial Analysis:** Built-in map component to select specific coordinates for localized yield simulations.
*   **Professional UI:** A sleek "glassmorphism" inspired interface with amber accents, optimized for technical clarity.

---

## 🛠️ Technical Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.x |
| **Web Framework** | Streamlit |
| **Data Science** | Pandas, NumPy |
| **Visualization** | Plotly, Folium |
| **Data Source** | Open-Meteo API |

---

## 📋 Theoretical Foundation

The application calculates the expected power output based on several critical parameters:

1.  **Solar Geometry:** Calculation of the declination angle and solar hour angle to determine the sun's position.
2.  **Atmospheric Attenuation:** Use of the Hottel model to estimate solar radiation reaching the surface.
3.  **Efficiency Losses:** Accounting for panel orientation, tilt, and environmental factors.

---

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/abderrahman7/solycast.git](https://github.com/abderrahman7/solycast.git)
   cd solycast
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
3. **Run the application:**
   ```bash
   streamlit run app.py
---

### 📊 Usage


*   **Location Input:** Input specific coordinates or use the interactive map to select your site.
*   **Parameter Tuning:** Adjust the installation's tilt angle, orientation, and peak power capacity.
*   **Data Visualization:** Analyze the forecasted 7-day yield and annual simulation estimates through interactive plots.

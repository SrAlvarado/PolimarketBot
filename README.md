# PolyBot AI 🚀

PolyBot AI es un bot autónomo de Paper Trading diseñado para operar en **Polymarket** utilizando **Google Gemini** como analista de riesgos.

## Características

- 🧠 **Cerebro Inteligente (Gemini)**: Analiza mercados y toma decisiones basadas en riesgo/beneficio.
- 📊 **Paper Trading**: Comienza con $1,000 USD virtuales y simula inversiones reales sin arriesgar dinero.
- 💼 **Gestor de Cartera**: Base de datos SQLite local (`cartera.db`) para registrar saldo, historial y PnL de forma segura.
- 🔄 **Totalmente Autónomo**: Busca mercados, evalúa opciones y comprueba resultados en un ciclo infinito.

## Requisitos Previos

- Python 3.8+
- Una API Key de Google Gemini. Consíguela gratis en [Google AI Studio](https://aistudio.google.com/app/apikey).

## Instalación y Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/SrAlvarado/PolimarketBot.git
   cd PolimarketBot
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la API Key**
   Copia el archivo de ejemplo y añade tu API Key:
   ```bash
   cp .env.example .env
   # Edita el archivo .env y añade tu GEMINI_API_KEY
   ```

## Ejecución

Para iniciar el bot, simplemente ejecuta:
```bash
python main.py
```

El bot inicializará la base de datos, te otorgará tus $1000 iniciales, y empezará a escanear los mercados activos.

## Landing Page

Puedes abrir `landing/index.html` en tu navegador para ver la página de presentación del proyecto.

## Arquitectura

- `main.py`: Bucle principal de ejecución.
- `portfolio.py`: Gestión de base de datos SQLite y saldo.
- `market_api.py`: Integración con la Gamma API de Polymarket.
- `brain.py`: Integración con Google Generative AI (Gemini).

---
*Disclaimer: Este bot es un simulador de inversiones (Paper Trading) con fines educativos. No invierte dinero real.*

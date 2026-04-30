import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configurar API Key
api_key = os.environ.get("GEMINI_API_KEY")

def analyze_markets(portfolio_balance, markets_data, performance_history=""):
    """
    Envía los mercados activos, el balance actual y el historial de rendimiento a Gemini para que tome una decisión de inversión.
    """
    if not api_key:
        print("Error: GEMINI_API_KEY no encontrada en variables de entorno o archivo .env")
        return []

    client = genai.Client(api_key=api_key)

    system_prompt = f"""
    Actúa como un Analista de Riesgos Cuantitativo para un bot de Paper Trading.
    Tienes un saldo disponible y una lista de mercados activos de Polymarket con sus probabilidades actuales (bestBid/bestAsk).
    Tu objetivo es analizar los mercados y elegir en cuáles invertir, buscando maximizar el retorno esperado (PnL).
    
    HISTORIAL DE RENDIMIENTO (Feedback Loop):
    Aquí tienes el resultado de tus últimas decisiones:
    {performance_history}
    
    Aprende de este historial. Si estás perdiendo, vuelve tu estrategia más conservadora o busca mercados con mayor volumen/probabilidad. Si estás ganando, mantén o ajusta el riesgo.
    También puedes decidir no invertir en un mercado si el riesgo es alto o la probabilidad no justifica el pago.
    No inviertas más del 20% del balance total en una sola iteración para diversificar.
    
    RESPONDE ESTRICTAMENTE EN FORMATO JSON. No incluyas explicaciones fuera del JSON, no uses bloques de código markdown (```json).
    Solo devuelve un array de objetos JSON con esta estructura exacta para cada decisión de inversión que tomes:
    [
        {{
            "mercado_id": "ID_DEL_MERCADO",
            "decision": "Yes", // o "No"
            "cantidad_usd_a_invertir": 10.5,
            "razonamiento_breve": "Breve justificación de la decisión, mencionando cómo el historial afectó la elección"
        }}
    ]
    Si decides no invertir en ninguno, devuelve un array vacío: []
    """

    user_prompt = f"""
    Balance de cartera disponible: ${portfolio_balance:.2f} USD
    
    Mercados disponibles para analizar:
    {json.dumps(markets_data, indent=2)}
    
    Recuerda: Responde SOLO con el array JSON crudo.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt + "\n\n" + user_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        # El SDK de python no asegura JSON estricto sin el mimetype, así que limpiamos posibles bloques markdown
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
            
        result = json.loads(text.strip())
        return result
    except json.JSONDecodeError as e:
        print(f"Error parseando respuesta de Gemini (no es JSON válido): {e}")
        return []
    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            print("INFO: La API de Gemini está saturada temporalmente (503). Reintentando en el próximo ciclo.")
        else:
            print(f"Error consultando a Gemini: {e}")
        return []

if __name__ == "__main__":
    # Test simple
    test_markets = [
        {
            "market_id": "123",
            "title": "Will AI take over the world by 2030?",
            "outcomes": ["Yes", "No"],
            "bestBid": 0.45,
            "bestAsk": 0.46,
            "volume": 100000
        }
    ]
    if api_key:
        res = analyze_markets(1000.0, test_markets, "Sin historial todavía.")
        print("Gemini decision:", json.dumps(res, indent=2))
    else:
        print("Setea GEMINI_API_KEY en .env para probar.")

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configurar API Key
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_markets(portfolio_balance, markets_data):
    """
    Envía los mercados activos y el balance actual a Gemini para que tome una decisión de inversión.
    """
    if not api_key:
        print("Error: GEMINI_API_KEY no encontrada en variables de entorno o archivo .env")
        return []

    system_prompt = """
    Actúa como un Analista de Riesgos Cuantitativo para un bot de Paper Trading.
    Tienes un saldo disponible y una lista de mercados activos de Polymarket con sus probabilidades actuales (bestBid/bestAsk).
    Tu objetivo es analizar los mercados y elegir en cuáles invertir, buscando maximizar el retorno esperado (PnL).
    También puedes decidir no invertir en un mercado si el riesgo es alto o la probabilidad no justifica el pago.
    No inviertas más del 20% del balance total en una sola iteración para diversificar.
    
    RESPONDE ESTRICTAMENTE EN FORMATO JSON. No incluyas explicaciones fuera del JSON, no uses bloques de código markdown (```json).
    Solo devuelve un array de objetos JSON con esta estructura exacta para cada decisión de inversión que tomes:
    [
        {
            "mercado_id": "ID_DEL_MERCADO",
            "decision": "Yes", // o "No"
            "cantidad_usd_a_invertir": 10.5,
            "razonamiento_breve": "Breve justificación de la decisión"
        }
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
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            system_prompt + "\n\n" + user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        # El SDK de python y mime_type nos aseguran que será JSON
        result = json.loads(response.text)
        return result
    except json.JSONDecodeError as e:
        print(f"Error parseando respuesta de Gemini (no es JSON válido): {e}")
        return []
    except Exception as e:
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
    if os.environ.get("GEMINI_API_KEY"):
        res = analyze_markets(1000.0, test_markets)
        print("Gemini decision:", json.dumps(res, indent=2))
    else:
        print("Setea GEMINI_API_KEY en .env para probar.")

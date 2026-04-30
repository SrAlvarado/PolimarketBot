import time
import os
from colorama import init, Fore, Style
import portfolio
import market_api
import brain

# Inicializar colorama para Windows
init()

def print_info(msg):
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {msg}")

def print_success(msg):
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {msg}")

def print_warning(msg):
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {msg}")

def print_error(msg):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

def run_cycle():
    print("\n" + "="*50)
    print_info("Iniciando nuevo ciclo de evaluación...")
    
    # 1. Revisar resoluciones pasadas (Mercados abiertos)
    open_positions = portfolio.get_open_positions()
    if open_positions:
        print_info(f"Revisando {len(open_positions)} posiciones abiertas...")
        for pos in open_positions:
            closed, winner = market_api.check_market_status(pos['market_id'])
            if closed:
                won = (winner == pos['decision'])
                payout, pnl = portfolio.close_position(pos['id'], won)
                
                if won:
                    portfolio.update_balance(payout) # Sumar el premio
                    print_success(f"¡Ganamos! Mercado '{pos['market_title']}' resolvió a {winner}. PnL: +${pnl:.2f}")
                else:
                    print_error(f"Perdimos. Mercado '{pos['market_title']}' resolvió a {winner}. PnL: ${pnl:.2f}")
    
    # 2. Ver saldo
    balance = portfolio.get_balance()
    total_pnl = portfolio.get_total_pnl()
    
    color_pnl = Fore.GREEN if total_pnl >= 0 else Fore.RED
    print(f"{Style.BRIGHT}>> Saldo Actual: ${balance:.2f} USD | PnL Histórico: {color_pnl}${total_pnl:.2f} USD{Style.RESET_ALL}")
    
    # Si no hay saldo, no podemos invertir
    if balance <= 0:
        print_error("Saldo insuficiente para invertir. Saliendo del ciclo.")
        return
        
    # 3. Buscar nuevos mercados
    print_info("Buscando mercados activos populares...")
    markets = market_api.get_active_markets(limit=5)
    
    if not markets:
        print_warning("No se encontraron mercados activos o hubo un error en la API.")
        return
        
    # 4. Consultar a Gemini (Feedback Loop)
    print_info("Consultando al cerebro (Gemini)...")
    performance_history = portfolio.get_recent_performance(limit=5)
    decisions = brain.analyze_markets(balance, markets, performance_history)
    
    if not decisions:
        print_info("Gemini decidió no invertir en ningún mercado en este ciclo o hubo un error.")
        return
        
    # 5. Ejecutar orden virtual
    for decision in decisions:
        market_id = decision.get("mercado_id")
        choice = decision.get("decision")
        amount = decision.get("cantidad_usd_a_invertir", 0)
        reasoning = decision.get("razonamiento_breve", "Sin justificación")
        
        if amount <= 0 or amount > balance:
            print_warning(f"Cantidad a invertir inválida (${amount}) para el mercado {market_id}. Saltando.")
            continue
            
        # Buscar el mercado en la lista obtenida para sacar titulo y precios
        market_data = next((m for m in markets if m["market_id"] == market_id), None)
        if not market_data:
            print_warning(f"Mercado {market_id} devuelto por Gemini no está en la lista actual. Saltando.")
            continue
            
        # Calcular el precio de la opción
        # Si la decisión es el primer outcome ("Yes"), usamos el precio de Yes (usualmente bestAsk).
        # En Polymarket Gamma API el precio es complejo de inferir solo con bestBid/bestAsk sin saber qué lado es.
        # Asumiremos un precio de 0.50 para simplificar si no podemos mapearlo, o usamos el promedio de bestBid/bestAsk.
        price = (market_data['bestBid'] + market_data['bestAsk']) / 2
        if price <= 0:
            price = 0.5
            
        shares = amount / price
        
        # Ejecutar compra virtual
        portfolio.record_trade(
            market_id=market_id,
            market_title=market_data['title'],
            decision=choice,
            invested_usd=amount,
            shares=shares
        )
        portfolio.update_balance(-amount) # Restar el dinero invertido
        balance -= amount # Actualizar variable local
        
        print_success(f"Inversión Ejecutada: ${amount:.2f} en '{market_data['title']}' (Decisión: {choice})")
        print(f"   {Fore.YELLOW}Justificación IA:{Style.RESET_ALL} {reasoning}")
        
    print_info("Ciclo finalizado con éxito.")

if __name__ == "__main__":
    print(f"{Style.BRIGHT}{Fore.MAGENTA}=== Polymarket Paper Trading Bot ==={Style.RESET_ALL}")
    
    # Inicializar BD
    portfolio.init_db()
    
    # Comprobar API Key
    if not os.environ.get("GEMINI_API_KEY"):
        print_error("GEMINI_API_KEY no encontrada.")
        print_info("Por favor, copia '.env.example' a '.env' y añade tu API Key.")
        exit(1)
        
    # Bucle principal
    while True:
        try:
            run_cycle()
            # Esperar 60 segundos para el próximo ciclo
            sleep_time = 60
            print_info(f"Esperando {sleep_time} segundos para el próximo ciclo...")
            time.sleep(sleep_time)
        except KeyboardInterrupt:
            print_info("\nBot detenido manualmente por el usuario.")
            break
        except Exception as e:
            print_error(f"Error inesperado en el ciclo principal: {e}")
            print_info("Esperando 60 segundos antes de reintentar...")
            time.sleep(60)

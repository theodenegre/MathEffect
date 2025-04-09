import numpy as np
import time

# Données de marché réelles (fictives pour cet exemple)
market_prices_a = [100, 102, 101, 103, 104]
market_prices_v = [101, 103, 102, 104, 105]

# Initialisation des paramètres
n_bots = 10
m_humans = 10
iterations = len(market_prices_a)

# Fonction de profit
def profit(p_a, p_v, q):
    return (p_v - p_a) * q

# Fonction pour calculer l'équilibre de Nash (approche avancée)
def nash_equilibrium(prices_a, prices_v, n_bots):
    # Matrices de payoffs pour les bots
    payoff_matrix_a = np.zeros((n_bots, len(prices_a)))
    payoff_matrix_v = np.zeros((n_bots, len(prices_v)))
    
    for i in range(n_bots):
        for j in range(len(prices_a)):
            payoff_matrix_a[i, j] = profit(prices_a[j], prices_v[j], 1)
            payoff_matrix_v[i, j] = profit(prices_v[j], prices_a[j], 1)
    
    # Calcul des meilleures réponses
    best_response_a = np.argmax(payoff_matrix_a, axis=1)
    best_response_v = np.argmax(payoff_matrix_v, axis=1)
    
    # Calcul des stratégies optimales
    optimal_price_a = np.mean([prices_a[br] for br in best_response_a])
    optimal_price_v = np.mean([prices_v[br] for br in best_response_v])
    
    return optimal_price_a, optimal_price_v

# Simulation du marché
def simulate_market(n_bots, m_humans, iterations, market_prices_a, market_prices_v):
    bot_profits = np.zeros(n_bots)
    human_profits = np.zeros(m_humans)
    bot_times = []
    human_times = []
    
    for t in range(iterations):
        # Bots calculent les prix optimaux en utilisant l'équilibre de Nash
        start_time = time.time()
        bot_prices_a = np.zeros(n_bots)
        bot_prices_v = np.zeros(n_bots)
        for i in range(n_bots):
            bot_prices_a[i], bot_prices_v[i] = nash_equilibrium(market_prices_a, market_prices_v, n_bots)
        bot_times.append(time.time() - start_time)
        
        # Humains ajustent leurs prix en fonction des données de marché réelles
        start_time = time.time()
        human_prices_a = np.array([market_prices_a[t]] * m_humans)
        human_prices_v = np.array([market_prices_v[t]] * m_humans)
        human_times.append(time.time() - start_time)
        
        # Exécution des transactions et calcul des profits
        for i in range(n_bots):
            q = np.random.randint(1, 100)
            bot_profits[i] += profit(bot_prices_a[i], bot_prices_v[i], q)
        
        for j in range(m_humans):
            q = np.random.randint(1, 100)
            human_profits[j] += profit(human_prices_a[j], human_prices_v[j], q)
    
    return bot_profits, human_profits, bot_times, human_times

# Exécution de la simulation
bot_profits, human_profits, bot_times, human_times = simulate_market(n_bots, m_humans, iterations, market_prices_a, market_prices_v)

# Affichage des résultats
print("Profit total des bots:", np.sum(bot_profits))
print("Profit total des humains:", np.sum(human_profits))
print("Temps moyen d'exécution des bots:", np.mean(bot_times))
print("Temps moyen d'exécution des humains:", np.mean(human_times))
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# Définition des transactions avec dates d'achat et de vente
transactions = [
    # Semaine 1
    {"ticker": "SHOP", "achat": "2025-10-06", "vente": "2025-10-08", "montant": 1000},
    {"ticker": "UPST", "achat": "2025-10-06", "vente": "2025-10-06", "montant": 1000},
    {"ticker": "PLTR", "achat": "2025-10-07", "vente": "2025-10-07", "montant": 1000},
    {"ticker": "DIS", "achat": "2025-10-07", "vente": "2025-10-09", "montant": 1000},
    {"ticker": "AMD", "achat": "2025-10-07", "vente": "2025-10-17", "montant": 1000},
    {"ticker": "DAL", "achat": "2025-10-07", "vente": "2025-10-09", "montant": 1000},
    {"ticker": "NFLX", "achat": "2025-10-07", "vente": "2025-10-13", "montant": 1000},
    {"ticker": "COIN", "achat": "2025-10-07", "vente": "2025-10-15", "montant": 1000},
    {"ticker": "RIOT", "achat": "2025-10-09", "vente": "2025-10-10", "montant": 1000},

    # Semaine 2
    {"ticker": "NVDA", "achat": "2025-10-13", "vente": "2025-10-15", "montant": 1000},
    {"ticker": "PLTR", "achat": "2025-10-13", "vente": "2025-10-13", "montant": 1000},  # 2ème trade
    {"ticker": "MSFT", "achat": "2025-10-13", "vente": "2025-10-13", "montant": 1000},
    {"ticker": "META", "achat": "2025-10-14", "vente": "2025-10-14", "montant": 1000},  # MTA = META
    {"ticker": "CRWD", "achat": "2025-10-16", "vente": "2025-10-17", "montant": 1000},
]

def get_stock_price(ticker, date):
    """Récupère le cours de clôture d'une action à une date donnée"""
    try:
        # Télécharger les données pour la période (avec marge pour gérer les weekends)
        start = datetime.strptime(date, "%Y-%m-%d") - timedelta(days=5)
        end = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=5)

        stock = yf.Ticker(ticker)
        hist = stock.history(start=start, end=end)

        if hist.empty:
            return None

        # Convertir l'index en timezone-naive pour éviter les erreurs de comparaison
        hist.index = hist.index.tz_localize(None)

        # Chercher la date exacte ou la plus proche
        target_date = pd.Timestamp(date)
        if target_date in hist.index:
            return hist.loc[target_date]['Close']
        else:
            # Prendre la date la plus proche (jour de bourse suivant)
            valid_dates = hist.index[hist.index >= target_date]
            if len(valid_dates) > 0:
                return hist.loc[valid_dates[0]]['Close']
            else:
                return hist.iloc[-1]['Close']
    except Exception as e:
        print(f"Erreur pour {ticker} à la date {date}: {e}")
        return None

# Calcul des résultats
resultats = []
total_gain = 0
total_investissement = 0

print("=" * 100)
print("ANALYSE DES TRANSACTIONS")
print("=" * 100)

for i, trade in enumerate(transactions, 1):
    ticker = trade["ticker"]
    date_achat = trade["achat"]
    date_vente = trade["vente"]
    montant = trade["montant"]

    # Récupérer les cours
    prix_achat = get_stock_price(ticker, date_achat)
    prix_vente = get_stock_price(ticker, date_vente)

    if prix_achat and prix_vente:
        # Calculer le nombre d'actions achetées
        nb_actions = montant / prix_achat

        # Calculer la valeur à la vente
        valeur_vente = nb_actions * prix_vente

        # Calculer le gain/perte
        gain = valeur_vente - montant
        pourcentage = (gain / montant) * 100

        resultats.append({
            "Ticker": ticker,
            "Date Achat": date_achat,
            "Prix Achat": prix_achat,
            "Date Vente": date_vente,
            "Prix Vente": prix_vente,
            "Actions": nb_actions,
            "Gain/Perte (€)": gain,
            "% Gain": pourcentage
        })

        total_gain += gain
        total_investissement += montant

        statut = "✅ GAIN" if gain >= 0 else "❌ PERTE"
        print(f"\n{i}. {ticker} {statut}")
        print(f"   Achat  : {date_achat} à {prix_achat:.2f}$ ({nb_actions:.4f} actions)")
        print(f"   Vente  : {date_vente} à {prix_vente:.2f}$")
        print(f"   Résultat: {gain:+.2f}€ ({pourcentage:+.2f}%)")
    else:
        print(f"\n{i}. {ticker} - ERREUR: Impossible de récupérer les cours")

# Affichage du résumé
print("\n" + "=" * 100)
print("RÉSUMÉ GLOBAL")
print("=" * 100)
print(f"Nombre de transactions : {len(transactions)}")
print(f"Investissement total   : {total_investissement:.2f}€")
print(f"Gain/Perte total       : {total_gain:+.2f}€")
print(f"Rendement              : {(total_gain/total_investissement)*100:+.2f}%")

# Créer un DataFrame pour export
df = pd.DataFrame(resultats)
if not df.empty:
    print("\n" + "=" * 100)
    print("TABLEAU DÉTAILLÉ")
    print("=" * 100)
    print(df.to_string(index=False))

    # Export CSV (optionnel)
    df.to_csv("resultats_trading.csv", index=False, encoding='utf-8')
    print("\n✅ Résultats exportés dans 'resultats_trading.csv'")

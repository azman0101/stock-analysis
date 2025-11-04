import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# Date d'évaluation : 05/11/2025
DATE_EVALUATION = "2025-11-05"

# Définition des achats (sans vente, position conservée)
achats = [
    {"ticker": "SHOP", "date_achat": "2025-10-06", "montant": 1000},
    {"ticker": "UPST", "date_achat": "2025-10-06", "montant": 1000},
    {"ticker": "PLTR", "date_achat": "2025-10-07", "montant": 1000},
    {"ticker": "DIS", "date_achat": "2025-10-07", "montant": 1000},
    {"ticker": "AMD", "date_achat": "2025-10-07", "montant": 1000},
    {"ticker": "DAL", "date_achat": "2025-10-07", "montant": 1000},
    {"ticker": "NFLX", "date_achat": "2025-10-07", "montant": 1000},
    {"ticker": "COIN", "date_achat": "2025-10-07", "montant": 1000},
    {"ticker": "RIOT", "date_achat": "2025-10-09", "montant": 1000},
    {"ticker": "NVDA", "date_achat": "2025-10-13", "montant": 1000},
    {"ticker": "PLTR", "date_achat": "2025-10-13", "montant": 1000},  # 2ème position
    {"ticker": "MSFT", "date_achat": "2025-10-13", "montant": 1000},
    {"ticker": "META", "date_achat": "2025-10-14", "montant": 1000},
    {"ticker": "CRWD", "date_achat": "2025-10-16", "montant": 1000},
]

def get_stock_price(ticker, date):
    """Récupère le cours de clôture d'une action à une date donnée"""
    try:
        # Télécharger les données avec marge pour gérer les weekends
        start = datetime.strptime(date, "%Y-%m-%d") - timedelta(days=5)
        end = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=5)
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start, end=end)
        
        if hist.empty:
            return None
        
        # Normaliser l'index pour éviter les problèmes de timezone
        hist.index = hist.index.tz_localize(None)
        
        # Chercher la date exacte ou la plus proche
        target_date = pd.Timestamp(date).tz_localize(None)
        if target_date in hist.index:
            return hist.loc[target_date]['Close']
        else:
            # Prendre le jour de bourse le plus proche
            valid_dates = hist.index[hist.index >= target_date]
            if len(valid_dates) > 0:
                return hist.loc[valid_dates[0]]['Close']
            else:
                return hist.iloc[-1]['Close']
    except Exception as e:
        print(f"⚠️  Erreur pour {ticker} à la date {date}: {e}")
        return None

# Regrouper les achats par ticker pour gérer les positions multiples
positions_par_ticker = {}
for achat in achats:
    ticker = achat["ticker"]
    if ticker not in positions_par_ticker:
        positions_par_ticker[ticker] = []
    positions_par_ticker[ticker].append(achat)

# Calcul des résultats
resultats = []
total_investi = 0
total_valeur_actuelle = 0
total_plus_value = 0

print("=" * 120)
print("ANALYSE DES POSITIONS (ACHAT ET CONSERVATION)")
print(f"Date d'évaluation : {DATE_EVALUATION}")
print("=" * 120)

position_num = 1
for ticker, positions in positions_par_ticker.items():
    print(f"\n{'─' * 120}")
    print(f"📊 {ticker} - {len(positions)} position(s)")
    print(f"{'─' * 120}")
    
    # Récupérer le prix actuel (au 05/11/2025)
    prix_actuel = get_stock_price(ticker, DATE_EVALUATION)
    
    if not prix_actuel:
        print(f"❌ Impossible de récupérer le prix actuel de {ticker}")
        continue
    
    ticker_investi = 0
    ticker_valeur = 0
    ticker_actions = 0
    
    for i, position in enumerate(positions, 1):
        date_achat = position["date_achat"]
        montant = position["montant"]
        
        # Récupérer le prix d'achat
        prix_achat = get_stock_price(ticker, date_achat)
        
        if prix_achat:
            # Calculer le nombre d'actions achetées
            nb_actions = montant / prix_achat
            
            # Calculer la valeur actuelle de cette position
            valeur_actuelle = nb_actions * prix_actuel
            
            # Calculer la plus-value latente
            plus_value = valeur_actuelle - montant
            pourcentage = (plus_value / montant) * 100
            
            resultats.append({
                "Ticker": ticker,
                "Position": i if len(positions) > 1 else "-",
                "Date Achat": date_achat,
                "Prix Achat ($)": prix_achat,
                "Prix Actuel ($)": prix_actuel,
                "Actions": nb_actions,
                "Investi (€)": montant,
                "Valeur Actuelle (€)": valeur_actuelle,
                "Plus-Value (€)": plus_value,
                "% Gain": pourcentage
            })
            
            ticker_investi += montant
            ticker_valeur += valeur_actuelle
            ticker_actions += nb_actions
            
            statut = "📈 GAIN" if plus_value >= 0 else "📉 PERTE"
            position_label = f"Position #{i}" if len(positions) > 1 else "Position unique"
            
            print(f"\n   {position_label} {statut}")
            print(f"   ├─ Date achat    : {date_achat}")
            print(f"   ├─ Prix achat    : {prix_achat:.2f}$")
            print(f"   ├─ Actions       : {nb_actions:.4f}")
            print(f"   ├─ Investi       : {montant:.2f}€")
            print(f"   ├─ Valeur actuelle: {valeur_actuelle:.2f}€")
            print(f"   └─ Plus-value    : {plus_value:+.2f}€ ({pourcentage:+.2f}%)")
        else:
            print(f"   ❌ Position #{i} - Impossible de récupérer le prix d'achat")
    
    # Résumé par ticker
    if ticker_investi > 0:
        ticker_plus_value = ticker_valeur - ticker_investi
        ticker_perf = (ticker_plus_value / ticker_investi) * 100
        
        print(f"\n   {'─' * 100}")
        print(f"   💼 TOTAL {ticker}")
        print(f"   ├─ Positions     : {len(positions)}")
        print(f"   ├─ Actions total : {ticker_actions:.4f}")
        print(f"   ├─ Investi       : {ticker_investi:.2f}€")
        print(f"   ├─ Valeur actuelle: {ticker_valeur:.2f}€")
        print(f"   └─ Plus-value    : {ticker_plus_value:+.2f}€ ({ticker_perf:+.2f}%)")
        
        total_investi += ticker_investi
        total_valeur_actuelle += ticker_valeur
        total_plus_value += ticker_plus_value

# Affichage du résumé global
print("\n\n" + "=" * 120)
print("📊 RÉSUMÉ GLOBAL DU PORTEFEUILLE")
print("=" * 120)
print(f"Date d'évaluation      : {DATE_EVALUATION}")
print(f"Nombre de tickers      : {len(positions_par_ticker)}")
print(f"Nombre total d'achats  : {len(achats)}")
print(f"Investissement total   : {total_investi:.2f}€")
print(f"Valeur actuelle        : {total_valeur_actuelle:.2f}€")
print(f"Plus-value latente     : {total_plus_value:+.2f}€")

if total_investi > 0:
    rendement_global = (total_plus_value / total_investi) * 100
    print(f"Rendement global       : {rendement_global:+.2f}%")

# Créer un DataFrame pour export
df = pd.DataFrame(resultats)
if not df.empty:
    print("\n" + "=" * 120)
    print("📋 TABLEAU DÉTAILLÉ DE TOUTES LES POSITIONS")
    print("=" * 120)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    print(df.to_string(index=False))
    
    # Statistiques supplémentaires
    print("\n" + "=" * 120)
    print("📈 STATISTIQUES")
    print("=" * 120)
    gains = df[df['Plus-Value (€)'] > 0]
    pertes = df[df['Plus-Value (€)'] < 0]
    
    print(f"Positions gagnantes    : {len(gains)} ({len(gains)/len(df)*100:.1f}%)")
    print(f"Positions perdantes    : {len(pertes)} ({len(pertes)/len(df)*100:.1f}%)")
    
    if len(gains) > 0:
        print(f"Gain moyen             : +{gains['Plus-Value (€)'].mean():.2f}€")
        print(f"Meilleur gain          : +{gains['Plus-Value (€)'].max():.2f}€ ({gains.loc[gains['Plus-Value (€)'].idxmax(), 'Ticker']})")
    
    if len(pertes) > 0:
        print(f"Perte moyenne          : {pertes['Plus-Value (€)'].mean():.2f}€")
        print(f"Pire perte             : {pertes['Plus-Value (€)'].min():.2f}€ ({pertes.loc[pertes['Plus-Value (€)'].idxmin(), 'Ticker']})")
    
    # Export CSV
    df.to_csv("positions_latentes.csv", index=False, encoding='utf-8')
    print("\n✅ Résultats exportés dans 'positions_latentes.csv'")

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import pytz

# Date d'évaluation : 05/11/2025
DATE_EVALUATION = "2025-11-05"

# Timezone du marché US (NYSE/NASDAQ)
US_EASTERN = pytz.timezone('America/New_York')

# Définition des achats (sans vente, position conservée)
# Achat effectué 2h après l'ouverture du marché (9h30 ET + 2h = 11h30 ET)
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

def get_stock_price_intraday(ticker, date, hours_after_open=2):
    """
    Récupère le cours d'une action 2h après l'ouverture du marché
    Marché US : ouverture à 9h30 ET, donc achat à 11h30 ET
    """
    try:
        # Convertir la date en datetime avec heure d'achat (11h30 ET)
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        # Heure d'achat : 9h30 + 2h = 11h30 ET
        purchase_time = date_obj.replace(hour=9+hours_after_open, minute=30)
        purchase_time_et = US_EASTERN.localize(purchase_time)
        
        # Télécharger les données intraday (1 minute) pour ce jour
        stock = yf.Ticker(ticker)
        
        # Essayer d'abord avec les données intraday
        start = date_obj
        end = date_obj + timedelta(days=1)
        
        # Télécharger données avec interval de 5 minutes
        hist = stock.history(start=start, end=end, interval="5m")
        
        if not hist.empty:
            # Normaliser l'index
            hist.index = hist.index.tz_convert(US_EASTERN)
            
            # Chercher le cours le plus proche de 11h30 ET
            target_time = purchase_time_et
            
            # Filtrer les données autour de 11h30 (entre 11h00 et 12h00)
            morning_data = hist[
                (hist.index.hour >= 11) & (hist.index.hour <= 12)
            ]
            
            if not morning_data.empty:
                # Prendre le cours le plus proche de 11h30
                closest_idx = morning_data.index[0]
                for idx in morning_data.index:
                    if abs((idx - target_time).total_seconds()) < abs((closest_idx - target_time).total_seconds()):
                        closest_idx = idx
                
                price = morning_data.loc[closest_idx]['Close']
                actual_time = closest_idx.strftime('%H:%M ET')
                return price, actual_time
        
        # Si pas de données intraday, utiliser le prix d'ouverture + moyenne open/high
        hist_daily = stock.history(start=start, end=end, interval="1d")
        if not hist_daily.empty:
            hist_daily.index = hist_daily.index.tz_localize(None)
            open_price = hist_daily.iloc[0]['Open']
            high_price = hist_daily.iloc[0]['High']
            # Approximation : prix 2h après ouverture ≈ (open + high) / 2
            estimated_price = (open_price + high_price) / 2
            return estimated_price, "~11:30 ET (estimé)"
        
        return None, None
        
    except Exception as e:
        print(f"⚠️  Erreur pour {ticker} à la date {date}: {e}")
        return None, None

def get_current_price(ticker, date):
    """Récupère le cours de clôture actuel"""
    try:
        start = datetime.strptime(date, "%Y-%m-%d") - timedelta(days=5)
        end = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=5)
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start, end=end)
        
        if hist.empty:
            return None
        
        # Normaliser l'index
        hist.index = hist.index.tz_localize(None)
        target_date = pd.Timestamp(date).tz_localize(None)
        
        if target_date in hist.index:
            return hist.loc[target_date]['Close']
        else:
            valid_dates = hist.index[hist.index >= target_date]
            if len(valid_dates) > 0:
                return hist.loc[valid_dates[0]]['Close']
            else:
                return hist.iloc[-1]['Close']
    except Exception as e:
        print(f"⚠️  Erreur pour {ticker} prix actuel: {e}")
        return None

# Regrouper les achats par ticker
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

print("=" * 130)
print("ANALYSE DES POSITIONS - ACHAT 2H APRÈS OUVERTURE DU MARCHÉ (11h30 ET)")
print(f"Date d'évaluation : {DATE_EVALUATION}")
print("=" * 130)
print("ℹ️  Marché US : Ouverture 9h30 ET → Achat à 11h30 ET (2h après ouverture)")
print("=" * 130)

position_num = 1
for ticker, positions in positions_par_ticker.items():
    print(f"\n{'─' * 130}")
    print(f"ð{ticker} - {len(positions)} position(s)")
    print(f"{'─' * 130}")
    
    # Récupérer le prix actuel (au 05/11/2025)
    prix_actuel = get_current_price(ticker, DATE_EVALUATION)
    
    if not prix_actuel:
        print(f"❌ Impossible de récupérer le prix actuel de {ticker}")
        continue
    
    ticker_investi = 0
    ticker_valeur = 0
    ticker_actions = 0
    
    for i, position in enumerate(positions, 1):
        date_achat = position["date_achat"]
        montant = position["montant"]
        
        # Récupérer le prix d'achat 2h après ouverture
        prix_achat, heure_achat = get_stock_price_intraday(ticker, date_achat, hours_after_open=2)
        
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
                "Heure Achat": heure_achat,
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
            
            statut = "ðGAIN" if plus_value >= 0 else "ðPERTE"
            position_label = f"Position #{i}" if len(positions) > 1 else "Position unique"
            
            print(f"\n   {position_label} {statut}")
            print(f"   ├─ Date achat    : {date_achat} à {heure_achat}")
            print(f"   ├─ Prix achat    : {prix_achat:.2f}$ (2h après ouverture)")
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
        
        print(f"\n   {'─' * 110}")
        print(f"   ðTOTAL {ticker}")
        print(f"   ├─ Positions     : {len(positions)}")
        print(f"   ├─ Actions total : {ticker_actions:.4f}")
        print(f"   ├─ Investi       : {ticker_investi:.2f}€")
        print(f"   ├─ Valeur actuelle: {ticker_valeur:.2f}€")
        print(f"   └─ Plus-value    : {ticker_plus_value:+.2f}€ ({ticker_perf:+.2f}%)")
        
        total_investi += ticker_investi
        total_valeur_actuelle += ticker_valeur
        total_plus_value += ticker_plus_value

# Affichage du résumé global
print("\n\n" + "=" * 130)
print("ðRÉSUMÉ GLOBAL DU PORTEFEUILLE")
print("=" * 130)
print(f"Stratégie              : Achat 2h après ouverture (11h30 ET)")
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
    print("\n" + "=" * 130)
    print("ðTABLEAU DÉTAILLÉ DE TOUTES LES POSITIONS")
    print("=" * 130)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 130)
    print(df.to_string(index=False))
    
    # Statistiques supplémentaires
    print("\n" + "=" * 130)
    print("ðSTATISTIQUES")
    print("=" * 130)
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
    df.to_csv("positions_intraday_11h30.csv", index=False, encoding='utf-8')
    print("\n✅ Résultats exportés dans 'positions_intraday_11h30.csv'")

print("\n" + "=" * 130)
print("ℹ️  NOTE : Les prix intraday sont récupérés avec un intervalle de 5 minutes")
print("         Si les données intraday ne sont pas disponibles, une estimation est utilisée")
print("=" * 130)

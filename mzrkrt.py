import yfinance as yf
import pandas as pd
from datetime import datetime

# Liste des tickers
tickers = ["SHOP", "UPST", "PLTR", "DIS", "AMD", "DAL", "NFLX", "COIN", "RIOT", "NVDA", "MSFT", "META", "CRWD"]

# Supprimer les doublons
tickers_uniques = list(set(tickers))
tickers_uniques.sort()

print("=" * 120)
print("📊 INFORMATIONS SUR LES MARCHÉS ET HORAIRES DE COTATION")
print("=" * 120)

resultats = []

for ticker in tickers_uniques:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Récupérer les informations principales
        nom_complet = info.get('longName', 'N/A')
        exchange = info.get('exchange', 'N/A')
        timezone = info.get('timeZoneFullName', 'N/A')
        pays = info.get('country', 'N/A')
        secteur = info.get('sector', 'N/A')
        industrie = info.get('industry', 'N/A')
        currency = info.get('currency', 'N/A')
        
        resultats.append({
            'Ticker': ticker,
            'Nom': nom_complet,
            'Marché': exchange,
            'Pays': pays,
            'Timezone': timezone,
            'Devise': currency,
            'Secteur': secteur,
            'Industrie': industrie
        })
        
        print(f"\n{'─' * 120}")
        print(f"🏢 {ticker} - {nom_complet}")
        print(f"{'─' * 120}")
        print(f"   📍 Marché (Exchange)  : {exchange}")
        print(f"   🌍 Pays               : {pays}")
        print(f"   🕐 Timezone           : {timezone}")
        print(f"   💱 Devise             : {currency}")
        print(f"   🏭 Secteur            : {secteur}")
        print(f"   🔧 Industrie          : {industrie}")
        
    except Exception as e:
        print(f"\n❌ Erreur pour {ticker}: {e}")
        resultats.append({
            'Ticker': ticker,
            'Nom': 'Erreur',
            'Marché': 'N/A',
            'Pays': 'N/A',
            'Timezone': 'N/A',
            'Devise': 'N/A',
            'Secteur': 'N/A',
            'Industrie': 'N/A'
        })

# Créer un DataFrame
df = pd.DataFrame(resultats)

# Résumé par marché
print("\n\n" + "=" * 120)
print("📊 RÉSUMÉ PAR MARCHÉ")
print("=" * 120)

if not df.empty:
    marches = df['Marché'].value_counts()
    print("\nNombre d'actions par marché :")
    for marche, count in marches.items():
        print(f"   • {marche}: {count} action(s)")
    
    print("\n" + "─" * 120)
    print("🕐 HORAIRES DE TRADING (Heure de New York - ET)")
    print("─" * 120)
    print("   📈 Marché principal: NYSE / NASDAQ")
    print("   ├─ Pré-marché     : 04:00 - 09:30 ET")
    print("   ├─ Session régulière: 09:30 - 16:00 ET")
    print("   └─ Après-marché   : 16:00 - 20:00 ET")
    
    print("\n" + "─" * 120)
    print("🌍 CONVERSION HORAIRES (pour référence)")
    print("─" * 120)
    print("   • 09:30 ET = 15:30 CET (Paris)")
    print("   • 16:00 ET = 22:00 CET (Paris)")
    
    # Tableau détaillé
    print("\n\n" + "=" * 120)
    print("📋 TABLEAU DÉTAILLÉ")
    print("=" * 120)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 40)
    print(df.to_string(index=False))
    
    # Export CSV
    df.to_csv("marches_actions.csv", index=False, encoding='utf-8')
    print("\n✅ Informations exportées dans 'marches_actions.csv'")

# Information sur les cours utilisés
print("\n\n" + "=" * 120)
print("⚠️  INFORMATION IMPORTANTE SUR LES COURS UTILISÉS")
print("=" * 120)
print("""
Lorsque vous spécifiez une DATE sans HEURE précise, Yahoo Finance retourne :
   • Le cours de CLÔTURE (Close) de cette journée
   • Clôture = 16:00 ET (22:00 heure de Paris)

Pour un bot de trading qui achète pendant la journée :
   • Si achat à 10:00 ET → Utilisez des données intraday (1min, 5min, 1h)
   • Si achat à la clôture → Le cours de Close est correct
   • Si achat à l'ouverture → Utilisez le cours Open (09:30 ET)

💡 Recommandation : Vérifiez à quelle heure votre bot effectue les transactions !
""")

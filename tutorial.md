# 🚀 NutriScan - Schnellreferenz

## 📱 URLs

### Erste Nutzung
```
https://nutriscan.bergerhq.de/?token=sk-dein-key
```

### Wiederholte Nutzung
```
https://nutriscan.bergerhq.de/
```
*(Token bleibt in Session gespeichert)*

## ⚡ Wichtigste Befehle

| Aktion | Befehl |
|--------|--------|
| **App starten (lokal)** | `python app.py` |
| **Mit Token öffnen** | `/?token=sk-...` |
| **API Key holen** | https://platform.openai.com/api-keys |
| **Neuen Key generieren** | OpenAI Dashboard → "Create new secret key" |
| **Budget prüfen** | https://platform.openai.com/account/usage |

## 🔒 Sicherheit

| Feature | Wert | Beschreibung |
|---------|------|--------------|
| **Rate Limit** | 30 Sek | Max. 1 Anfrage pro Session |
| **Token-Speicherung** | Session | Verschlüsselter Cookie |
| **Max. Upload** | 16 MB | Maximale Bildgröße |
| **API Key Format** | `sk-...` | Muss mit "sk-" beginnen |

## 💰 Kosten

| Modell | Kosten/Bild | Empfehlung |
|--------|-------------|------------|
| **GPT-4o** | ~$0.005 | Beste Qualität |
| **GPT-4o-mini** | ~$0.0015 | Günstiger, schneller |

**Beispiel:** 100 Analysen/Monat = $0.50 (GPT-4o) oder $0.15 (GPT-4o-mini)

## 🎯 Workflow

```
1. App mit Token öffnen (nur 1x nötig)
2. Foto aufnehmen
3. Optional: Beschreibung
4. Analysieren (Wartezeit: ~5-10 Sek)
5. Ergebnis prüfen
6. Optional: Portion anpassen
7. Fertig!
```

**Wichtig:** Warte 30 Sekunden vor nächster Analyse!

## 📸 Foto-Tipps

| Kriterium | Empfehlung |
|-----------|------------|
| **Abstand** | 30-50 cm |
| **Winkel** | 45° von oben |
| **Licht** | Tageslicht oder hell |
| **Fokus** | Essen im Mittelpunkt |
| **Hintergrund** | Neutral, nicht ablenkend |

## ⚠️ Häufige Fehler

| Fehlermeldung | Bedeutung | Lösung |
|--------------|-----------|---------|
| "Kein API Token" | Token fehlt | `/?token=sk-...` hinzufügen |
| "Rate Limit erreicht" | Zu schnell | 30 Sekunden warten |
| "Ungültiger API Key" | Token falsch | Neuen Key erstellen |
| "Analyse fehlgeschlagen" | Bild/Netzwerk | Neues Foto oder später versuchen |

## 🔧 Konfiguration (app.py)

```python
# Rate Limit anpassen
RATE_LIMIT_SECONDS = 30  # Standard: 30

# Modell wechseln
model="gpt-4o"          # Beste Qualität
model="gpt-4o-mini"     # Günstiger

# Max. Upload-Größe
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

## 📱 iPhone Installation

```
1. Safari öffnen (WICHTIG: Nicht Chrome!)
2. Teilen-Button (↗️)
3. "Zum Home-Bildschirm"
4. "Hinzufügen"
5. Fertig! 🎉
```

## 🆘 Troubleshooting Quick Fixes

### Problem: Kamera funktioniert nicht
```
→ Nutze HTTPS-Version (nicht HTTP)
→ Oder: "Foto hochladen" Button nutzen
```

### Problem: Session verloren
```
→ Browser-Cache geleert?
→ Lösung: Token erneut via URL setzen
```

### Problem: Langsame Analyse
```
→ Bild zu groß? (Max 16MB)
→ Langsame Internet-Verbindung?
→ OpenAI Server überlastet? (selten)
```

## 📊 API Key Management

### Key erstellen
```
1. https://platform.openai.com/api-keys
2. "Create new secret key"
3. Name: "NutriScan"
4. Kopieren (wird nur 1x angezeigt!)
```

### Budget-Limit setzen
```
1. https://platform.openai.com/account/limits
2. Hard limit: $10/Monat
3. Soft limit: $5 (für Warnung)
4. Email-Benachrichtigung: An
```

### Key widerrufen
```
1. https://platform.openai.com/api-keys
2. Finde Key "NutriScan"
3. "Revoke" Button
4. Erstelle neuen Key
```

## 🔗 Wichtige Links

| Link | Zweck |
|------|-------|
| [OpenAI API Keys](https://platform.openai.com/api-keys) | Keys verwalten |
| [OpenAI Usage](https://platform.openai.com/account/usage) | Kosten prüfen |
| [OpenAI Limits](https://platform.openai.com/account/limits) | Budget setzen |
| [Render.com](https://render.com) | Deployment |
| [GitHub Repo](https://github.com/emaa10/nutriscan) | Source Code |


#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <algorithm> // Pour le calcul de la médiane

// ==========================================
// Constantes exigées en tête de fichier (B.3)
// ==========================================
#define HAUTEUR_INSTALL_CM 250
#define SEUIL_JAUNE_CM     10
#define SEUIL_ROUGE_CM     30
#define POINT_ID           "P07"
#define DEVICE_ID          "TEEW-07"
// Endpoint qui accepte les mesures capteur (POST). /points est en lecture seule (GET).
#define API_URL            "https://sneezing-snap-choosing.ngrok-free.dev/api/v1/readings"

// Branchements Pins (cohérents avec le diagram.json proposé)
#define PIN_TRIG    12
#define PIN_ECHO    14
#define PIN_DHT     15
#define DHTTYPE     DHT22

#define PIN_LED_VERT  25
#define PIN_LED_JAUNE 26
#define PIN_LED_ROUGE 27
#define PIN_BUZZER    33

DHT dht(PIN_DHT, DHTTYPE);

// Client TLS persistant : recreer une poignee de main TLS complete a
// chaque appel coute plusieurs secondes sur ESP32 (mesure via ngrok :
// ~5s de duree de connexion mediane contre ~5ms de traitement cote
// backend). En le gardant global et en activant le keep-alive HTTP,
// la connexion est reutilisee entre les cycles au lieu d'etre
// renegociee a chaque envoi.
WiFiClientSecure secureClient;

// Structure pour stocker les données en cas d'échec du réseau (Buffer RAM de 50 places)
struct Measurement {
  float water_cm;
  float temp_c;
  String ts;
};
Measurement ram_buffer[50];
int buffer_count = 0;

// Configuration WiFi de simulation Wokwi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

void setup() {
  Serial.begin(115200);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);

  pinMode(PIN_LED_VERT, OUTPUT);
  pinMode(PIN_LED_JAUNE, OUTPUT);
  pinMode(PIN_LED_ROUGE, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  dht.begin();

  secureClient.setInsecure(); // pas de verification de certificat — suffisant pour la démo hackathon

  Serial.println("Connexion au WiFi de simulation Wokwi...");
  WiFi.begin(ssid, password);

  // On ne bloque pas le démarrage si le réseau échoue (Critère B.6: mode dégradé opérationnel)
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 10) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connecté !");
  } else {
    Serial.println("\nMode dégradé activé (Pas de réseau)");
  }
}

// Fonction pour trier et obtenir la valeur médiane de distance (Rejet des valeurs aberrantes)
float getMedianDistance(float temperature) {
  float measures[10];
  int valid_count = 0;

  // Calcul de la vitesse du son corrigée : v = 331.3 + 0.606 * T
  float speed_of_sound = 331.3 + (0.606 * temperature);

  for (int i = 0; i < 10; i++) {
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);

    long duration_us = pulseIn(PIN_ECHO, HIGH, 30000); // timeout 30ms

    if (duration_us > 0) {
      // Formule imposée : distance_cm = duree_us * v / 20000
      measures[valid_count] = (duration_us * speed_of_sound) / 20000.0;
      valid_count++;
    }
    delay(20); // court répit entre les tirs ultrasoniques
  }

  if (valid_count == 0) return HAUTEUR_INSTALL_CM; // Sécurité si aucune mesure

  std::sort(measures, measures + valid_count);
  return measures[valid_count / 2];
}

// Envoi des données vers l'API
bool sendPostRequest(float water, float temp, String timestamp) {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  http.begin(secureClient, API_URL);
  http.setReuse(true); // garde la connexion TLS ouverte entre les requetes
  http.addHeader("Content-Type", "application/json");

  // Construction manuelle du JSON UTF-8 sans bibliothèque externe lourde
  String jsonPayload = "{";
  jsonPayload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  jsonPayload += "\"point_id\":\"" + String(POINT_ID) + "\",";
  jsonPayload += "\"ts\":\"" + timestamp + "\",";
  jsonPayload += "\"water_cm\":" + String(water, 1) + ",";
  jsonPayload += "\"temp_c\":" + String(temp, 1) + ",";
  jsonPayload += "\"battery_v\":3.92,"; // Valeur fixe demandée par le contrat
  jsonPayload += "\"source\":\"sensor\"";
  jsonPayload += "}";

  int httpResponseCode = http.POST(jsonPayload);
  http.end();

  return (httpResponseCode == 200 || httpResponseCode == 201);
}

void loop() {
  // 1 & 2. Lecture des capteurs
  float temp_c = dht.readTemperature();
  if (isnan(temp_c)) temp_c = 25.0; // Valeur par défaut si le capteur bugge

  float distance_cm = getMedianDistance(temp_c);

  // 4. Calcul de la hauteur d'eau stagnante
  float water_cm = (float)HAUTEUR_INSTALL_CM - distance_cm;
  if (water_cm < 0) water_cm = 0; // Contrainte de sécurité imposée

  // 5 & 6. Logique de Niveau local (Fallback) & Actionneurs
  String level = "VERT";

  // Réinitialisation des actionneurs
  digitalWrite(PIN_LED_VERT, LOW);
  digitalWrite(PIN_LED_JAUNE, LOW);
  digitalWrite(PIN_LED_ROUGE, LOW);
  noTone(PIN_BUZZER);

  if (water_cm < SEUIL_JAUNE_CM) {
    level = "VERT";
    digitalWrite(PIN_LED_VERT, HIGH);
    // Silence (pas de bip)
  }
  else if (water_cm >= SEUIL_JAUNE_CM && water_cm <= SEUIL_ROUGE_CM) {
    level = "JAUNE";
    digitalWrite(PIN_LED_JAUNE, HIGH);
    // Mode 2 bips rapides
    tone(PIN_BUZZER, 1000, 100); delay(150);
    tone(PIN_BUZZER, 1000, 100);
  }
  else if (water_cm > SEUIL_ROUGE_CM) {
    level = "ROUGE";
    digitalWrite(PIN_LED_ROUGE, HIGH);
    // Sirène continue
    tone(PIN_BUZZER, 440);
  }

  // Horodatage simulé (format ISO8601 exigé)
  String current_ts = "2026-08-23T14:32:00Z";

  // 7 & 8. Envoi ou stockage en cas d'échec
  bool success = sendPostRequest(water_cm, temp_c, current_ts);

  // Format d'affichage strict pour le Moniteur Série (B.4)
  Serial.print("water_cm=");
  Serial.print(water_cm, 1);
  Serial.print(" temp=");
  Serial.print(temp_c, 1);
  Serial.print(" level=");
  Serial.print(level);

  if (success) {
    Serial.println(" -> POST 200 OK");
    // Si des données étaient en attente dans la RAM, on tente d'en dépiler une
    if (buffer_count > 0) {
      Measurement delayed = ram_buffer[buffer_count - 1];
      if (sendPostRequest(delayed.water_cm, delayed.temp_c, delayed.ts)) {
        buffer_count--;
      }
    }
  } else {
    Serial.println(" -> POST FAILED (Stored in RAM)");
    // Sauvegarde en RAM si buffer non plein (Limite de 50 mesures)
    if (buffer_count < 50) {
      ram_buffer[buffer_count] = { water_cm, temp_c, current_ts };
      buffer_count++;
    }
  }

  // Boucle de 3 secondes pour le mode Démo (B.3)
  delay(3000);
}

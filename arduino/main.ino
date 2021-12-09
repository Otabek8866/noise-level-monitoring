#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>
#include <math.h>
//#include <RTCZero.h>
//#include <DateTime.h>
//#include <WiFi101.h>
#include "arduino_secrets.h"

//Setting credentials
char ssid[] = SECRET_SSID;   // your network SSID (name)
char pass[] = SECRET_PASS;   // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS; // the Wifi radio's status

// Server address and port number
char serverAddress[] = "your_server_ip_address"; //"172.27.63.72";  // server address
int port = 80;

// create http client
WiFiClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, port);

// Defining PIN and global de
int sensorPin = A0;
int sensorValue = 0;
//RTCZero rtc;

void setup()
{
  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  //  while (!Serial);

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED)
  {
    Serial.print("Attempting to connect to network: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(5000);
  }

  // connect and print out the data:
  Serial.println("You're connected to the network");

  Serial.println("----------------------------------------");
  printData();
  Serial.println("----------------------------------------");
}

void loop()
{

  // reading the data from PIN
  float average = 0;
  for (int i = 0; i < 20; i++)
  {
    average += analogRead(sensorPin);
    delay(250);
  }
  average = average / 20;
  float result = 20.0 * log10(average);

  Serial.println("making POST request");
  String contentType = "application/json";

  // data to send
  String postData = "{\"value\": ";
  postData.concat(result);
  String half2 = "}";
  postData += half2;

  client.post("/sensordata", contentType, postData);

  // read the status code and body of the response
  int statusCode = client.responseStatusCode();
  String response = client.responseBody();

  Serial.print("Status code: ");
  Serial.println(statusCode);
  Serial.print("Response: ");
  Serial.println(response);

  Serial.println("Wait for 5 minutes");
}

// function to print out the network status
void printData()
{
  Serial.println("Board Information:");
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  Serial.println();
  Serial.println("Network Information:");
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);
}

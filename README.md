# Noise Level Monitoring
Noise Level Monitoring application for classrooms

This application includes the whole architecture implementation.
There is a sensor intalled on Arduino board. It measures the noise level and sends to the proxy(web) server.
The proxy server analyzes the data, checks for anomalies and sends it to SSiO IoT platform to store.

When a user wants to monitor the noise level in the room, he accesses the web server.
The web page includes all the realtime and historical data of noise levels.
The web page also informs the user if the noise level reaches a specified threshold.


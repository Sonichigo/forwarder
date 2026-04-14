# forwarder
Forwarder to translate integer dates to format DBmarlin expects

# forwarder
Forwarder to translate integer dates to format DBmarlin expects

## example running locally
An example running locally

In 1 terminal:

	mjeffery@mjminikube:~/forwarder$ python3 app.py 
 	* Serving Flask app 'app'
 	* Debug mode: off
	2026-04-14 10:28:30,316 INFO werkzeug WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 	* Running on all addresses (0.0.0.0)
 	* Running on http://127.0.0.1:8080
 	* Running on http://192.168.1.245:8080
	2026-04-14 10:28:30,316 INFO werkzeug Press CTRL+C to quit

In 2nd terminal:

	mjeffery@mjminikube:~$ curl -v 'http://127.0.0.1:8080/archiver/rest/v1/activity/summary?from=-60000&to=0&tz=Europe/London&interval=0&id=5'
	*   Trying 127.0.0.1:8080...
	* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
	> GET /archiver/rest/v1/activity/summary?from=-60000&to=0&tz=Europe/London&interval=0&id=5 HTTP/1.1
	> Host: 127.0.0.1:8080
	> User-Agent: curl/7.81.0
	> Accept: */*
	> 
	* Mark bundle as not supporting multiuse
	< HTTP/1.1 200 OK
	< Server: Werkzeug/3.1.8 Python/3.10.12
	< Date: Tue, 14 Apr 2026 10:29:08 GMT
	< Content-Type: application/json
	< Content-Length: 268
	< Connection: close
	< 
	[[{"avgwaittime":1000.047619047619,"batchexecutions":0.0,"executions":0.0,"stddevwaittime":0.21295885490081326,"summary":null,"timestamp":"2026-04-14+11:28:37","waitcount":21.0,"waittime":21001.0,"waittimesquared":21002001.0,"zscorewaittime":0.00010647435621168279}]]
	* Closing connection 0

In first terminal:

        2026-04-14 10:29:07,968 INFO archiver-forwarder Incoming request path=/archiver/rest/v1/activity/summary remote_addr=127.0.0.1 args={'from': '-60000', 'to': '0', 'tz': 'Europe/London', 'interval': '0', 'id': '5'}
        2026-04-14 10:29:07,970 INFO archiver-forwarder Converted epoch_ms=1776162487968 tz=Europe/London formatted=2026-04-14+11:28:07
        2026-04-14 10:29:07,970 INFO archiver-forwarder Converted epoch_ms=1776162547968 tz=Europe/London formatted=2026-04-14+11:29:07
        2026-04-14 10:29:07,970 INFO archiver-forwarder Rewritten upstream URL=https://play.dbmarlin.com/archiver/rest/v1/activity/summary?from=2026-04-14+11:28:07&to=2026-04-14+11:29:07&tz=Europe%2FLondon&interval=0&id=5
        2026-04-14 10:29:08,144 INFO archiver-forwarder Upstream response status=200 content_type=application/json;charset=UTF-8
        2026-04-14 10:29:08,145 INFO archiver-forwarder Converted epoch_ms=1776162517968 tz=Europe/London formatted=2026-04-14+11:28:37
        2026-04-14 10:29:08,145 INFO werkzeug 127.0.0.1 - - [14/Apr/2026 10:29:08] "GET /archiver/rest/v1/activity/summary?from=-60000&to=0&tz=Europe/London&interval=0&id=5 HTTP/1.1" 200 -

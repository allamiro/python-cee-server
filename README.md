# CEE Server Using Python

## What is Common Event Expression (CEE)?
CEE was developed by MITRE as an extension for Syslog, based on JSON. MITRE’s work on CEE was discontinued in 2013. Below is an example of a CEE log message:

```
Dec 20 12:42:20 syslog-relay serveapp[1335]: @cee: {"pri":10,"id":121,"appname":"serveapp","pid":1335,"host":"syslog-relay","time":"2011-12-20T12:38:05.123456-05:00","action":"login","domain":"app","object":"account","status":"success"}
```
## Required Tools

To set up the CEE Server on Redhat/CentOS/Fedora systems, ensure the following tools are installed:

```dnf install python3 python3-tools -y ```

## How to Use the Tool
### Run Manually

1. Clone the Repository

Clone the repository to your preferred location:

```git clone https://github.com/allamiro/cee-server.git```

2. Navigate to the Directory and Run the Script

Change the directory to the cee-server directory and run the script:

```cd cee-server```

```python3 cee_log_server.py```

3. Create a Service for Continuous Execution (Optional)

If you want the script to run as a persistent service:

* Make the ```configure_service.bash``` script executable:

```chmod +x configure_service.bash```

* Execute the script to create the service:

```./configure_service.bash ```

This will create and enable a systemd service for the CEE server.


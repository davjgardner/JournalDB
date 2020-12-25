# JournalDB

JournalDB is a simple self-hosted cloud journaling application created with Python Flask. It allows the creation of daily entries, and displays them in a fast web timeline view.

# Getting Started

1. Clone the project to your server: `git clone git@github.com:davjgardner/journaldb.git`
2. Install with `pip`: `cd journaldb && pip install .`
3. Set up the environment with `source env.sh`
4. Initialize the database with `flask init-db`
5. Run with `flask run`
6. Visit http://localhost:5000 and start journaling!

## Start JournalDB on boot

This is just one way to automatically start JournalDB. You may also want to consider a Docker container, or even running it with a real webserver.

### Systemd Unit File

```
[Unit]
Description=JournalDB cloud journaling system
After=network.target

[Service]
Type=simple
User=<your_user>

ExecStart=/path/to/journaldb/run.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start it with `sudo systemctl enable journaldb && sudo systemctl start journaldb`

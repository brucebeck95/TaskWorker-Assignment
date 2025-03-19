# Steps:
Run `make run`. This will build the application and run the Database and web server.
You can then access the swagger documentation from `localhost:8000/docs`.

`make test` will run the pytest happy flow tests.

The round robin configuration can be changed in `Dockerfile`.

I would normally make this a cron job on the server that I am hosting, or via an AWS cron job.
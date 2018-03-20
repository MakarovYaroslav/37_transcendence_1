worker_processes  1;

events {
    worker_connections  1024;
}

http{
    include mime.types;

    upstream django {
        server unix://{{ PROJECT_PATH }}/{{ PROJECT_NAME }}/social_network.sock;
    }

    server {
        listen 80;
        server_name localhost;
        charset utf-8;

        client_max_body_size 75M;

        location /static {
            alias {{ PROJECT_PATH }}/{{ PROJECT_NAME }}/static;

        }

        location / {
            uwsgi_pass  django;
            include     {{ PROJECT_PATH }}/{{ PROJECT_NAME }}/configs/uwsgi_params;
        }
    }
}
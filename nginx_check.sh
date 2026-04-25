#!/bin/bash
# NGINX Configuration Check for DPRAMP

echo "🔍 NGINX Configuration Check"
echo "============================"

# Check if NGINX config exists
NGINX_CONFIG="/etc/nginx/sites-available/dpramp"

if [ -f "$NGINX_CONFIG" ]; then
    echo "✅ NGINX config found: $NGINX_CONFIG"
    echo ""
    echo "📄 Current NGINX configuration:"
    echo "================================"
    cat "$NGINX_CONFIG"
    echo ""
    
    # Check if static files location is correct
    if grep -q "alias /var/www/dpramp/staticfiles" "$NGINX_CONFIG"; then
        echo "✅ Static files alias found"
    else
        echo "❌ Static files alias NOT found"
        echo ""
        echo "🔧 Add this to your NGINX config:"
        echo "location /static/ {"
        echo "    alias /var/www/dpramp/staticfiles/;"
        echo "}"
    fi
    
    # Check if media files location is correct
    if grep -q "alias /var/www/dpramp/media" "$NGINX_CONFIG"; then
        echo "✅ Media files alias found"
    else
        echo "❌ Media files alias NOT found"
        echo ""
        echo "🔧 Add this to your NGINX config:"
        echo "location /media/ {"
        echo "    alias /var/www/dpramp/media/;"
        echo "}"
    fi
    
else
    echo "❌ NGINX config NOT found: $NGINX_CONFIG"
    echo ""
    echo "🔧 Create NGINX config with:"
    echo "sudo nano /etc/nginx/sites-available/dpramp"
    echo ""
    echo "📄 Add this content:"
    echo "server {"
    echo "    listen 80;"
    echo "    server_name dpramp.com www.dpramp.com;"
    echo ""
    echo "    location = /favicon.ico { access_log off; log_not_found off; }"
    echo "    location /static/ {"
    echo "        alias /var/www/dpramp/staticfiles/;"
    echo "    }"
    echo "    location /media/ {"
    echo "        alias /var/www/dpramp/media/;"
    echo "    }"
    echo "    location / {"
    echo "        include proxy_params;"
    echo "        proxy_pass http://127.0.0.1:8000;"
    echo "    }"
    echo "}"
fi

echo ""
echo "🔄 Test NGINX configuration:"
echo "sudo nginx -t"
echo ""
echo "🔄 Restart NGINX:"
echo "sudo systemctl restart nginx"

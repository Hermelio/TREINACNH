#!/bin/bash
# Script to setup security measures for TREINACNH server

echo "=================================================="
echo "TREINACNH Security Setup Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}1. Installing fail2ban...${NC}"
apt-get update
apt-get install -y fail2ban

echo -e "${YELLOW}2. Configuring fail2ban...${NC}"
# Copy filter
cp fail2ban-django-auth.conf /etc/fail2ban/filter.d/django-auth.conf

# Copy jail configuration
cp fail2ban-jail-treinacnh.conf /etc/fail2ban/jail.d/treinacnh.conf

# Enable and start fail2ban
systemctl enable fail2ban
systemctl restart fail2ban

echo -e "${GREEN}✓ Fail2ban configured and started${NC}"

echo -e "${YELLOW}3. Backing up current Nginx configuration...${NC}"
cp /etc/nginx/sites-available/treinacnh /etc/nginx/sites-available/treinacnh.backup.$(date +%Y%m%d)

echo -e "${YELLOW}4. Installing new secure Nginx configuration...${NC}"
cp nginx_secure.conf /etc/nginx/sites-available/treinacnh

# Test Nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
    echo -e "${YELLOW}5. Reloading Nginx...${NC}"
    systemctl reload nginx
    echo -e "${GREEN}✓ Nginx reloaded with new configuration${NC}"
else
    echo -e "${RED}✗ Nginx configuration test failed${NC}"
    echo -e "${YELLOW}Restoring backup...${NC}"
    cp /etc/nginx/sites-available/treinacnh.backup.$(date +%Y%m%d) /etc/nginx/sites-available/treinacnh
    exit 1
fi

echo -e "${YELLOW}6. Creating cache directory for Nginx...${NC}"
mkdir -p /var/cache/nginx
chown www-data:www-data /var/cache/nginx

echo -e "${YELLOW}7. Configuring UFW Firewall...${NC}"
# Allow only necessary ports
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8080/tcp comment 'App Port'
ufw allow 3306/tcp comment 'MySQL'

echo -e "${GREEN}✓ Firewall configured${NC}"

echo -e "${YELLOW}8. Setting up log rotation...${NC}"
cat > /etc/logrotate.d/treinacnh << 'EOF'
/var/www/TREINACNH/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn-treinacnh > /dev/null 2>&1 || true
    endscript
}
EOF

echo -e "${GREEN}✓ Log rotation configured${NC}"

echo -e "${YELLOW}9. Installing security updates...${NC}"
apt-get update
apt-get upgrade -y

echo ""
echo "=================================================="
echo -e "${GREEN}Security setup completed successfully!${NC}"
echo "=================================================="
echo ""
echo "Summary of protections:"
echo "  ✓ Fail2ban installed and configured"
echo "  ✓ Nginx hardened with rate limiting"
echo "  ✓ Security headers configured"
echo "  ✓ Firewall (UFW) configured"
echo "  ✓ Log rotation configured"
echo "  ✓ System updated"
echo ""
echo "To check fail2ban status:"
echo "  sudo fail2ban-client status"
echo ""
echo "To check banned IPs:"
echo "  sudo fail2ban-client status django-auth"
echo "  sudo fail2ban-client status sshd"
echo ""
echo "To unban an IP:"
echo "  sudo fail2ban-client set django-auth unbanip <IP>"
echo ""
echo -e "${YELLOW}Note: Django rate limiting will be active after deploying the code changes${NC}"

# Deploying Education Assistant to EC2

This guide explains how to deploy the containerized Education Assistant application to an Amazon EC2 instance.

## Prerequisites

1. An AWS account
2. Basic knowledge of AWS EC2
3. An EC2 instance running Amazon Linux 2 or Ubuntu
4. SSH access to your EC2 instance

## Deployment Steps

### 1. Set Up Your EC2 Instance

1. Launch an EC2 instance (t2.micro or larger recommended)
2. Make sure to configure the security group to allow:
   - SSH (port 22) from your IP
   - HTTP (port 80) from anywhere
   - HTTPS (port 443) from anywhere
   - Custom TCP (port 8080) from anywhere (if you want to expose the app directly)

### 2. Install Docker on EC2

Connect to your EC2 instance via SSH:

```bash
ssh -i your-key.pem ec2-user@your-ec2-instance-ip
```

Install Docker and Docker Compose:

**For Amazon Linux 2:**
```bash
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**For Ubuntu:**
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu
# Install Docker Compose
sudo apt install -y docker-compose
```

Log out and log back in for the group changes to take effect.

### 3. Deploy the Application

1. Clone your repository or upload your application files to the EC2 instance:

```bash
# If using git
git clone your-repo-url

# Or create a directory and upload files manually
mkdir education-assistant
cd education-assistant
# Then upload your files with scp or similar
```

2. Create or update the `.env` file with your production settings:

```bash
nano .env
```

Make sure to set your production API keys and other environment variables.

3. Build and start the Docker container:

```bash
docker-compose up -d
```

This will build the Docker image and start the container in detached mode.

### 4. Verify Deployment

Check if the container is running:

```bash
docker ps
```

Test the application by accessing:
```
http://your-ec2-instance-ip:8080
```

### 5. Set Up a Domain and HTTPS (Optional)

For production deployments, it's recommended to set up a proper domain name and HTTPS:

1. Configure a domain to point to your EC2 instance IP
2. Install and configure Nginx to proxy requests to your Docker container
3. Use Certbot/Let's Encrypt to add HTTPS

Example Nginx configuration:

```
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Continuous Deployment (Optional)

For automated deployments, you can set up a CI/CD pipeline using GitHub Actions, AWS CodePipeline, or other CI/CD tools.

## Monitoring and Maintenance

- **Logs**: View container logs with `docker-compose logs`
- **Restart**: Restart the container with `docker-compose restart`
- **Update**: Pull latest changes, then run `docker-compose up -d --build`

## Troubleshooting

- If the application isn't accessible, check:
  - Docker container status: `docker ps`
  - Container logs: `docker-compose logs`
  - EC2 security group settings
  - Firewall settings: `sudo iptables -L` 
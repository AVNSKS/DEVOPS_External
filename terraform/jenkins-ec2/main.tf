
# Unified Firewall Security Group Matrix
resource "aws_security_group" "agronet_ha_sg" {
  name        = "agronet-ha-security-group"
  description = "Production Multi-Node Ingress Matrix"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 1. Master Control Node
resource "aws_instance" "k3s_master" {
  ami                    = "ami-01a00762f46d584a1"
  instance_type          = "c7i-flex.large"
  key_name               = "DEVOPS"
  vpc_security_group_ids = [aws_security_group.agronet_ha_sg.id]
  tags                   = { Name = "AgroNet-K3s-Master" }
}

# 2. Worker Node 01 (Active Workloads)
resource "aws_instance" "k3s_worker_1" {
  ami                    = "ami-01a00762f46d584a1"
  instance_type          = "c7i-flex.large"
  key_name               = "DEVOPS"
  vpc_security_group_ids = [aws_security_group.agronet_ha_sg.id]
  tags                   = { Name = "AgroNet-K3s-Worker-01" }
}

# 3. Worker Node 02 (Failover / Extra Scale Capacity)
resource "aws_instance" "k3s_worker_2" {
  ami                    = "ami-01a00762f46d584a1"
  instance_type          = "c7i-flex.large"
  key_name               = "DEVOPS"
  vpc_security_group_ids = [aws_security_group.agronet_ha_sg.id]
  tags                   = { Name = "AgroNet-K3s-Worker-02" }
}

output "master_ip" { value = aws_instance.k3s_master.public_ip }
output "worker_1_ip" { value = aws_instance.k3s_worker_1.public_ip }
output "worker_2_ip" { value = aws_instance.k3s_worker_2.public_ip }
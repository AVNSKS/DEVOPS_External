output "master_public_ip" {
  description = "The public IP address of the K3s Master Control Node"
  value       = aws_instance.k3s_master.public_ip
}

output "master_instance_id" {
  description = "The AWS Instance ID of the K3s Master Control Node"
  value       = aws_instance.k3s_master.id
}

output "worker_1_public_ip" {
  description = "The public IP address of Worker Node 01"
  value       = aws_instance.k3s_worker_1.public_ip
}

output "worker_2_public_ip" {
  description = "The public IP address of Worker Node 02"
  value       = aws_instance.k3s_worker_2.public_ip
}

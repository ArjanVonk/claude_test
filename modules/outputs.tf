output "acr_login_server" {
  description = "ACR login server URL"
  value       = azurerm_container_registry.main.login_server
}

output "dashboard_url" {
  description = "Public URL of the Streamlit dashboard"
  value       = "http://${azurerm_container_group.main.fqdn}:8501"
}

output "container_ip" {
  description = "Public IP of the container group"
  value       = azurerm_container_group.main.ip_address
}

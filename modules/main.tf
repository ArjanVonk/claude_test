resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# ── Container Registry ────────────────────────────────────────────────────────
resource "azurerm_container_registry" "main" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

# ── Container Instance ────────────────────────────────────────────────────────
resource "azurerm_container_group" "main" {
  name                = "ci-imbalance-dashboard"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  restart_policy      = "Always"

  image_registry_credential {
    server   = azurerm_container_registry.main.login_server
    username = azurerm_container_registry.main.admin_username
    password = azurerm_container_registry.main.admin_password
  }

  container {
    name   = "dashboard"
    image  = "${azurerm_container_registry.main.login_server}/imbalance-dashboard:${var.image_tag}"
    cpu    = var.cpu
    memory = var.memory_gb

    ports {
      port     = 8501
      protocol = "TCP"
    }
  }

  ip_address_type = "Public"
  dns_name_label  = "imbalance-dashboard"

  exposed_port {
    port     = 8501
    protocol = "TCP"
  }
}

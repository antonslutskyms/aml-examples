provider "azurerm" {
  features {}
}

resource "null_resource" "create_ml_registry" {
  provisioner "local-exec" {
    command = <<EOT
      az ml registry create --resource-group antonslutsky-rg --file "${path.module}/registry.yml"
    EOT
    interpreter = ["pwsh", "-Command"]
  }
}
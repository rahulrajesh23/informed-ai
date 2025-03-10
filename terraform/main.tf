terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }

  backend "gcs" {
    bucket = "informed-ai-prod-2-bucket"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_container_cluster" "gke_cluster" {
  name     = "informed-ai"
  location = var.region

  lifecycle {
    ignore_changes = [
      node_pool_auto_config,
      secret_manager_config
    ]
  }
}

resource "google_container_node_pool" "default_node_pool" {
  name               = "default"
  cluster            = "informed-ai"
  location           = var.region
  node_count         = 1
  initial_node_count = 1
  node_locations     = ["us-central1-c"]

  node_config {
    machine_type = "e2-standard-2"
    disk_size_gb = 100

    oauth_scopes = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/service.management.readonly",
      "https://www.googleapis.com/auth/servicecontrol",
      "https://www.googleapis.com/auth/trace.append"
    ]

    metadata = {
      "disable-legacy-endpoints" = "true"
    }

    shielded_instance_config {
      enable_integrity_monitoring = true
      enable_secure_boot          = false
    }

    kubelet_config {
      cpu_cfs_quota                          = false
      insecure_kubelet_readonly_port_enabled = "TRUE"
      pod_pids_limit                         = 0
    }

    resource_labels = {
      "goog-gke-node-pool-provisioning-model" = "on-demand"
    }

    advanced_machine_features {
      enable_nested_virtualization = false
      threads_per_core             = 0
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
    strategy        = "SURGE"
  }

  queued_provisioning {
    enabled = false
  }

  lifecycle {
    ignore_changes = [
      instance_group_urls,
      managed_instance_group_urls,
      version
    ]
  }
}

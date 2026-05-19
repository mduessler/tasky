# Infrastructure Dokumentation

> **Zweck:** Remote Terraform State Backend für verteilte Entwicklung + AWS-gehosteter
> GitLab Runner
> **Region:** `eu-central-1` (Frankfurt)
> **Terraform:** ≥ 1.6.0 · AWS Provider `~> 5.0`

______________________________________________________________________

## Übersicht

Die Infrastruktur ist in zwei voneinander getrennte Terraform-Workspaces
aufgeteilt, die in einer festen Reihenfolge deployed werden müssen:

```
terraform/
├── bootstrap/                  # 1. Schritt: State-Backend aufsetzen
│   └── modules/
│       ├── s3_bucket/          # Wiederverwendbares S3-Modul
│       ├── security/           # Verschlüsselung & Public-Access-Block
│       └── logging/            # Access-Logging für den State-Bucket
│
└── environment/
    └── dev/
        └── gitlab-runner/      # 2. Schritt: GitLab Runner deployen
            └── modules/
                ├── compute/    # EC2-Instanz
                ├── network/    # VPC, Subnets, NAT Gateway
                └── security/   # IAM Role & Instance Profile
```

Das Bootstrap-Layer legt den S3-Bucket und die DynamoDB-Tabelle an, die der
gitlab-runner-Workspace anschließend als Remote-Backend nutzt. So können mehrere
Entwickler gleichzeitig am selben Terraform-State arbeiten, ohne sich
gegenseitig zu überschreiben.

______________________________________________________________________

## Layer 1 – Bootstrap (Remote State Backend)

**Verzeichnis:** `terraform/bootstrap/`

Dieser Workspace wird **einmalig** ausgeführt und legt die gesamte Infrastruktur
an, auf der das Remote-State-Management aufbaut. Er verwaltet seinen eigenen
State **lokal** (kein S3-Backend).

### Ressourcen

#### S3 State Bucket

| Eigenschaft        | Wert                                       |
| ------------------ | ------------------------------------------ |
| Name               | `gitlab-runner-terraform-state-<owner_id>` |
| Versioning         | Aktiviert                                  |
| Verschlüsselung    | AES-256 (Server-Side)                      |
| Public Access      | Vollständig blockiert                      |
| TLS                | Erzwungen (Policy `DenyNonTLS`)            |
| Destroy Protection | `prevent_destroy = true`                   |

Der Bucket speichert die `terraform.tfstate`-Dateien aller nachgelagerten
Workspaces. Versioning stellt sicher, dass ältere State-Versionen bei Bedarf
wiederhergestellt werden können.

#### DynamoDB Lock Table

| Eigenschaft | Wert                            |
| ----------- | ------------------------------- |
| Name        | `gitlab-runner-terraform-locks` |
| Billing     | PAY_PER_REQUEST                 |
| Hash Key    | `LockID` (String)               |

Verhindert konkurrierende `terraform apply`-Ausführungen. Bevor Terraform den
State schreibt, legt es einen Lock in dieser Tabelle an. Ist der Lock bereits
vorhanden, schlägt der Vorgang mit einem Fehler fehl.

#### S3 Log Bucket

| Eigenschaft      | Wert                                            |
| ---------------- | ----------------------------------------------- |
| Name             | `gitlab-runner-terraform-state-logs-<owner_id>` |
| Zweck            | Access-Logs des State-Buckets                   |
| Prefix           | `logs/`                                         |
| Object Ownership | `BucketOwnerPreferred`                          |

Alle Zugriffe auf den State-Bucket werden in diesen separaten Bucket geloggt.
Der Log-Bucket hat dieselben Sicherheitseinstellungen (AES-256, Public-Access-
Block, TLS-only) wie der State-Bucket selbst.

### Module

**`modules/s3_bucket`** — Erstellt einen S3-Bucket mit konfigurierbarem
Versioning. Wird von `bootstrap/main.tf` und `modules/logging` genutzt.

**`modules/security`** — Wendet AES-256-Serverseitenverschlüsselung und
vollständigen Public-Access-Block auf einen gegebenen Bucket an.

**`modules/logging`** — Erstellt den Log-Bucket und aktiviert S3 Server Access
Logging vom State-Bucket dorthin. Stellt sicher, dass nur der S3-Logging-Service
in den Log-Bucket schreiben darf und nur aus dem eigenen AWS-Account.

### Konfiguration

```hcl
# terraform/bootstrap/terraform.tfvars
aws_region  = "eu-central-1"
environment = "dev"
owner_id    = "REDACTED_AWS_ACCOUNT"   # AWS Account ID – Teil des Bucket-Namens
```

### Outputs

| Output                | Beschreibung                                       |
| --------------------- | -------------------------------------------------- |
| `s3_bucket_name`      | Name des State-Buckets (für Backend-Konfiguration) |
| `dynamodb_table_name` | Name der Lock-Tabelle                              |

### Deployment

```bash
cd terraform/bootstrap
terraform init
terraform plan
terraform apply
```

> ⚠️ Dieser Workspace darf **nicht** gelöscht werden, solange nachgelagerte
> Workspaces existieren. Der S3-Bucket hat `prevent_destroy = true` gesetzt
> und muss vor dem Löschen manuell geleert werden.

______________________________________________________________________

## Layer 2 – GitLab Runner

**Verzeichnis:** `terraform/environment/dev/gitlab-runner/`

Dieser Workspace deployed den GitLab Runner als EC2-Instanz in einer privaten
AWS-Netzwerkinfrastruktur. Er nutzt das im Bootstrap aufgesetzte S3-Backend für
seinen Remote-State.

### Remote Backend

```hcl
backend "s3" {
  bucket       = "gitlab-runner-terraform-state-REDACTED_AWS_ACCOUNT"
  key          = "dev/terraform.tfstate"
  region       = "eu-central-1"
  use_lockfile = true
  encrypt      = true
}
```

`use_lockfile = true` aktiviert das S3-native Locking (ab Terraform 1.15 als
Ergänzung zu DynamoDB verfügbar). `encrypt = true` stellt sicher, dass der State
verschlüsselt abgelegt wird.

### Architektur

```
Internet
    │
    ▼
Internet Gateway
    │
    ▼
Public Subnet (10.0.0.0/24)
    │
    ├── Elastic IP
    │
    ▼
NAT Gateway
    │
    ▼
Private Subnet (10.0.1.0/24)
    │
    ▼
EC2: GitLab Runner
    │  Security Group: nur HTTPS (443) outbound
    │  IAM Role: gitlab-runner-role-dev
    ▼
(kein eingehender Traffic)
```

Der Runner hat **keine öffentliche IP** und ist über das Internet nicht
erreichbar. Ausgehende Verbindungen (z.B. zu gitlab.com, zur Docker Registry)
laufen über den NAT Gateway.

### Module

#### `modules/network`

Erstellt die gesamte Netzwerkinfrastruktur:

| Ressource        | Wert                                |
| ---------------- | ----------------------------------- |
| VPC CIDR         | `10.0.0.0/16`                       |
| Public Subnet    | `10.0.0.0/24` (AZ: `eu-central-1a`) |
| Private Subnet   | `10.0.1.0/24` (AZ: `eu-central-1a`) |
| Internet Gateway | Für public Subnet                   |
| NAT Gateway      | Im public Subnet, mit Elastic IP    |
| Security Group   | Nur Egress TCP 443 (HTTPS)          |

Die Security Group lässt **keinen eingehenden Traffic** zu. Der Runner
kommuniziert nur ausgehend mit GitLab über HTTPS.

#### `modules/compute`

Erstellt die EC2-Instanz für den Runner:

| Eigenschaft   | Wert                                          |
| ------------- | --------------------------------------------- |
| AMI           | Ubuntu 24.04 LTS (Noble) – aktuellste Version |
| Instance Type | `t3.micro` (konfigurierbar)                   |
| Subnet        | Private Subnet                                |
| Public IP     | Nein                                          |
| IAM Profile   | `gitlab-runner-profile-dev`                   |

Das AMI wird dynamisch über einen Data-Source-Filter bezogen (`owners =   ["099720109477"]`
ist Canonicals offizielle AWS-Account-ID), sodass immer das aktuellste
Ubuntu-24.04-Image verwendet wird.

#### `modules/security`

Erstellt die IAM-Berechtigungen für den Runner:

| Ressource        | Name                        |
| ---------------- | --------------------------- |
| IAM Role         | `gitlab-runner-role-dev`    |
| Instance Profile | `gitlab-runner-profile-dev` |

Die IAM-Role erlaubt EC2-Instanzen, diese Role anzunehmen (`ec2.amazonaws.com`
als Trust Principal). Folgende AWS Managed Policies sind angehängt:

| Policy                         | Zweck                                   |
| ------------------------------ | --------------------------------------- |
| `AmazonSSMManagedInstanceCore` | SSM Session Manager Zugriff             |
| `AmazonS3FullAccess`           | Terraform State lesen/schreiben         |
| `AmazonDynamoDBFullAccess`     | Terraform Lock-Tabelle                  |
| `AmazonEC2FullAccess`          | EC2-Ressourcen provisionieren           |
| `AmazonVPCFullAccess`          | Netzwerk-Ressourcen provisionieren      |
| `IAMFullAccess`                | IAM Roles für provisionierte Ressourcen |

> ⚠️ `IAMFullAccess` erlaubt dem Runner theoretisch, Rollen mit mehr Rechten
> als er selbst hat anzulegen (Privilege Escalation). Für eine Dev-Umgebung
> akzeptabel — in Prod sollte das auf konkrete `iam:PassRole`-Bindings
> eingeschränkt werden.

### Outputs

| Output                      | Beschreibung                      |
| --------------------------- | --------------------------------- |
| `gitlab_runner_instance_id` | Instance ID des Runners (für SSM) |

Shell-Zugriff auf die Instanz per SSM:

```bash
aws ssm start-session --target $(terraform output -raw gitlab_runner_instance_id)
```

### Konfiguration

```hcl
# terraform/environment/dev/gitlab-runner/terraform.tfvars
aws_region  = "eu-central-1"
environment = "dev"
# instance_type wird nicht gesetzt → default "t3.micro"
```

### Deployment

```bash
# Voraussetzung: Bootstrap ist bereits deployed
cd terraform/environment/dev/gitlab-runner
terraform init
terraform plan
terraform apply
```

______________________________________________________________________

## Sicherheitsübersicht

| Bereich               | Maßnahme                                               |
| --------------------- | ------------------------------------------------------ |
| State-Zugriff         | S3-Bucket nur per TLS erreichbar (`DenyNonTLS`)        |
| State-Verschlüsselung | AES-256 at rest, `encrypt = true` im Backend           |
| State-Locking         | DynamoDB + S3 native Lockfile                          |
| Public Access         | S3-Buckets vollständig gesperrt                        |
| Audit Trail           | Access Logs in separatem Log-Bucket                    |
| Netzwerk              | Runner nur im private Subnet, kein eingehender Traffic |
| Egress                | Nur HTTPS (Port 443) erlaubt                           |
| Instanzzugriff        | SSM Session Manager (kein SSH, kein Bastion)           |
| IAM                   | Instance Role mit Managed Policies für CI/CD-Zugriff   |

______________________________________________________________________

## Offene Punkte / Empfehlungen

- **Terraform State des Bootstraps**: Der Bootstrap-State liegt lokal und ist per
  `.gitignore` ausgeschlossen. Geht die lokale State-Datei verloren, verliert
  Terraform die Kenntnis über den S3-Bucket und die DynamoDB-Tabelle — eine manuelle
  Wiederherstellung via `terraform import` wäre nötig. Empfehlung: Die State-Datei
  zusätzlich extern sichern.
- **IAM Privilege Escalation**: `IAMFullAccess` auf dem Runner erlaubt das Erstellen
  beliebiger Rollen. Für Prod auf konkrete `iam:PassRole`-Bindings einschränken.
- **Multi-AZ**: Aktuell alles in `eu-central-1a`. Für Hochverfügbarkeit könnten
  Subnets und Runner auf mehrere AZs verteilt werden.

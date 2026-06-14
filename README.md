# Contractor ERP & Company Profile Website (ConstructFlow ERP)

This repository contains the containerized deployment setup and custom ERP modules for the **Contractor ERP and Company Profile Website** project. Built for a construction subcontractor business, this system prioritizes practical operational records over complex enterprise workflows.

---

## Table of Contents
1. [Project Overview & Business Context](#project-overview--business-context)
2. [Key Business Interpretation & Core Goals](#key-business-interpretation--core-goals)
3. [Scope Definition: MVP vs. Post-MVP](#scope-definition-mvp-vs-post-mvp)
4. [Payroll & Attendance Decision Rationale](#payroll--attendance-decision-rationale)
5. [Worker Wage Recap Flow](#worker-wage-recap-flow)
6. [Core Data Entities](#core-data-entities)
7. [User Roles](#user-roles)
8. [Technical Architecture](#technical-architecture)
9. [Deployment & First Run Instructions](#deployment--first-run-instructions)
10. [Custom Module Management](#custom-module-management)
11. [Backups](#backups)
12. [MVP Success Criteria](#mvp-success-criteria)
13. [Known Gaps & Future Considerations](#known-gaps--future-considerations)

---

## Project Overview & Business Context

The client is a construction subcontractor business managed personally by Bapak Junaidi, which has operated for approximately five years. The business focuses on construction work including:
* Housing projects (single houses, townhouses, housing projects)
* Ruko (shophouses)
* Building renovations
* Housing project subcontracting (borongan proyek perumahan)

### Operations Context
* **Contract/Project System:** Works on a project/contract system with developers or companies.
* **Material Procurement:** Materials are purchased directly from supplier building stores and stored in temporary warehouses on project/location sites.
* **Workforce:** The worker count varies heavily depending on the project scale. A single-house renovation may involve around 4 workers, whereas large-scale projects can push the total workforce to 150-200 workers.
* **Payroll:** Payments are processed weekly (every Saturday) in cash. Daily worker wages range from Rp60,000 to Rp100,000, leading to a total weekly payroll expense that can reach approximately Rp60,000,000.
* **Administration:** Financial and payroll records are currently managed manually on a weekly basis, with no dedicated administrative division.
* **Existing Project Data:** Historically, the business has executed multiple projects under key clients:
  * **PT Rid Jaya Bersama:** Dream Land 1 (Borang)
  * **PT Ramatrimitra Development:** Kartika Mataram (Talang Jambi), The Greenvillage (Mata Merah), Taman Asri 2 (Gandus), Siknatur (Gandus)
  * **PT Agung Sumatera Development:** Osaka Residence, Osaka Residence 2, Griya Bukit Berlian, Orchard Sukomoro, Orchard Tanjung Sari

---

## Key Business Interpretation & Core Goals

Since the client is a subcontractor rather than a general retail business, the system must support labor-heavy, project-based, and material-cost-sensitive operations. The MVP prioritizes practical operational tracking rather than a complex enterprise ERP workflow.

The core priorities of the MVP are:
1. **Project Tracking:** Real-time visibility into project timelines and statuses.
2. **Worker & Payment Tracking:** Easy recording of days worked and cash payouts.
3. **Material Purchase Tracking:** Recording quantities and costs of materials delivered to site warehouses.
4. **Supplier Database:** Managing store details and material categories.
5. **Weekly Financial Summary:** Aggregated view of project expenditures vs. contract incomes.
6. **Company Profile & Project Portfolio Website:** Public-facing website showcasing services, past projects, and contacts.

---

## Scope Definition: MVP vs. Post-MVP

### 1. In Scope for MVP
* **Company Profile Website:**
  * Home page, About, and Services section.
  * Project portfolio section (displaying PT Rid Jaya Bersama, PT Ramatrimitra, and PT Agung Sumatera projects).
  * Client list section.
  * WhatsApp Call-to-Action (CTA) for contact.
  * Basic pricing explanation section (describing estimation dynamics, not rigid price lists).
  * Website service categories: *Pembangunan rumah, Pembangunan ruko, Pembangunan townhouse, Renovasi bangunan, Borongan proyek perumahan*.
* **ERP System (Odoo-based):**
  * Project Management, Client Management, and Supplier Management.
  * Material Purchase Records.
  * Worker Records (stored as contact entries, not system users).
  * Worker Wage Recap (**Rekap Upah Harian/Mingguan**).
  * Weekly Payroll Summary.
  * Simple Project Finance Summary (Profit/Loss estimation).
  * Basic User Roles (Admin/Owner, Mandor/Supervisor, Finance/Admin).

### 2. Out of Scope for MVP (Future Roadmap)
* **Formal Attendance System:** No check-in/check-out, GPS tracking, worker logins, or biometric integration.
* **Full HR Payroll Complexity:** Standardized HR payroll modules, taxes, benefits, and deductions.
* **Advanced Inventory Automation:** Barcode tracking, automated reordering rules, or multi-step routing.
* **Full Accounting Setup:** General ledger, double-entry bookkeeping, tax reporting (unless requested later).
* **RAB (Rencana Anggaran Biaya) / Project Cost Estimation:** Automated quotation engine (rely on manual estimations for MVP).

---

## Payroll & Attendance Decision Rationale

> [!IMPORTANT]
> The MVP deliberately excludes a formal attendance system (GPS, worker accounts, or biometric check-in).

**Why?**
Workers are managed directly on the field by the Mandor (Bapak Junaidi), and wages are paid in cash every Saturday. Introducing login accounts, mobile check-ins, or physical scanners does not align with the current real-world field workflow. 

Instead, the MVP introduces the **Rekap Upah Harian / Mingguan** (Daily/Weekly Wage Recap) flow. This workflow registers work days and wages per project without demanding worker authentication.

---

## Worker Wage Recap Flow

The Mandor-led weekly wage recap operates as follows:
1. Admin or Mandor selects the **Project**.
2. Admin or Mandor selects the **Payroll Week** (date range).
3. Admin or Mandor records the **Workers** involved in that project.
4. Admin or Mandor enters each worker's **Daily Wage** (defaults from worker record).
5. Admin or Mandor enters the **Number of Working Days** (e.g., 1–6 days).
6. The system calculates the total wage:
   $$\text{Total Worker Wage} = \text{Daily Wage} \times \text{Number of Work Days}$$
7. Admin or Mandor marks the payment status (**Unpaid** or **Paid**).
8. Paid wages are logged as **Project Payroll Expenses**.
9. The weekly payroll summary can be reviewed, exported, and paid in cash.

---

## Core Data Entities

### 1. Project
* **Fields:** Project Name, Client, Project Type, Location, Start Date, Estimated End Date, Project Status, Contract Value, Notes.

### 2. Client
* **Fields:** Client/Company Name, Contact Person, Phone/WhatsApp, Address, Notes.

### 3. Supplier
* **Fields:** Supplier/Store Name, Contact Person, Phone/WhatsApp, Address, Material Category Supplied, Notes.

### 4. Worker
* **Fields:** Worker Name, Worker Role/Type, Default Daily Wage, Phone Number, Assigned Project, Active/Inactive Status, Notes.

### 5. Worker Wage Recap
* **Fields:** Project, Wage Period/Week, Worker, Worker Role/Type, Daily Wage, Number of Work Days, Total Wage, Payment Method (Default: Cash), Payment Date, Payment Status (Paid/Unpaid), Notes.

### 6. Material Purchase
* **Fields:** Project, Supplier, Purchase Date, Material Name, Quantity, Unit, Unit Price, Total Price, Payment Status, Receipt/Photo Reference, Notes.

### 7. Weekly Finance Summary
* **Fields:** Week/Date Range, Project, Total Material Purchase, Total Worker Wage, Other Expenses, Total Project Expense, Income/Payment Received, Estimated Profit/Loss, Notes.

---

## User Roles

1. **Admin / System Owner:**
   * Full access to projects, clients, suppliers, material purchases, wage recaps, financial summaries, and website configurations.
2. **Mandor / Project Supervisor:**
   * Access to project workers, daily wage entries, and payment status updates.
3. **Finance / Admin Staff:**
   * Access to material purchases, weekly payroll summaries, and weekly financial recaps.

> [!NOTE]
> For the first MVP stage, a single admin account is acceptable, provided the structure permits role segregation in the future.

---

## Technical Architecture

* **VPS Target Environment:** Biznet Gio Neo Lite SS (1 vCPU, 2 GB RAM, 60 GB SSD)
* **Operating System:** Ubuntu Linux
* **Deployment Method:** Docker Compose (multi-container setup)
* **Services:**
  * **Odoo (v19.0 Community):** Main ERP base. Configured with optimized worker/memory limits to fit the 2 GB RAM environment.
  * **PostgreSQL (v15):** Persistent database using named docker volumes.
  * **Caddy:** Reverse proxy with automated SSL certificate provisioning.
  * **Docker Volumes:**
    * `odoo-db-data`: Postgres data persistence.
    * `odoo-web-data`: Odoo filestore (attachments, documents).
    * `caddy-data` & `caddy-config`: Caddy configurations and SSL cert storage.

---

## Deployment & First Run Instructions

### 1. Prerequisites Setup
If deploying on a fresh VPS, you can run the provided Docker installation script:
```bash
sudo ./scripts/install-docker-ubuntu.sh
```
This script installs Docker, Docker Compose, Fail2ban, and sets up UFW. Review the file [scripts/install-docker-ubuntu.sh](file:///home/aliceevr/projects/constructflow-erp/scripts/install-docker-ubuntu.sh) for details.

### 2. Environment Configuration
Copy the sample environment file to create your active `.env`:
```bash
cp .env.example .env
```
Open [.env](file:///home/aliceevr/projects/constructflow-erp/.env) and update the credentials:
```ini
DOMAIN=erp.yourdomain.com
POSTGRES_PASSWORD=YOUR_SECURE_PG_PASSWORD
ODOO_MASTER_PASSWORD=YOUR_SECURE_ODOO_ADMIN_PASSWORD
ODOO_DB_NAME=contractor_erp
```

### 3. Running the Infrastructure
Start the containers in detached mode:
```bash
docker compose pull
docker compose up -d
```
Verify that the services are running:
```bash
docker compose ps
```

### 4. Database Setup & Security Hardening
1. Navigate to `https://your-domain.com`.
2. Create the Odoo database using the master password and database name configured in your `.env`.
3. To secure the database manager page from unauthorized access, open [config/odoo.conf](file:///home/aliceevr/projects/constructflow-erp/config/odoo.conf).
4. Change `list_db = True` to `list_db = False`.
5. Restart the Odoo service:
   ```bash
   docker compose restart odoo
   ```

---

## Custom Module Management

The project uses a custom Odoo module skeleton located at [addons/contractor_wage_recap](file:///home/aliceevr/projects/constructflow-erp/addons/contractor_wage_recap).

To install or update the custom module after code changes:
```bash
# Force-update the custom module in the database
docker compose exec odoo odoo -d contractor_erp -u contractor_wage_recap --stop-after-init

# Restart the Odoo container to apply changes
docker compose restart odoo
```

---

## Backups

The automated backup script is located at [scripts/backup.sh](file:///home/aliceevr/projects/constructflow-erp/scripts/backup.sh). It dumps the PostgreSQL database and tars the Odoo filestore directory, saving them in the `backups/` directory.

To run a backup manually:
```bash
# Load environmental parameters and execute the backup script
source .env
./scripts/backup.sh
```
Files in the backup folder are ignored by git via [.gitignore](file:///home/aliceevr/projects/constructflow-erp/.gitignore) but the folder is preserved with [backups/.gitkeep](file:///home/aliceevr/projects/constructflow-erp/backups/.gitkeep). 

To set up a daily cron backup:
```bash
# Add this to crontab -e to run backup every midnight
0 0 * * * /bin/bash /home/aliceevr/projects/constructflow-erp/scripts/backup.sh >> /var/log/contractor_backup.log 2>&1
```

---

## MVP Success Criteria

The MVP is successful if:
1. **Public Website:** The company profile successfully renders details, service categories, project portfolios, clients, and has an interactive contact/WhatsApp CTA button.
2. **Contact Database:** Admin can record client, worker, and supplier contact lists.
3. **Project Management:** System supports logging projects with client assignments and statuses.
4. **Mandor Wage Recap:** Admin/Mandor can record daily wages, assign workers to projects, specify working days, automatically calculate weekly pay, and toggle paid/unpaid statuses.
5. **Material Purchase Records:** Admin can record material receipts, quantities, units, and supplier associations per project.
6. **Project Expenses & Weekly Summary:** Financial records generate combined weekly payroll and material expense summaries.
7. **VPS Stability:** Odoo, Postgres, and Caddy deploy and operate stably under Docker inside the 2 GB RAM VPS.

---

## Known Gaps & Future Considerations

These requirements must be gathered before full production launch:
* Official business logo and primary brand colors.
* Dedicated WhatsApp/business call number and email.
* Complete physical address of the company.
* High-quality photos of past project portfolios.
* Final verification of which project and client names may be displayed on the public website.
* Exact workflow approval states for weekly payroll release.

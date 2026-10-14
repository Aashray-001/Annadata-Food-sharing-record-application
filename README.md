# Annadata - Food Donation & Distribution System

A full-featured JavaFX desktop application with MySQL database connectivity for managing food donations, recipient claims, emergency aid requests, and daily food distribution services.

---

## 🌟 Key Features

### 1. Role-Based Authentication & Dashboards
- **Roles**: Donor, Recipient (NGO / Shelter / Individual), and System Admin.
- Password hashing with **BCrypt**.
- Role-specific navigation and tailored dashboard interfaces.

### 2. 🐕 Daily Food Distribution Services (Assigned Places)
- Daily and weekly assigned places for:
  - 🐕 **Dog Food Service** (street animal feeding, shelters)
  - 🏠 **Old Age Homes**
  - 🛕 **Temples & Religious Annadanam / Langar**
  - 🏫 **Orphanages**
  - 🍲 **Community Kitchens & Relief Centers**
  - 🏥 **Hospitals**
  - 🎓 **Schools**
- Interactive **Weekly Schedule Grid** (Monday–Sunday × Morning / Afternoon / Evening).
- Real-time **Today's Distribution** panel tracking delivery status (`Scheduled`, `Assigned`, `In Transit`, `Delivered`, `Completed`).

### 3. 🚨 Emergency Aid for Disaster Relief
- Dedicated section in the Recipient dashboard to request urgent aid for:
  - Natural calamities & flood/cyclone relief
  - Medical emergencies & community crises
- Priority urgency badges: 🔴 **Critical**, 🟠 **High**, 🟡 **Medium**.
- Donors and admins can view active emergency feeds and pledge assistance directly.

### 4. 📊 Donation Source Tracking & Analytics
- Every donation records its source:
  - 👤 **Individual**
  - 🏢 **Organization** (NGOs, restaurants, grocery stores, corporations)
  - 🏛️ **Government Bodies** (public distribution programs, state relief)
- Admin analytics with **JavaFX Pie Charts** (source breakdown percentage) and **Bar Charts** (monthly donation trends).

### 5. Donation Lifecycle & Expiry Alerts
- Status transitions: `Available` ➔ `Claimed` ➔ `Accepted` ➔ `Picked Up` ➔ `Completed`.
- Expiry tracking with visual highlights for donations nearing expiration within 24 hours.

---

## 📁 Project Structure

```
food-donation-system/
├── compile.bat                  # One-click Windows compile script
├── run.bat                      # One-click Windows launch script
├── sql/
│   └── schema.sql               # MySQL database schema & sample seed data
├── lib/                         # External libraries (pre-downloaded)
│   ├── javafx-base-21.0.2.jar
│   ├── javafx-controls-21.0.2.jar
│   ├── javafx-fxml-21.0.2.jar
│   ├── javafx-graphics-21.0.2.jar
│   ├── jbcrypt-0.4.jar
│   └── mysql-connector-j-8.4.0.jar
├── resources/
│   ├── css/
│   │   └── styles.css           # Custom JavaFX styling & theme
│   └── fxml/                    # FXML layouts for all views
│       ├── login.fxml
│       ├── register.fxml
│       ├── donor_dashboard.fxml
│       ├── recipient_dashboard.fxml
│       ├── admin_dashboard.fxml
│       ├── create_donation.fxml
│       ├── donation_details.fxml
│       ├── emergency_aid.fxml
│       ├── donation_charts.fxml
│       ├── distribution_places.fxml
│       ├── distribution_schedule.fxml
│       └── notifications.fxml
├── sql/
│   ├── schema.sql               # Full DB schema (auto-run on first launch)
│   └── dumps/                   # Per-table SQL dumps with all live data
│       ├── food_donation_db_users.sql
│       ├── food_donation_db_donations.sql
│       ├── food_donation_db_requests.sql
│       ├── food_donation_db_emergency_aids.sql
│       ├── food_donation_db_notifications.sql
│       ├── food_donation_db_distribution_places.sql
│       ├── food_donation_db_distribution_schedule.sql
│       └── food_donation_db_routines.sql
├── src/
│   ├── app/
│   │   └── Main.java            # App entry point
│   ├── db/
│   │   ├── DatabaseConnection.java
│   │   └── DatabaseInitializer.java
│   ├── model/                   # 7 Data models
│   ├── dao/                     # 7 Data Access Objects (JDBC)
│   ├── controller/              # FXML UI Controllers
│   └── util/                    # AlertUtil, PasswordUtil, SessionManager
└── out/                         # Compiled bytecode and assets
```

---

## ⚙️ Prerequisites & Setup

1. **Java JDK**: JDK 17 or higher (JDK 25 LTS is tested and verified).
2. **MySQL Server**: MySQL 8.0 or MariaDB running on port `3306`.
3. **Database Configuration**:
   - By default, the application connects to `localhost:3306` with user `root` and password `root`.
   - You can customize credentials by setting environment variables before running:
     ```shell
     set DB_URL=jdbc:mysql://localhost:3306/food_donation_db
     set DB_USER=your_username
     set DB_PASSWORD=your_password
     ```
   - On first launch, `DatabaseInitializer` will automatically run `sql/schema.sql` to create `food_donation_db`, all required tables, and seed initial places and the admin user!

---

## 🗄️ Importing the Database (For Team Members)

The `sql/dumps/` folder contains the **complete live database** with all tables and data.
Import it into your local MySQL before running the app:

### Option A — MySQL Workbench (GUI)
1. Open MySQL Workbench → connect with `root` / `root`
2. Go to **Server → Data Import**
3. Select **"Import from Self-Contained File"**
4. Import each file from the `sql/dumps/` folder one by one
5. Click **Start Import**

### Option B — Command Line (Fastest)
Open a terminal in the project folder and run:
```cmd
mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS food_donation_db;"
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_users.sql
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_distribution_places.sql
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_donations.sql
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_requests.sql
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_emergency_aids.sql
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_notifications.sql
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_distribution_schedule.sql
mysql -u root -proot food_donation_db < sql\dumps\food_donation_db_routines.sql
```

> If `mysql` is not recognized, use the full path:
> `"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"`

After importing, run `run.bat` — you will be logged in with the same data as the main system.



## 🚀 How to Run

### Quick Start (Windows)
Double-click or run:
```shell
run.bat
```

### Or Manually via Terminal:
```shell
# Recompile if you make changes:
cmd /c "javac --module-path lib --add-modules javafx.controls,javafx.fxml,javafx.graphics -cp "lib/*" -d out @sources.txt"

# Run application:
java --module-path lib --add-modules javafx.controls,javafx.fxml,javafx.graphics -cp "out;lib/*;resources" app.Main
```

---

## 🔑 Ready-to-Use Accounts

| Role | Email | Password | What You Can Test |
|---|---|---|---|
| **Admin** | `admin@Annadata.com` | `admin123` | View source analytics charts, weekly schedule matrix, manage places, and activate/deactivate users. |
| **Donor** | `donor@Annadata.com` | `donor123` | Post new food donations with source tracking, view your listings, review claim requests, and pledge emergency relief. |
| **Recipient** | `recipient@Annadata.com` | `recipient123` | Browse & search available food, claim donations with messages, view claim statuses, and post 🚨 Emergency Aid requests. |

*(You can also click **Register** on the login window to create any number of custom accounts!)*

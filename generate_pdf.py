import os
import subprocess
import markdown

md_file_path = r"C:\Users\Aashray\.gemini\antigravity\brain\2e3dc715-b47d-491a-a01f-0a1cfd7776ac\annadata_project_documentation.md"

with open(md_file_path, "r", encoding="utf-8") as f:
    base_md = f.read()

# Extended markdown with deep dive into Aashray's assigned topic
aashray_section = """

---

# 🌟 SPECIAL MODULE DEEP-DIVE: DONATIONS & CLAIM REQUESTS
### *Assigned Module for Aashray — Architecture, Code Walkthrough & Presentation Defense*

---

## 1. Overview of the Module
In the Annadata system, the **Donations and Claim Requests** module forms the core operational heart of the application. Without this module, food cannot be listed, discovered, requested, or transferred.

It fulfills the two fundamental user journeys:
1. **Donor Journey**: A donor lists surplus food with expiry time, quantity, category, and pickup details, monitors its status, and approves or rejects claim requests.
2. **Recipient Journey**: A verified recipient (shelter, community kitchen, or individual) browses available donations in real-time, submits claim requests with custom notes, and tracks claim approval.

---

## 2. The 8 Core Classes in Detail

### Class 1: `Donation.java` (Model Layer)
- **Role**: Plain Old Java Object (POJO) representing a row in the `donations` table.
- **Key Attributes**:
  - `id`: Unique identifier (auto-increment in MySQL).
  - `donorId`: Foreign key to `users(id)`.
  - `title`, `description`: Details of the food.
  - `category`: Category string (`cooked`, `raw`, `packaged`, `beverages`, `dog_food`, `other`).
  - `quantity`, `unit`: Measurement of food (e.g., `50 plates`, `20 kg`).
  - `expiryDate` (`LocalDateTime`): Crucial for food safety.
  - `pickupAddress`: Physical pickup location.
  - `sourceType` (`individual`, `organization`, `government`), `sourceName`.
  - `status`: Lifecycle state (`available`, `accepted`, `completed`, `expired`, `cancelled`).
  - `donorName`: Additional field populated during SQL `JOIN` with the `users` table for display.
- **Why it matters**: Encapsulates donation data so controllers and DAOs pass typed objects rather than loose strings or arrays.

---

### Class 2: `Request.java` (Model Layer)
- **Role**: POJO representing a claim request for a donation in the `requests` table.
- **Key Attributes**:
  - `id`: Primary key.
  - `donationId`: Foreign key to `donations(id)`.
  - `recipientId`: Foreign key to `users(id)`.
  - `status`: State of request (`pending`, `accepted`, `rejected`, `completed`).
  - `message`: Note from recipient explaining their requirement or logistics.
  - `createdAt`: Timestamp when request was submitted.
  - `donationTitle`, `donorName`, `recipientName`: Joined display fields for dashboards.
- **Why it matters**: Tracks the negotiation between donor and recipient before physical food transfer.

---

### Class 3: `DonationDAO.java` (Data Access Layer)
- **Role**: Handles all database operations related to the `donations` table using JDBC and `PreparedStatement`.
- **Key Methods**:
  1. `create(Donation d)`:
     - Executes `INSERT INTO donations (...) VALUES (?, ?, ...)`.
     - Sets parameters using `pstmt.setString()`, `pstmt.setInt()`, and converts `LocalDateTime` to `java.sql.Timestamp`.
  2. `findAvailable()`:
     - Executes:
       ```sql
       SELECT d.*, u.name as donor_name 
       FROM donations d 
       LEFT JOIN users u ON d.donor_id = u.id 
       WHERE d.status = 'available' AND d.expiry_date > NOW() 
       ORDER BY d.created_at DESC
       ```
     - Filters out expired food and already-claimed donations automatically at the database level!
  3. `findByDonor(int donorId)`:
     - Returns all donations created by a specific donor.
  4. `findById(int id)`:
     - Fetches complete details of a single donation joined with donor's name.
  5. `updateStatus(int id, String status)`:
     - Transitions donation state (e.g., from `available` to `accepted` or `completed`).
  6. `countBySourceType()` & `countMonthlyBySource()`:
     - Aggregates donation stats for the Admin analytics dashboard.
- **Why it matters**: Isolates all SQL queries so that if database schema or driver changes, the UI code remains untouched.

---

### Class 4: `RequestDAO.java` (Data Access Layer)
- **Role**: Manages all SQL persistence and retrieval for claim requests.
- **Key Methods**:
  1. `create(Request r)`:
     - Executes `INSERT INTO requests (donation_id, recipient_id, status, message, created_at) VALUES (?, ?, ?, ?, ?)`.
     - Defaults status to `'pending'`.
  2. `findByDonation(int donationId)`:
     - Executes `SELECT r.*, u.name as recipient_name FROM requests r JOIN users u ON r.recipient_id = u.id WHERE r.donation_id = ?`.
     - Allows the donor to see who requested their food and read their messages.
  3. `findByRecipient(int recipientId)`:
     - Executes a multi-table JOIN across `requests`, `donations`, and `users` so the recipient sees donation titles and donor names in their "My Claims" screen.
  4. `updateStatus(int id, String status)`:
     - Changes request status to `'accepted'` or `'rejected'`.
- **Why it matters**: Protects against SQL injection using parameterized queries while maintaining referential integrity.

---

### Class 5: `CreateDonationController.java` (Controller Layer)
- **Role**: Backing controller for `create_donation.fxml`.
- **How it works**:
  - `initialize()`: Populates dropdown ComboBoxes for `categoryCombo` (`cooked`, `raw`, `packaged`, etc.) and `sourceTypeCombo`. Auto-populates donor address and name from `SessionManager.getCurrentUser()`.
  - `handleSubmit()`:
    1. Extracts values from `titleField`, `categoryCombo`, `quantityField`, `expiryPicker`, etc.
    2. Validates that no required fields are blank and validates that quantity is numeric (`Integer.parseInt`).
    3. Constructs `Donation` object with current donor's user ID from `SessionManager`.
    4. Calls `donationDAO.create(d)`.
    5. Displays user-friendly confirmation using `AlertUtil.showInformation()` and resets form fields.
  - `handleCancel()`: Clears the input fields.

---

### Class 6: `DonationDetailsController.java` (Controller Layer)
- **Role**: Adaptive details view for both Donors and Recipients (`donation_details.fxml`).
- **Dynamic Dual-Role Logic**:
  - Receives the donation object and current role via `setDonation(Donation d, String role)`.
  - **When viewed by a Recipient**:
    - Shows donation specs (category, quantity, expiry, donor source).
    - Enables the `recipientBox` with a message input field and a "Claim This Donation" button.
    - If status is not `'available'`, disables the claim button.
    - When claimed: calls `requestDAO.create()`, disables button, and creates an in-app notification for the donor via `NotificationDAO`.
  - **When viewed by a Donor**:
    - Enables the `donorBox` and calls `loadRequestsForDonor()`.
    - Populates all incoming claim requests with `Accept` and `Reject` action buttons.
    - Accepting updates both `requests.status = 'accepted'` and `donations.status = 'accepted'`.
    - Provides options to "Mark Completed" or "Cancel Donation".

---

### Class 7: `DonorDashboardController.java` (Controller Layer)
- **Role**: Coordinates the main interface for logged-in donors (`donor_dashboard.fxml`).
- **Key Responsibilities**:
  - Displays welcome message with donor's name.
  - Shows real-time unread notification count badge via `notificationDAO.countUnread()`.
  - Generates stat cards: Total Donations, Active Donations, Completed, Expiring Soon.
  - Renders recent donations dynamically as styled cards with action buttons (View Details, Edit, Cancel).
  - Navigation handlers:
    - `showCreateDonation()`: Loads `create_donation.fxml` into central `contentArea`.
    - `showMyDonations()`: Queries `donationDAO.findByDonor(userId)` and builds donation cards.
    - `showTodaySchedule()`, `showEmergencies()`, `showNotifications()`.
    - `handleLogout()`: Clears `SessionManager` and redirects to login screen.

---

### Class 8: `RecipientDashboardController.java` (Controller Layer)
- **Role**: Coordinates the primary interface for recipients/NGOs (`recipient_dashboard.fxml`).
- **Key Responsibilities**:
  - `showBrowse()`:
    - Calls `donationDAO.findAvailable()` to fetch all non-expired, unreserved donations.
    - Provides real-time keyword search and category filtering.
    - Renders responsive cards displaying food category badge, quantity, expiry time, and pickup address.
    - Clicking "View Details" opens `DonationDetailsController` with recipient capabilities.
  - `showMyClaims()`:
    - Calls `requestDAO.findByRecipient(userId)` to display all claims made by this recipient.
    - Displays claim status badges (`PENDING`, `ACCEPTED`, `REJECTED`).
  - Access to Emergency Aid requests and weekly distribution schedule.

---

## 3. End-to-End Sequence Diagram

```
DONOR                       CONTROLLER & DAO                  MYSQL DATABASE
  │                                │                                │
  │── Fill Form & Click Submit ───>│                                │
  │   (CreateDonationController)   │── PreparedStatement INSERT ──>│ (donations table)
  │                                │<── Insert OK ──────────────────│
  │<── "Donation Created" Alert ───│                                │
  │                                │                                │
RECIPIENT                          │                                │
  │── Opens Browse Donations ─────>│                                │
  │   (RecipientDashboardController│── SELECT available & not exp ─>│
  │                                │<── List of Donations ──────────│
  │<── Displays Cards ─────────────│                                │
  │                                │                                │
  │── Enters Note & Clicks Claim ─>│                                │
  │   (DonationDetailsController)  │── INSERT request (status=pend)─>│ (requests table)
  │                                │── INSERT notification ─────────>│ (notifications table)
  │<── "Claim Requested" Alert ────│                                │
  │                                │                                │
DONOR                              │                                │
  │── Opens Donation Details ─────>│                                │
  │   (DonationDetailsController)  │── SELECT requests for donation>│
  │                                │<── Returns pending requests ───│
  │<── Shows "Accept" Button ──────│                                │
  │── Clicks "Accept" ────────────>│                                │
  │                                │── UPDATE requests (accepted) ──>│
  │                                │── UPDATE donations (accepted) ─>│
  │<── Refreshes View ─────────────│                                │
```

---

## 4. What to Say in Your Presentation & Viva

### 1. Elevator Pitch of Your Module:
> *"My module is 'Donations and Claim Requests' — it is the primary business engine of Annadata. It governs how food items are created, validated, published, searched, claimed by recipients, and approved by donors. I implemented 4 controllers, 2 DAOs, and 2 Model classes managing the complete lifecycle of a food donation."*

### 2. If Asked: "How do you ensure food safety and prevent expired food from being claimed?"
> *"In `DonationDAO.findAvailable()`, we run a condition `WHERE status = 'available' AND expiry_date > NOW()`. This ensures expired donations are automatically filtered out at the database query level, preventing recipients from requesting outdated food."*

### 3. If Asked: "How do you handle role-based behavior in the details view?"
> *"Instead of creating two duplicate screens for donors and recipients, `DonationDetailsController` takes a `viewerRole` parameter in `setDonation()`. If the user is a recipient, it shows the claim form and message box. If the user is a donor, it loads all pending requests with 'Accept' and 'Reject' action buttons."*

### 4. If Asked: "Why use PreparedStatements in DonationDAO and RequestDAO?"
> *"Every query uses `PreparedStatement` with parameterized placeholders `?`. This protects the application against SQL injection attacks and improves performance because the database engine pre-compiles the SQL execution plan."*

"""

full_content = base_md + aashray_section

# Convert markdown to HTML
html_body = markdown.markdown(full_content, extensions=['tables', 'fenced_code'])

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Annadata - Complete Documentation and Aashray Topics</title>
<style>
    @page {{
        size: A4;
        margin: 18mm 16mm 18mm 16mm;
        @bottom-right {{
            content: counter(page);
            font-size: 9pt;
            color: #666;
        }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #24292e;
        line-height: 1.55;
        font-size: 10.5pt;
        background: #fff;
    }}
    h1 {{
        color: #1b5e20;
        border-bottom: 2.5px solid #2e7d32;
        padding-bottom: 8px;
        font-size: 20pt;
        margin-top: 24pt;
        page-break-after: avoid;
    }}
    h2 {{
        color: #2e7d32;
        border-bottom: 1px solid #c8e6c9;
        padding-bottom: 5px;
        font-size: 15pt;
        margin-top: 18pt;
        page-break-after: avoid;
    }}
    h3 {{
        color: #388e3c;
        font-size: 12pt;
        margin-top: 14pt;
        page-break-after: avoid;
    }}
    h4 {{
        font-size: 11pt;
        color: #333;
        page-break-after: avoid;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12pt 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }}
    th, td {{
        border: 1px solid #d0d7de;
        padding: 6px 10px;
        text-align: left;
    }}
    th {{
        background-color: #e8f5e9;
        color: #1b5e20;
        font-weight: 600;
    }}
    tr:nth-child(even) {{
        background-color: #f9fbf9;
    }}
    pre {{
        background-color: #f6f8fa;
        border: 1px solid #d0d7de;
        border-radius: 6px;
        padding: 10px 12px;
        overflow-x: auto;
        font-size: 9pt;
        line-height: 1.4;
        page-break-inside: avoid;
    }}
    code {{
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        background-color: rgba(175, 184, 193, 0.2);
        padding: 0.15em 0.35em;
        border-radius: 4px;
        font-size: 9pt;
    }}
    pre code {{
        background-color: transparent;
        padding: 0;
    }}
    blockquote {{
        border-left: 4px solid #4caf50;
        margin: 10pt 0;
        padding: 6pt 14pt;
        background: #f1f8e9;
        color: #2e7d32;
        page-break-inside: avoid;
    }}
    hr {{
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 20pt 0;
    }}
    ul, ol {{
        padding-left: 20px;
    }}
    li {{
        margin-bottom: 4px;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

html_out_path = r"C:\Users\Aashray\.gemini\antigravity\scratch\food-donation-system\presentation_doc.html"
with open(html_out_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("HTML created successfully. Generating PDF via Chrome headless...")

pdf_out_system = r"C:\Users\Aashray\.gemini\antigravity\scratch\food-donation-system\Annadata_Complete_Guide_and_Aashray_Topics.pdf"
desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
pdf_out_desktop = os.path.join(desktop_dir, "Annadata_Complete_Guide_and_Aashray_Topics.pdf")

chrome_cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_out_system}",
    html_out_path
]

res = subprocess.run(chrome_cmd, capture_output=True, text=True)
print("Chrome return code:", res.returncode)

if os.path.exists(pdf_out_system):
    print("PDF generated successfully at:", pdf_out_system)
    # Also copy to Desktop for instant download/access
    import shutil
    shutil.copyfile(pdf_out_system, pdf_out_desktop)
    print("PDF also copied to Desktop at:", pdf_out_desktop)
else:
    print("PDF generation failed.")
    print("Stderr:", res.stderr)

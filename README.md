# Hotel Reservation System (HRS)

A Flask-based Hotel Reservation System connecting to a remote MySQL database.

## Setup

1.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit `.env` and fill in your MySQL database credentials.

4.  **Run the Application**:
    ```bash
    flask run
    # OR
    python run.py
    ```

5.  **Seed Data (Optional)**:
    To populate the database with initial data (Admin user, Rooms, Customers):
    ```bash
    python seed.py
    ```

## Usage

*   **Public Booking**: Access `http://localhost:5000/` to view rooms and make reservations.
*   **Admin Panel**: Access `http://localhost:5000/admin/login`.
    *   Default Admin Credentials (if seeded):
        *   Username: `admin`
        *   Password: `admin123`

## Project Structure

*   `app/`: Application source code.
    *   `models.py`: Database models.
    *   `routes/`: API and Frontend routes.
*   `static/`: CSS and JavaScript files.
*   `templates/`: HTML templates.
*   `run.py`: Entry point.

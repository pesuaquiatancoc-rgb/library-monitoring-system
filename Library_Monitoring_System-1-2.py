from datetime import datetime, timedelta
import re

inventory = {
    "011": {"title": "Two Birds, One Stone", "Available": 2, "Borrowed": 0},
    "022": {"title": "The Great Gatsby", "Available": 1, "Borrowed": 0},
    "033": {"title": "1984", "Available": 2, "Borrowed": 0},
    "044": {"title": "How To Feel Alive", "Available": 0, "Borrowed": 1},
    "055": {"title": "Second Option", "Available": 1, "Borrowed": 0},
    "066": {"title": "Modern Mathematics", "Available": 5, "Borrowed": 0},
    "077": {"title": "Introduction to Python Programming", "Available": 2, "Borrowed": 1},
    "088": {"title": "How To Think Like A Genius", "Available": 4, "Borrowed": 1},
}

users = {
    "L000-1": {"name": "Xyle Kirjie", "password": "asdwasdwasdw123", "role": "librarian"},
    "02-2627-012321": {"name": "Jan Paul", "password": "qwerty123", "role": "student", "student_id": "00-0000-000001"},
    "T001-1": {"name": "Michael Jackson", "password": "pass123", "role": "teacher"},
    "T001-2": {"name": "Louise Antonette", "password": "Louise123xd", "role": "teacher"}
}

borrow_requests = {
    "02-2627-012321": [{
        'book_id': '022', 
        'title': 'The Great Gatsby', 
        'timestamp': datetime.strptime("2026-10-11 09:30", "%Y-%m-%d %H:%M"), 
        'status': 'Pending'
    }],
}

borrow_history = {
    "02-2627-012321": [{'book_id': '044', 'title': 'How To Feel Alive', 'timestamp': datetime.strptime("2026-9-18 09:30", "%Y-%m-%d %H:%M"), 'status': 'Borrowed'}],
    "T001-1": [{'book_id': '088', 'title': 'How To Think Like A Genius', 'timestamp': datetime.strptime("2026-9-19 14:15", "%Y-%m-%d %H:%M"), 'status': 'Borrowed'}],
    "T001-2": [{'book_id': '077', 'title': 'Introduction to Python Programming', 'timestamp': datetime.strptime("2026-9-20 11:00", "%Y-%m-%d %H:%M"), 'status': 'Borrowed'}]
}


password_pattern = r"(?=.*[A-Za-z])(?=.*\d).{6,}"  
title_pattern = r"^[A-Za-z0-9][A-Za-z0-9\s,.:;!?\-()]*$"  
quantity_pattern = r"^[1-9]\d*$"  
id_patterns = {
    "student": r"^\d{2}-\d{4}-\d{6}$",  
    "teacher": r"^T\d{3}-\d$",    
    "librarian": r"^L\d{3}-\d$"   
}


def normalize_student_id(student_id):
    """Normalize common dash characters and surrounding spaces in student IDs."""
    student_id = (student_id or "").strip()
    student_id = re.sub(r"[\u2010-\u2015\u2212]", "-", student_id)
    student_id = re.sub(r"\s*-\s*", "-", student_id)
    return student_id


def is_valid_student_id(student_id):
    """Accept student IDs only in the format 00-0000-000000."""
    return re.fullmatch(id_patterns["student"], normalize_student_id(student_id)) is not None



def find_book(query):
    """Checks if a book title exists in the inventory (case-insensitive)."""
    query = query.strip()
    if query in inventory:
        return query
    for book_id, data in inventory.items():
        if data["title"].lower() == query.lower():
            return book_id
    return None

def register(role_choice, id_number, name, password, student_id=None):
    """Register a user. Student system IDs are generated automatically."""

    role_map = {"1": "student", "2": "teacher", "3": "librarian"}
    if role_choice not in role_map:
        print("Error: Invalid role choice.")
        return False
    role = role_map[role_choice]

    if role == "student":
        student_id = normalize_student_id(student_id)
        if not is_valid_student_id(student_id):
            print("INVALID ID, TRY AGAIN")
            return False
        if any(u.get("student_id") == student_id for u in users.values()):
            print("Error: Student ID already registered.")
            return False
        id_number = student_id

    else:
        prefix = "T" if role == "teacher" else "L"
        number = 1
        while f"{prefix}{number:03d}-1" in users:
            number += 1
        id_number = f"{prefix}{number:03d}-1"

    if id_number in users:
        print("Error: ID Number already exists.")
        return False

    name = name.strip()
    if not name:
        print("Error: Name cannot be empty.")
        return False

    if not re.fullmatch(password_pattern, password):
        print("Error: Password must be at least 6 characters long and contain both letters and numbers.")
        return False

    users[id_number] = {"name": name, "password": password, "role": role}
    if role == "student":
        users[id_number]["student_id"] = student_id
    print(f"Success! Registered {name} (ID: {id_number}) as a {role}.")
    return True

def login(role_choice, login_name, password):
    """Authenticate students by registered Student ID, and staff by registered name."""
    role_map = {"1": "student", "2": "teacher", "3": "librarian"}
    role = role_map.get(str(role_choice).strip())
    login_name = (login_name or "").strip()

    if role == "student":
        normalized_id = normalize_student_id(login_name)
        user_id = next(
            (stored_id for stored_id, account in users.items()
             if account.get("role") == "student"
             and normalize_student_id(stored_id) == normalized_id),
            None,
        
        )
    elif role in ("teacher", "librarian"):
        user_id = next(
            (stored_id for stored_id, account in users.items()
             if account.get("role") == role
             and account.get("name", "").strip().casefold() == login_name.casefold()),
            None,
        )
    else:
        print("Error: Invalid role choice.")
        return None

    user = users.get(user_id) if user_id is not None else None
    if not user or user.get("password") != password:
        print(f"INVALID {role.upper()} NAME/ID OR PASSWORD, TRY AGAIN")
        return None

    print(f"Login successful. Welcome, {user['name']} ({user['role']})!")
    return user_id, user["role"]

# --- LIBRARIAN ACTIONS ---
def add_book(book_id, title, quantity, role):
    if role != "librarian":
        print(" Access Denied: Only librarians can add books.")
        return False
    book_id = book_id.strip()
    title = title.strip()
    
    if not re.match(title_pattern, title):
        print(" Error: Book title must contain only letters or/with numbers.")
        return False
    if not re.match(quantity_pattern, str(quantity)):
        print(" Error: Quantity must be a positive number.")
        return False
    quantity = int(quantity)
    
    if book_id in inventory:
        existing_title = inventory[book_id]["title"]
        if existing_title.lower() != title.lower():
            print(f" Error: Book ID '{book_id}' already exists and belongs to '{existing_title}', not '{title}'.")
            return False
        else:
            inventory[book_id]["Available"] += quantity
            print(f" Library updated: Added {quantity} copies to '{existing_title}' (ID: {book_id}).")
            return True

    for existing_id, data in inventory.items():
        if data["title"].lower() == title.lower():
            print(f" Error: Book title '{title}' already exists under Book ID '{existing_id}'.")
            return False

    inventory[book_id] = {"title": title, "Available": quantity, "Borrowed": 0}
    print(f" Library updated: '{title}' added with Book ID {book_id}.")
    return True
   
def remove_book(book_id, quantity, role):
    if role != "librarian":
        print(" Access Denied: Only librarians can remove books.")
        return False
    book_id = book_id.strip()
    if book_id not in inventory:
        print(" Error: Book ID does not exist.")
        return False
        
    if not re.match(quantity_pattern, str(quantity)):
        print(" Error: Quantity must be a positive number.")
        return False
    quantity = int(quantity)
    
    if inventory[book_id]["Available"] >= quantity:
        inventory[book_id]["Available"] -= quantity
        title = inventory[book_id]["title"]
        if inventory[book_id]["Available"] == 0 and inventory[book_id]["Borrowed"] == 0:
            del inventory[book_id]
            print(f" Library updated: '{title}' (ID: {book_id}) has been completely removed.")
            return True
        else:
            print(f" Library updated: Removed {quantity} copies of '{title}'. Available: {inventory[book_id]['Available']}")
            return True
    else:
        print(" Error: Not enough available copies to remove.")
        return False

def view_requests(role):
    if role != "librarian":
        print(" Access Denied.")
        return False
    print("\n--- BOOK REQUESTS ---")
    print("=" * 135)
    print(f"{'ID Number':<18} | {'Name':<20} | {'Book ID':<10} | {'Title':<30} | {'Status':<10} | {'Timestamp':<20} |")
    print("=" * 135)
    has_reqs = False
    for u_id, req_list in borrow_requests.items():
        name = users.get(u_id, {}).get("name", "Unknown")
        for req in req_list:
            print(f"{u_id:<18} | {name:<20} | {req['book_id']:<10} | {req['title']:<30} | {req['status']:<10} | {req['timestamp'].strftime('%Y-%m-%d %H:%M'):<20} |")
            has_reqs = True
    if not has_reqs:
        print(" No pending book requests.")
    print("=" * 135)
    return True

def accept_borrow_request(target_id, book_id, role):
    if role != "librarian":
        print(" Access Denied.")
        return False
    target_id = target_id.strip()
    book_id = book_id.strip()
    
    if target_id not in borrow_requests:
        print(" Error: No requests found for this ID Number.")
        return False
        
    found_req = None
    for req in borrow_requests[target_id]:
        if req['book_id'] == book_id and req['status'] == 'Pending':
            found_req = req
            break
            
    if not found_req:
        print(" Error: Pending request not found for this Book ID.")
        return False
        
    if book_id in inventory and inventory[book_id]["Available"] > 0:
        inventory[book_id]["Available"] -= 1
        inventory[book_id]["Borrowed"] += 1
        accepted_time = datetime.now()
        found_req['status'] = 'Approved'
        found_req['approved_timestamp'] = accepted_time
        found_req['timestamp'] = accepted_time
        found_req['return_date'] = (accepted_time + timedelta(days=7)).date()
        
        borrow_time = accepted_time
        borrow_history.setdefault(target_id, []).append({
            "book_id": book_id,
            "title": inventory[book_id]["title"], 
            "timestamp": borrow_time,
            "borrowed_timestamp": borrow_time,
            "status": "Borrowed"
        })
        print(f" Success! Request approved for {users[target_id]['name']} ({target_id}).")
        return True
    else:
        print(" Error: Book is unavailable.")
        return False

def view_user_history(current_id, target_id, role):
    """Show request, approval, borrowing, and return activities with their actual timestamps."""
    if role != "librarian" and current_id != target_id:
        print(" Access Denied.")
        return False

    name = users.get(target_id, {}).get("name", target_id)
    activities = []

    for request in borrow_requests.get(target_id, []):
        book_id = request.get("book_id", "")
        title = request.get("title", "")
        requested_at = request.get("requested_timestamp", request.get("timestamp"))
        status = request.get("status", "").casefold()
        if status == "pending" and requested_at:
            activities.append((book_id, title, requested_at, "PENDING"))
        elif status == "approved":
            approved_at = request.get("approved_timestamp", request.get("timestamp"))
            if approved_at:
                activities.append((book_id, title, approved_at, "APPROVED"))

    for record in borrow_history.get(target_id, []):
        status = record.get("status", "").casefold()
        if status == "returned":
            when = record.get("returned_timestamp", record.get("timestamp"))
            label = "RETURNED"
        else:
            when = record.get("borrowed_timestamp", record.get("timestamp"))
            label = "BORROWED"
        if when:
            activities.append((record.get("book_id", ""), record.get("title", ""), when, label))

    activities.sort(key=lambda item: item[2])
    print(f"\n--- MY HISTORY: {name} ({target_id}) ---")
    print("=" * 100)
    print(f"{'BOOK ID':<10} | {'BOOK TITLE':<35} | {'DATE & TIME':<19} | {'STATUS':<10} |")
    print("=" * 100)
    for book_id, title, when, status in activities:
        print(f"{book_id:<10} | {title:<35} | {when.strftime('%d/%m/%y %H:%M'):<19} | {status:<10} |")
    if not activities:
        print(" No request, borrowing, or returning history found for this user.")
    print("=" * 100)
    return True

def view_all_history(role):
    if role != "librarian":
        print(" Access Denied.")
        return False
    print(f"\n--- ALL BORROWING & RETURNING RECORDS ---")
    print("=" * 125)
    print(f"{'ID Number':<15} | {'Name':<20} | {'Book Title':<40} | {'Status':<10} | {'Date':<20} |")
    print("=" * 125)
    for u_id, history in borrow_history.items():
        name = users.get(u_id, {}).get("name", "Unknown")
        if not history:
            print(f"{u_id:<15} | {name:<20} | {'No borrowing or returning history':<40} | {'-':<10} | {'-':<20} |")
        else:
            for record in history:
                print(f"{u_id:<15} | {name:<20} | {record['title']:<40} | {record['status']:<10} | {record['timestamp'].strftime('%Y-%m-%d %H:%M'):<20} |")
    print("="*125)
    return True

def view_inventory():
    print("\n--- LIBRARY INVENTORY ---")
    print("=" * 76)
    print(f"{'Book ID':<10} | {'Book Title':<35} | {'Available':<10} | {'Borrowed':<10} |")
    print("=" * 76)
    for b_id, book in inventory.items():
        print(f"{b_id:<10} | {book['title']:<35} | {book['Available']:<10} | {book['Borrowed']:<10} |")
    print("=" * 76)
    return True

# --- STUDENT & TEACHER ACTIONS ---
def view_available_books():
    print("\n--- AVAILABLE BOOKS ---")
    print("=" * 63)
    print(f"{'Book ID':<10} | {'Book Title':<35} | {'Available':<10} | ")
    print("=" * 63)
    found = False
    for b_id, book in inventory.items():
        if book["Available"] > 0:
            print(f"{b_id:<10} | {book['title']:<35} | {book['Available']:<10} | ")
            found = True
    if not found:
        print(" No books available.")
    print("=" * 63)
    return True

def view_my_requests(user_id):
    """Display request status only, with the automatically calculated return deadline."""
    print("\n--- MY BOOK REQUEST ---")
    print("=" * 100)
    print("STATUS:")
    requests_list = borrow_requests.get(user_id, [])
    if not requests_list:
        print("You have no book requests.")
    for request in requests_list:
        status = request.get("status", "").casefold()
        title = request.get("title", "the requested book").upper()
        if status == "approved":
            approved_at = request.get("approved_timestamp", request.get("timestamp"))
            deadline = request.get("return_date")
            if approved_at:
                deadline = (approved_at + timedelta(days=7)).date()
                request["return_date"] = deadline
            if deadline:
                print(f"YOUR REQUEST FOR [{title}] HAS BEEN APPROVED. PLEASE RETURN THE BOOK BEFORE {deadline.strftime('%d/%m/%y')}.")
            else:
                print(f"YOUR REQUEST FOR [{title}] HAS BEEN APPROVED.")
        elif status == "pending":
            print(f"YOUR REQUEST FOR [{title}] IS PENDING LIBRARIAN APPROVAL.")
        else:
            print(f"YOUR REQUEST FOR [{title}] STATUS: {request.get('status', 'Unknown').upper()}.")
    print("=" * 100)
    return True

def request_book(user_id, query, role):
    if role not in ["student", "teacher"]:
        print(" Access Denied.")
        return False
    book_id = find_book(query)
    
    if book_id and inventory[book_id]["Available"] > 0:
        if any(req["book_id"] == book_id and req["status"] == "Pending"
               for req in borrow_requests.get(user_id, [])):
            print(" You already have a pending request for this book.")
            return False
        requested_at = datetime.now()
        borrow_requests.setdefault(user_id, []).append({
            "book_id": book_id,
            "title": inventory[book_id]["title"],
            "timestamp": requested_at,
            "requested_timestamp": requested_at,
            "status": "Pending"
        })
        print(f" Success! Request for '{inventory[book_id]['title']}' submitted.")
        return True
    else:
        print(" Sorry, that book ID/title is invalid or unavailable.")
        return False
    

def return_book(user_id, title, role):
    if not title:
        print(" Error: Book title cannot be empty.")
        return False

    if role not in ["student", "teacher"]:
        print(" Access Denied: Only students and teachers can return books.")
        return False
        
    matched_title = find_book(title)
    if not matched_title or inventory[matched_title]["Borrowed"] <= 0:
        print(" Error: This book is not currently marked as borrowed.")
        return False

    found_record = next(
        (r for r in borrow_history.get(user_id, []) 
         if r.get("book_id") == matched_title and r["status"] == "Borrowed"), 
        None
    )

    if not found_record:
        print(" Error: You do not have an active borrow record for this book.")
        return False

    inventory[matched_title]["Available"] += 1
    inventory[matched_title]["Borrowed"] -= 1
    
    return_time = datetime.now()
    found_record['status'] = 'Returned'
    found_record['returned_timestamp'] = return_time
    found_record['timestamp'] = return_time

    book_title = inventory[matched_title]["title"]
    print(f" Success! You returned '{book_title}' at {return_time.strftime('%Y-%m-%d %H:%M')}.")
    return True


def main():
    while True:
        print("\n=== LIBRARY MONITORING SYSTEM ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()
            
        if choice == "1":
            print("\nSelect a role first:")
            print("1. Student")
            print("2. Teacher")
            print("3. Librarian")
            
            while True:
                role_choice = input("Choose role (1-3): ").strip()
                if role_choice in ("1", "2", "3"):
                    break
                print("Error: Please choose 1, 2, or 3.")
                
            student_id = None
            if role_choice == "1":
                while True:
                    student_id = normalize_student_id(input("Enter Student ID (e.g., 02-2627-000000): "))
                    if is_valid_student_id(student_id):
                        break
                    print("INVALID ID, TRY AGAIN")
                id_number = None  
            else:
                id_number = None  
            name = input("Enter Full Name: ").strip()
            password = input("Enter password: ").strip()

            register(role_choice, id_number, name, password, student_id)

        elif choice == "2":
            print("\nSelect a role to log in:")
            print("1. Student")
            print("2. Teacher")
            print("3. Librarian")
            role_choice = input("Choose role (1-3): ").strip()

            if role_choice == "1":
                login_name = input("Enter Student ID: ").strip()
            elif role_choice in ("2", "3"):
                login_name = input("Enter registered full name: ").strip()
            else:
                print("Error: Please choose 1, 2, or 3.")
                continue

            password = input("Enter password: ").strip()
            login_result = login(role_choice, login_name, password)
            if login_result is None:
                continue

            logged_id, role = login_result
                
            if role == "librarian":
                while True:
                    print("\n--- LIBRARIAN MENU ---")
                    print("1. View Inventory")
                    print("2. Add Book")
                    print("3. Remove Book")
                    print("4. View Requests")
                    print("5. Accept Borrow Request")
                    print("6. View User History")
                    print("7. View All History")
                    print("8. Logout")
                    lib_choice = input("Choose an option (1-8): ").strip()
                        
                    if lib_choice == "1":
                        view_inventory()
                    elif lib_choice == "2":
                        b_id = input("Enter Book ID (e.g., 012): ").strip()
                        title = input("Enter book title: ").strip()
                        qty = input("Enter quantity: ").strip()
                        add_book(b_id, title, qty, role)
                    elif lib_choice == "3":
                        b_id = input("Enter Book ID to remove: ").strip()
                        qty = input("Enter quantity: ").strip()
                        remove_book(b_id, qty, role)
                    elif lib_choice == "4":
                        view_requests(role)
                    elif lib_choice == "5":
                        target_id = input("Enter requester's ID Number: ").strip()
                        b_id = input("Enter Book ID to accept: ").strip()
                        accept_borrow_request(target_id, b_id, role)
                    elif lib_choice == "6":  
                        target_id = input("Enter user's ID Number to check history: ").strip()
                        view_user_history(logged_id, target_id, role)
                    elif lib_choice == "7":
                        view_all_history(role)
                    elif lib_choice == "8":
                        print("Logging out...")
                        break
                    else:
                        print("Invalid choice. Try again.")

            elif role in ["student", "teacher"]:
                menu_title = "--- STUDENT MENU ---" if role == "student" else "--- TEACHER MENU ---"
                while True:
                    print("\n" + menu_title)
                    print("1. View Available Books")
                    print("2. Request Book (by ID or Title)")
                    print("3. View My Book Requests")
                    print("4. Return Book (by ID or Title)")
                    print("5. View My History")
                    print("6. Logout")
                    user_choice = input("Choose an option (1-6): ").strip()
                        
                    if user_choice == "1":
                        view_available_books()
                    elif user_choice == "2":
                        query = input("Enter Book ID or title to request: ").strip()
                        request_book(logged_id, query, role)
                    elif user_choice == "3":
                        view_my_requests(logged_id)
                    elif user_choice == "4":
                        query = input("Enter Book ID or title to return: ").strip()
                        return_book(logged_id, query, role)
                    elif user_choice == "5":
                        view_user_history(logged_id, logged_id, role)
                    elif user_choice == "6":
                        print("Logging out...")
                        break
                    else:
                        print("Invalid choice. Try again.")
                            
        elif choice == "3":
            print("Exiting program. Thank you!")
            break
        else:
            print("Invalid option. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
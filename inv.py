import sqlite3
from colorama import init, Fore, Style

init(autoreset=True)
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS boxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    box_id INTEGER,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (box_id) REFERENCES boxes(id)
)
""")
conn.commit()

def add_box():
    name = input("Enter box name: ").strip()
    cursor.execute("INSERT INTO boxes (name) VALUES (?)", (name,))
    conn.commit()
    print(Fore.GREEN + "Box added successfully.")

def delete_box():
    list_boxes()
    box_id = input("Enter box ID to delete: ").strip()
    cursor.execute("DELETE FROM boxes WHERE id = ?", (box_id,))
    cursor.execute("DELETE FROM items WHERE box_id = ?", (box_id,))
    conn.commit()
    print(Fore.RED + "Box and its items deleted.")

def add_item():
    list_boxes()
    box_id = input("Enter box ID: ").strip()
    name = input("Enter item name: ").strip()
    quantity = input("Enter quantity (default 1): ").strip()
    quantity = int(quantity) if quantity.isdigit() else 1
    cursor.execute("INSERT INTO items (name, box_id, quantity) VALUES (?, ?, ?)", (name, box_id, quantity))
    conn.commit()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.GREEN + "Item added.")

def delete_item():
    list_items()
    item_id = input("Enter item ID to delete: ").strip()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.RED + "Item deleted.")

def list_boxes():
    cursor.execute("SELECT id, name FROM boxes")
    boxes = cursor.fetchall()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.CYAN + "\nBoxes:")
    for box in boxes:
        print(f"{Fore.MAGENTA}[{box[0]:>4}]{Style.RESET_ALL} {box[1]}")
    if not boxes:
        print(Fore.YELLOW + "\n" + "=" * 30)
        print(Fore.YELLOW + "No boxes found.")

def list_items():
    cursor.execute("""
    SELECT items.id, items.name, boxes.name, items.quantity
    FROM items
    LEFT JOIN boxes ON items.box_id = boxes.id
    """)
    items = cursor.fetchall()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.CYAN + "\nItems:")
    for item in items:
        item_id = f"[{item[0]:>4}]"
        name = f"{item[1]:<40}"
        quantity = f"{item[3]:>4}"
        print(f"{Fore.MAGENTA}{item_id}{Style.RESET_ALL} {name} | {Fore.BLUE}{quantity}{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}(Box: {item[2]})")
    if not items:
        print(Fore.YELLOW + "\n" + "=" * 30)
        print(Fore.YELLOW + "No items found.")

def search_box():
    keyword = input("Search box name: ").strip()
    cursor.execute("SELECT id, name FROM boxes WHERE name LIKE ?", (f"%{keyword}%",))
    results = cursor.fetchall()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.CYAN + "\nSearch results:")
    for box in results:
        print(f"{Fore.MAGENTA}[{box[0]:>4}]{Style.RESET_ALL} {box[1]}")
    if not results:
        print(Fore.YELLOW + "\n" + "=" * 30)
        print(Fore.YELLOW + "No matching boxes.")

def search_item():
    keyword = input("Search item name: ").strip()
    cursor.execute("""
    SELECT items.id, items.name, boxes.name, items.quantity
    FROM items
    LEFT JOIN boxes ON items.box_id = boxes.id
    WHERE items.name LIKE ?
    """, (f"%{keyword}%",))
    results = cursor.fetchall()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.CYAN + "\nSearch results:")
    for item in results:
        item_id = f"[{item[0]:>4}]"
        name = f"{item[1]:<40}"
        quantity = f"{item[3]:>4}"
        print(f"{Fore.MAGENTA}{item_id}{Style.RESET_ALL} {name} | {Fore.BLUE}{quantity}{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}(Box: {item[2]})")
    if not results:
        print(Fore.YELLOW + "\n" + "=" * 30)
        print(Fore.YELLOW + "No matching items.")

def edit_box_name():
    list_boxes()
    box_id = input("Enter box ID to rename: ").strip()
    new_name = input("Enter new box name: ").strip()
    cursor.execute("UPDATE boxes SET name = ? WHERE id = ?", (new_name, box_id))
    conn.commit()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.GREEN + "Box renamed.")

def edit_item_name():
    list_items()
    item_id = input("Enter item ID to rename: ").strip()
    new_name = input("Enter new item name: ").strip()
    cursor.execute("UPDATE items SET name = ? WHERE id = ?", (new_name, item_id))
    conn.commit()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.GREEN + "Item renamed.")

def edit_item_quantity():
    list_items()
    item_id = input("Enter item ID to change quantity: ").strip()
    new_qty = input("Enter new quantity: ").strip()
    if new_qty.isdigit():
        cursor.execute("UPDATE items SET quantity = ? WHERE id = ?", (int(new_qty), item_id))
        conn.commit()
        print(Fore.YELLOW + "\n" + "=" * 30)
        print(Fore.GREEN + "Quantity updated.")
    else:
        print(Fore.YELLOW + "\n" + "=" * 30)
        print(Fore.RED + "Invalid quantity.")

def move_item():
    list_items()
    item_id = input("Enter item ID to move: ").strip()
    list_boxes()
    new_box_id = input("Enter new box ID: ").strip()
    cursor.execute("UPDATE items SET box_id = ? WHERE id = ?", (new_box_id, item_id))
    conn.commit()
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.GREEN + "Item moved successfully.")

def list_items_by_box():
    list_boxes()
    box_id = input("Enter box ID to view its items: ").strip()
    cursor.execute("""
        SELECT items.id, items.name, items.quantity
        FROM items
        WHERE box_id = ?
    """, (box_id,))
    items = cursor.fetchall()

    cursor.execute("SELECT name FROM boxes WHERE id = ?", (box_id,))
    box = cursor.fetchone()

    if not box:
        print(Fore.RED + "Box not found.")
        return
    print(Fore.YELLOW + "\n" + "=" * 30)
    print(Fore.CYAN + f"\nItems in box '{box[0]}':")
    if items:
        for item in items:
            item_id = f"[{item[0]:>4}]"
            name = f"{item[1]:<40}"
            quantity = f"{item[2]:>4}"
            print(f"{Fore.MAGENTA}{item_id}{Style.RESET_ALL} {name} | {Fore.BLUE}{quantity}{Style.RESET_ALL}")
    else:
        print(Fore.YELLOW + "No items in this box.")

def menu():
    while True:
        print(Fore.YELLOW + "=" * 30)
        print(Fore.CYAN + "         INVENTORY MENU")
        print(Fore.YELLOW + "=" * 30 + Style.RESET_ALL)

        # Additions - GREEN
        print(f"{Fore.GREEN} 1. Add Box {Style.RESET_ALL}")
        print(f"{Fore.GREEN} 3. Add Item {Style.RESET_ALL}")

        # Removals - RED
        print(f"{Fore.RED} 2. Delete Box {Style.RESET_ALL}")
        print(f"{Fore.RED} 4. Delete Item {Style.RESET_ALL}")

        # Listings - YELLOW
        print(f"{Fore.YELLOW} 5. List Boxes {Style.RESET_ALL}")
        print(f"{Fore.YELLOW} 6. List Items {Style.RESET_ALL}")
        print(f"{Fore.YELLOW}13. List Items by Box {Style.RESET_ALL}")

        # Searches - CYAN
        print(f"{Fore.CYAN} 7. Search Box {Style.RESET_ALL}")
        print(f"{Fore.CYAN} 8. Search Item {Style.RESET_ALL}")

        # Edits & Moves - CYAN
        print(f"{Fore.CYAN} 9. Edit Box Name {Style.RESET_ALL}")
        print(f"{Fore.CYAN}10. Edit Item Name {Style.RESET_ALL}")
        print(f"{Fore.CYAN}11. Move Item {Style.RESET_ALL}")
        print(f"{Fore.CYAN}12. Edit Item Quantity {Style.RESET_ALL}")

        # Exit - CYAN or WHITE
        print(f"{Fore.RED}14. Exit\n")


        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_box()
        elif choice == "2":
            delete_box()
        elif choice == "3":
            add_item()
        elif choice == "4":
            delete_item()
        elif choice == "5":
            list_boxes()
        elif choice == "6":
            list_items()
        elif choice == "7":
            search_box()
        elif choice == "8":
            search_item()
        elif choice == "9":
            edit_box_name()
        elif choice == "10":
            edit_item_name()
        elif choice == "11":
            move_item()
        elif choice == "12":
            edit_item_quantity()
        elif choice == "13":
            list_items_by_box()
        elif choice == "14":
            print(Fore.YELLOW + "Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
    conn.close()

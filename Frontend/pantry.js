const API_URL = "http://127.0.0.1:8000/api";
const USER_ID = 1;

document.addEventListener("DOMContentLoaded", fetchPantryItems);

async function fetchPantryItems() {
    try {
        const response = await fetch(`${API_URL}/users/${USER_ID}/pantry`);
        const data = await response.json();
        
        const tableBody = document.getElementById("pantry-table-body");
        tableBody.innerHTML = "";

        if (Array.isArray(data) && data.length > 0) {
            data.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.ingredient_name || 'Ingredient #' + item.id}</td>
                    <td>${item.amount}</td>
                    <td>${item.unit}</td>
                    <td>
                        <button style="color: var(--danger-red); border:none; background:none; cursor:pointer;" onclick="deletePantryItem(${item.id})">Remove</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No items in your pantry.</td></tr>`;
        }
    } catch (error) {
        console.error("Error fetching pantry items:", error);
    }
}

document.getElementById("pantry-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const payload = {
        ingredient_id: parseInt(document.getElementById("pantry-ing-id").value),
        amount: parseFloat(document.getElementById("pantry-amount").value),
        unit: document.getElementById("pantry-unit").value
    };

    try {
        const response = await fetch(`${API_URL}/users/${USER_ID}/pantry`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            document.getElementById("pantry-form").reset();
            fetchPantryItems();
        }
    } catch (error) {
        console.error("Error adding pantry item:", error);
    }
});

async function deletePantryItem(pantryId) {
    try {
        const response = await fetch(`${API_URL}/pantry/${pantryId}`, {
            method: "DELETE"
        });

        if (response.ok) {
            fetchPantryItems();
        }
    } catch (error) {
        console.error("Error deleting pantry item:", error);
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const signinBtn = document.querySelector(".btn-signin");
    if (!signinBtn) return;

    const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";

    if (isLoggedIn) {
        signinBtn.textContent = "Logout";
        signinBtn.href = "#";
        signinBtn.addEventListener("click", (e) => {
            e.preventDefault();
            localStorage.removeItem("isLoggedIn");
            window.location.href = "index.html";
        });
    } else {
        signinBtn.textContent = "Sign in";
        signinBtn.href = "login.html";
    }
});
try {
   
    const response = await fetch('YOUR_API_URL');
    if (!response.ok) {
        throw new Error('Item or ID not found. Please check your input.');
    }
    const data = await response.json();
    
} catch (error) {
    const resultBox = document.querySelector('.result-box') || document.getElementById('error-message');
    if (resultBox) {
        resultBox.style.color = '#E11D48';
        resultBox.textContent = `⚠️ Error: ${error.message}`;
    } else {
        alert(error.message);
    }
}
function renderPantryTable(items) {
    const tbody = document.querySelector('.data-table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    items.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>#${item.id}</strong></td>
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td><button onclick="deleteItem(${item.id})">Delete</button></td>
        `;
        tbody.appendChild(row);
    });
}

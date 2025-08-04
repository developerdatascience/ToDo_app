
const rowsPerPage = 5;
const table = document.querySelector(".styled-table tbody");
const rows = table.querySelectorAll("tr");
const pagination = document.getElementById("pagination");

function showPage(page) {
    let start = (page - 1) * rowsPerPage;
    let end = start + rowsPerPage;

    rows.forEach((row, index) => {
        row.style.display = index >= start && index < end ? "" : "none";
    });
}

function setupPagination() {
    let totalPages = Math.ceil(rows.length / rowsPerPage);
    pagination.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
        let btn = document.createElement("button");
        btn.textContent = i;
        btn.style.margin = "0 5px";
        btn.style.padding = "6px 12px";
        btn.style.border = "1px solid #ccc";
        btn.style.borderRadius = "4px";
        btn.style.cursor = "pointer";
        btn.addEventListener("click", () => showPage(i));
        pagination.appendChild(btn);
    }

    showPage(1);
}

if (rows.length > rowsPerPage) {
    setupPagination();
}


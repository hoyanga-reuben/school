document.addEventListener("DOMContentLoaded", function () {
    // Remove any static placeholder rows before initializing DataTable
    $('#transfersTable .no-data').remove();

    // Initialize DataTable
    const table = $('#transfersTable').DataTable();

    // Live search
    $('#searchInput').on('keyup', function () {
        table.search(this.value).draw();
    });

    // Toggle Dark Mode
    $('#darkModeToggle').click(function () {
        $('body').toggleClass('dark-mode');
    });

    // Parse notifications from JSON embedded in HTML
    let notifications = [];
    const notifElement = document.getElementById('notif-data');
    if (notifElement) {
        try {
            notifications = JSON.parse(notifElement.textContent || "[]");
        } catch (e) {
            console.error("Failed to parse notifications JSON:", e);
        }
    }

    // Update notification count and dropdown
    $('#notifCount').text(notifications.length);
    const dropdown = $('#notificationDropdown');
    if (notifications.length === 0) {
        dropdown.append('<div class="dropdown-item">No notifications</div>');
    } else {
        notifications.forEach(note => {
            dropdown.append(`<div class="dropdown-item">${note}</div>`);
        });
    }

    // Toggle dropdown display
    $('#notificationBtn').click(() => {
        $('#notificationDropdown').toggle();
    });
});

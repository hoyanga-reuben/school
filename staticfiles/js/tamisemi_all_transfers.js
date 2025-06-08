document.addEventListener("DOMContentLoaded", function () {
    // Initialize DataTable
    const table = $('#transfersTable').DataTable();

    // Search functionality
    $('#searchInput').on('keyup', function () {
        table.search(this.value).draw();
    });

    // Toggle Dark Mode
    $('#darkModeToggle').click(function () {
        $('body').toggleClass('dark-mode');
    });

    // Load notifications
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

    // Toggle notifications dropdown
    $('#notificationBtn').click(() => {
        dropdown.toggle();
    });

    // Approve button handler (optional future feature)
    $('.btn-approve').click(function () {
        const id = $(this).data('id');
        Swal.fire({
            title: 'Approve this request?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Yes, approve',
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = `/tamisemi/approve_transfer/${id}/`;
            }
        });
    });

    // Reject button handler (optional future feature)
    $('.btn-reject').click(function () {
        const id = $(this).data('id');
        Swal.fire({
            title: 'Reject this request?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, reject',
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = `/tamisemi/reject_transfer/${id}/`;
            }
        });
    });
});

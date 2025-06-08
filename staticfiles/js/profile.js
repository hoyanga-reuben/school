document.addEventListener("DOMContentLoaded", function () {
    // Dark mode toggle
    $('#darkModeToggle').click(function () {
        $('body').toggleClass('dark-mode');
    });

    // Example notifications - you can load these via JSON if needed
    const notifications = [
        "Your profile has been updated successfully",
        "1 transfer request needs attention"
    ];

    $('#notifCount').text(notifications.length);
    notifications.forEach(note => {
        $('#notificationDropdown').append(`<div class="dropdown-item">${note}</div>`);
    });

    $('#notificationBtn').click(() => {
        $('#notificationDropdown').toggle();
    });
});

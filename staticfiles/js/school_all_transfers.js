$(document).ready(function () {
    // Initialize DataTable
    $('#transfersTable').DataTable({
        responsive: true,
        pageLength: 10
    });

    // Search filter
    $('#searchInput').on('keyup', function () {
        $('#transfersTable').DataTable().search(this.value).draw();
    });

    // Display dynamic notifications
    if (typeof schoolNotifications !== 'undefined' && schoolNotifications.length > 0) {
        Swal.fire({
            title: 'Notifications',
            html: '<ul style="text-align: left;">' + schoolNotifications.map(n => `<li>${n}</li>`).join('') + '</ul>',
            icon: 'info',
            confirmButtonText: 'Close',
            confirmButtonColor: '#3085d6'
        });
    }
});

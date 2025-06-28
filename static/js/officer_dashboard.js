$(document).ready(function () {
    // Initialize DataTable
    const table = $('#transfersTable').DataTable({
        language: {
            emptyTable: "No transfer requests available"
        }
    });

    // Search functionality
    $('#searchInput').on('keyup', function () {
        table.search(this.value).draw();
    });

    // SweetAlert confirmation for Approve/Reject
    $('.btn-approve, .btn-reject').click(function (e) {
        e.preventDefault();
        const href = $(this).attr('href');
        const name = $(this).data('name');
        const isApprove = $(this).hasClass('btn-approve');

        Swal.fire({
            title: isApprove ? 'Approve this request?' : 'Reject this request?',
            text: `Teacher: ${name}`,
            icon: isApprove ? 'question' : 'warning',
            showCancelButton: true,
            confirmButtonText: isApprove ? 'Yes, approve' : 'Yes, reject',
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = href;
            }
        });
    });
});
$(document).ready(function () {
    // --- Existing Functionalities (Your Code) ---

    // Initialize DataTable
    const table = $('#transfersTable').DataTable({
        language: {
            emptyTable: "No transfer requests available"
        }
    });

    // Search functionality
    $('#searchInput').on('keyup', function () {
        table.search(this.value).draw();
    });

    // SweetAlert confirmation for Approve/Reject
    $('.btn-approve, .btn-reject').click(function (e) {
        e.preventDefault();
        const href = $(this).attr('href');
        const name = $(this).data('name'); // Make sure your HTML for these buttons has data-name attribute
        const isApprove = $(this).hasClass('btn-approve');

        Swal.fire({
            title: isApprove ? 'Approve this request?' : 'Reject this request?',
            text: `Teacher: ${name}`,
            icon: isApprove ? 'question' : 'warning',
            showCancelButton: true,
            confirmButtonText: isApprove ? 'Yes, approve' : 'Yes, reject',
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = href;
            }
        });
    });

    // Sidebar active link highlighting (from previous discussions)
    document.querySelectorAll('.sidebar-links a').forEach(link => {
      if (link.href === window.location.href) {
        link.classList.add('active');
      }
    });


    // --- Dark Mode Functionality (New Code) ---

    // Function to apply the dark mode preference from localStorage
    function applyDarkModePreference() {
        const isDarkModeEnabled = localStorage.getItem('darkMode') === 'enabled';
        if (isDarkModeEnabled) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }

    // Apply dark mode preference on page load
    // This needs to be called within $(document).ready() if you want it to run after jQuery is ready
    // Or, better yet, call it outside if it only depends on document.body existing, for faster application
    applyDarkModePreference();

    // Event listener for the dark mode toggle button
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');

            // Save preference to localStorage
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
            } else {
                localStorage.setItem('darkMode', 'disabled');
            }
        });
    }
});
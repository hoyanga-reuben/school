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

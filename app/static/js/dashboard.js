// Dashboard specific JS
$(document).ready(function () {
    if ($('#dashboard-summary').length) {
        loadDashboardSummary();
        loadRecentReservations();
    }
});

function loadDashboardSummary() {
    $.get('/api/dashboard/summary', function (data) {
        $('#summary-pending').text(data.PENDING || 0);
        $('#summary-booked').text(data.BOOKED || 0);
        $('#summary-checked-in').text(data.CHECKED_IN || 0);
        $('#summary-checked-out').text(data.CHECKED_OUT || 0);
        $('#summary-cancelled').text(data.CANCELLED || 0);
    });
}

function loadRecentReservations() {
    $.get('/api/reservations?status=PENDING', function (data) {
        const tbody = $('#recent-reservations-body');
        tbody.empty();
        data.forEach(res => {
            tbody.append(`
                <tr>
                    <td>${res.id}</td>
                    <td>${res.guest_name}</td>
                    <td>${res.check_in_date}</td>
                    <td>${res.status}</td>
                    <td><a href="/admin/reservations">Manage</a></td>
                </tr>
            `);
        });
    });
}

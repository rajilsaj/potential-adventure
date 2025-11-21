// Reservations management JS
$(document).ready(function () {
    if ($('#reservations-table').length) {
        loadAdminReservations();
    }
});

function loadAdminReservations() {
    $.get('/api/reservations', function (reservations) {
        const tbody = $('#reservations-table-body');
        tbody.empty();
        reservations.forEach(res => {
            tbody.append(`
                <tr>
                    <td>${res.id}</td>
                    <td>${res.guest_name}</td>
                    <td>${res.room_id}</td>
                    <td>${res.check_in_date} to ${res.check_out_date}</td>
                    <td>
                        <select onchange="updateReservationStatus(${res.id}, this.value)">
                            <option value="PENDING" ${res.status === 'PENDING' ? 'selected' : ''}>PENDING</option>
                            <option value="BOOKED" ${res.status === 'BOOKED' ? 'selected' : ''}>BOOKED</option>
                            <option value="CHECKED_IN" ${res.status === 'CHECKED_IN' ? 'selected' : ''}>CHECKED_IN</option>
                            <option value="CHECKED_OUT" ${res.status === 'CHECKED_OUT' ? 'selected' : ''}>CHECKED_OUT</option>
                            <option value="CANCELLED" ${res.status === 'CANCELLED' ? 'selected' : ''}>CANCELLED</option>
                        </select>
                    </td>
                </tr>
            `);
        });
    });
}

function updateReservationStatus(id, status) {
    $.ajax({
        url: `/api/reservations/${id}`,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({ status: status }),
        success: function () {
            // Optional: show toast
        }
    });
}

$(document).ready(function () {
    // Login Logic
    $('#login-form').on('submit', function (e) {
        e.preventDefault();
        const username = $('#username').val();
        const password = $('#password').val();

        $.ajax({
            url: '/api/auth/login',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username, password }),
            success: function (response) {
                window.location.href = '/admin/dashboard';
            },
            error: function () {
                $('#login-error').text('Invalid credentials');
            }
        });
    });

    // Logout Logic
    $('#logout-btn').on('click', function () {
        $.post('/api/auth/logout', function () {
            window.location.href = '/admin/login';
        });
    });

    // Dashboard Logic
    if ($('#dashboard-summary').length) {
        loadDashboardSummary();
        loadRecentReservations();
    }

    // Rooms Management Logic
    if ($('#rooms-table').length) {
        loadAdminRooms();

        $('#create-room-form').on('submit', function (e) {
            e.preventDefault();
            const data = {
                room_number: $('#room_number').val(),
                floor: $('#floor').val(),
                room_type: $('#room_type').val(),
                capacity: $('#capacity').val(),
                base_price: $('#base_price').val(),
                status: 'AVAILABLE'
            };

            $.ajax({
                url: '/api/rooms',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function () {
                    alert('Room created');
                    loadAdminRooms();
                    $('#create-room-form')[0].reset();
                },
                error: function (xhr) {
                    alert('Error: ' + xhr.responseJSON.error);
                }
            });
        });
    }

    // Reservations Management Logic
    if ($('#reservations-table').length) {
        loadAdminReservations();
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

function loadAdminRooms() {
    $.get('/api/rooms', function (rooms) {
        const tbody = $('#rooms-table-body');
        tbody.empty();
        rooms.forEach(room => {
            tbody.append(`
                <tr>
                    <td>${room.room_number}</td>
                    <td>${room.room_type}</td>
                    <td>${room.status}</td>
                    <td>$${room.base_price}</td>
                    <td>
                        <button onclick="updateRoomStatus(${room.id}, 'AVAILABLE')">Set Available</button>
                        <button onclick="updateRoomStatus(${room.id}, 'OUT_OF_SERVICE')">Set Maintenance</button>
                    </td>
                </tr>
            `);
        });
    });
}

function updateRoomStatus(id, status) {
    $.ajax({
        url: `/api/rooms/${id}`,
        method: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({ status: status }),
        success: function () {
            loadAdminRooms();
        }
    });
}

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

// Rooms management JS
$(document).ready(function () {
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
});

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

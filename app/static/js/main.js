$(document).ready(function () {
    // Load rooms on index page
    if ($('#rooms-list').length) {
        loadRooms();
    }

    // Handle reservation form submission
    $('#reservation-form').on('submit', function (e) {
        e.preventDefault();

        const formData = {
            guest_name: $('#guest_name').val(),
            guest_email: $('#guest_email').val(),
            room_id: $('#room_id').val(),
            check_in_date: $('#check_in_date').val(),
            check_out_date: $('#check_out_date').val()
        };

        $.ajax({
            url: '/api/reservations',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                alert('Reservation created successfully! ID: ' + response.id);
                $('#reservation-form')[0].reset();
            },
            error: function (xhr) {
                alert('Error: ' + (xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error'));
            }
        });
    });
});

function loadRooms() {
    const roomImages = [
        "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1591088398332-8a7791972843?w=800&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800&auto=format&fit=crop&q=60"
    ];

    $.get('/api/rooms', function (rooms) {
        const container = $('#rooms-list');
        const select = $('#room_id');
        container.empty();
        select.empty();
        select.append('<option value="">Select a Room</option>');

        rooms.forEach((room, index) => {
            // Pick a random image or cycle through
            const imgUrl = roomImages[index % roomImages.length];

            // Status badge styling
            let statusClass = 'bg-green-100 text-green-800';
            if (room.status !== 'AVAILABLE') statusClass = 'bg-red-100 text-red-800';

            // Add to grid
            const card = `
                <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition duration-300 transform hover:-translate-y-1 flex flex-col">
                    <div class="h-48 overflow-hidden">
                        <img src="${imgUrl}" alt="Room ${room.room_number}" class="w-full h-full object-cover transition duration-500 hover:scale-110">
                    </div>
                    <div class="p-6 flex-grow">
                        <div class="flex justify-between items-start mb-4">
                            <div>
                                <h3 class="text-xl font-bold text-gray-800">Room ${room.room_number}</h3>
                                <p class="text-sm text-gray-500 uppercase tracking-wide font-semibold">${room.room_type}</p>
                            </div>
                            <span class="px-3 py-1 rounded-full text-xs font-bold ${statusClass}">
                                ${room.status}
                            </span>
                        </div>
                        
                        <div class="flex items-center text-gray-600 mb-2">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                            <span>Floor ${room.floor}</span>
                        </div>
                        <div class="flex items-center text-gray-600 mb-4">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 005.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                            <span>Capacity: ${room.capacity} Person(s)</span>
                        </div>
                    </div>
                    <div class="px-6 py-4 bg-gray-50 border-t flex justify-between items-center">
                        <span class="text-2xl font-bold text-blue-600">$${room.base_price}<span class="text-sm text-gray-500 font-normal">/night</span></span>
                        ${room.status === 'AVAILABLE' ?
                    `<button onclick="$('#room_id').val(${room.id}); document.getElementById('reservation-form').scrollIntoView({behavior: 'smooth'});" class="text-blue-600 hover:text-blue-800 font-semibold text-sm focus:outline-none">Select Room &rarr;</button>` :
                    `<span class="text-gray-400 text-sm font-medium">Unavailable</span>`
                }
                    </div>
                </div>
            `;
            container.append(card);

            // Add to select if available
            if (room.status === 'AVAILABLE') {
                select.append(`<option value="${room.id}">Room ${room.room_number} (${room.room_type}) - $${room.base_price}</option>`);
            }
        });
    });
}

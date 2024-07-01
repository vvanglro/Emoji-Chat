async function joinRoomChat(room_id = null) {
    try {
        const response = await fetch(`/api/newchat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ room_id: room_id })
        });

        if (response.ok) {
            window.location.href = `/chat?room_id=${room_id}`;
        } else {
            console.error('Error:', response.statusText);
            alert('Failed to start a new chat session. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong. Please try again.');
    }
}

// 展示房间列表
function show_room_list(room_list) {
    const new_room = (data) => {
        return `<li class="list-group-item">
            <div class="row align-items-start">
                <div class="col">
                    ${data.room_id}
                </div>
                <div class="col">
                    <span class="badge text-bg-primary">${data.member_count}</span>
                </div>
                <div class="col">
                    <button type="button" class="btn btn-primary" onclick="joinRoomChat('${data.room_id}')">Join</button>
                </div>
            </div>
        </li>`;
    }

    let room_dom = "";
    for (let room of room_list) {
        room_dom += new_room(room)
    }

    document.querySelector("#room_list > ul").innerHTML = room_dom;
}

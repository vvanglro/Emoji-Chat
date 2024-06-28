async function startNewChat(room_id = null) {
    // 生成 UUID
    room_id = room_id || generateUUID();
    const apiHost = window.location.host;  // 替换为你的后端API地址

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

// 简单的UUID生成器
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
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
                    <button type="button" class="btn btn-primary" onclick="startNewChat('${data.room_id}')">Join</button>
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


(async function () {
    // 初始化房间列表
    try {
        const response = await (await fetch(`/room/query`)).json();
        // 按照房间人数降序排列
        show_room_list(response.data.toSorted((a, b) => a.member_count - b.member_count > 0 ? -1 : 1))
    } catch (error) {
        console.error('Error:', error);
        alert('Something went wrong. Please try again.');
    }
})()

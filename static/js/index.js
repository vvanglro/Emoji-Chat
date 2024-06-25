async function startNewChat() {
    // 生成 UUID
    const room_id = generateUUID();
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
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

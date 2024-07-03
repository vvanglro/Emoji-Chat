async function startNewChat() {
  try {
    const response = await fetch(`/api/newchat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json(); // 解析 JSON 数据
      const groupId = data.group_id; // 取出 group_id
      window.location.href = `/chat?group_id=${groupId}`;
    } else {
      console.error("Error:", response.statusText);
      alert("Failed to start a new chat session. Please try again.");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Something went wrong. Please try again.");
  }
}

// 简单的UUID生成器
function generateUUID() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0,
      v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

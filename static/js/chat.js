const urlParams = new URLSearchParams(window.location.search);
const group_id = urlParams.get("group_id");
console.log(">>> group_id: ", group_id);
const apiHost = window.location.host; // 替换为你的后端API地址

const emojis = [
  "😀",
  "😁",
  "😂",
  "😃",
  "😄",
  "😅",
  "😆",
  "😉",
  "😊",
  "😋",
  "😎",
  "😍",
  "😘",
  "😗",
  "😙",
  "😚",
  "😇",
  "😐",
  "😑",
  "😶",
  "😏",
  "😣",
  "😥",
  "😮",
  "😯",
  "😪",
  "😫",
  "😴",
  "😌",
  "😛",
  "😜",
  "😝",
  "😒",
  "😓",
  "😔",
  "😕",
  "😲",
  "😷",
  "😖",
  "😞",
  "😟",
  "😤",
  "😢",
  "😭",
  "😦",
  "😧",
  "😨",
  "😬",
  "😰",
  "😱",
  "😳",
  "😵",
  "😡",
  "😠",
];
const userEmoji = emojis[Math.floor(Math.random() * emojis.length)];
const uid = setdefault_uid(userEmoji.codePointAt());
const ws = new WebSocket(`/ws/${group_id}/${uid.split("#")[1]}`);
const responseCache = {}; // 缓存API响应
let canSendMessage = true; // 控制是否可以发送消息的标志

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log(">>> data", data);
  if (data.code || data.code === 10401) {
    alert(data.msg);
  }
  displayMessage(data.emoji_msg, data.uid, false, data.msg);
};

document
  .getElementById("messageText")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });

// 简单的UUID生成器
function generateUUID() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0,
      v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function setdefault_uid(user_id) {
  let uid = localStorage.getItem("uid");
  if (uid === null) {
    uid = user_id + "#" + generateUUID();
    localStorage.setItem("uid", uid);
  }
  return uid;
}

async function loadMessage() {
  // 加载消息
  const response = await (
    await fetch(`/mesage/query?group_id=${group_id}`)
  ).json();
  console.log("load", response);
  response.data.forEach(({ emoji_msg, uid, msg }) => {
    displayMessage(emoji_msg, uid, true, msg);
  });
}

function sendMessage() {
  if (!canSendMessage) {
    alert("You can only send one message every one seconds.");
    return;
  }

  const input = document.getElementById("messageText");
  const message = input.value;
  if (message.trim() !== "") {
    displayMessage(message, uid);
    let msg = {
      group_id: group_id,
      uid: uid,
      msg: message,
    };
    ws.send(JSON.stringify(msg));
    input.value = "";
    canSendMessage = false;
    setTimeout(() => (canSendMessage = true), 1000);
  }
}

async function handleApiMessageClick(event) {
  const messageElement = event.currentTarget;
  const messageText = messageElement.querySelector(".text-content").textContent;

  if (messageElement.querySelector(".response-content")) {
    messageElement.querySelector(".response-content").remove();
  } else {
    const responseContent = messageElement.getAttribute("data-response-msg");

    const responseDiv = document.createElement("div");
    responseDiv.classList.add("response-content");
    responseDiv.textContent = responseContent;

    messageElement.appendChild(responseDiv);
  }
}

function displayMessage(message, from_uid, load = false, responseMsg = null) {
  const messages = document.getElementById("messages");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add(
    "d-flex",
    "align-items-start",
    "mb-3",
    "user-message",
  );

  const avatarDiv = document.createElement("div");
  avatarDiv.textContent = String.fromCodePoint(from_uid.split("#")[0]);
  avatarDiv.classList.add("avatar");
  avatarDiv.style.fontSize = "50px";
  avatarDiv.style.lineHeight = "50px";
  avatarDiv.style.marginRight = "10px";

  const messageContent = document.createElement("div");
  messageContent.classList.add(
    "message-content-container",
    "p-2",
    "border",
    "rounded",
  );

  if (from_uid === uid) {
    messageDiv.classList.add("flex-row-reverse");
    messageContent.classList.add("bg-primary");
    //<!--            messageContent.classList.add('text-white');-->
    if (load) {
      messageContent.classList.add("bg-light");
    }
  } else {
    messageContent.classList.add("bg-light");
  }

  if (responseMsg) {
    messageContent.setAttribute("data-response-msg", responseMsg);
    messageContent.onclick = handleApiMessageClick; // 添加点击事件
  }

  const textContent = document.createElement("div");
  textContent.classList.add("text-content");
  textContent.textContent = message;

  messageContent.appendChild(textContent);
  messageContent.style.position = "relative";

  messageDiv.appendChild(avatarDiv);
  messageDiv.appendChild(messageContent);
  messages.appendChild(messageDiv);
  messages.scrollTop = messages.scrollHeight;
}

loadMessage();

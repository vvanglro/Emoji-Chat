function show_room_list(room_list) {
  const new_room = (data) => {
    // 使用模板字面量来构造 URL
    const url = `/chat?group_id=${data.group_id}`;
    return `<li class="list-group-item">
  <div class="row align-items-start">
    <div class="col">${data.group_id}</div>
    <div class="col">
      <span class="badge text-bg-primary">${data.member_count}</span>
    </div>
    <div class="col">
      <a
        href="/chat?group_id=${encodeURIComponent(data.group_id)}"
        class="btn btn-primary"
        >Join</a
      >
    </div>
  </div>
</li>
`;
  };

  let room_dom = "";
  for (let room of room_list) {
    room_dom += new_room(room);
  }

  document.querySelector("#room_list > ul").innerHTML = room_dom;
}

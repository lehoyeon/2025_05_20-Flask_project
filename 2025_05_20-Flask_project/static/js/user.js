const userForm = document.getElementById('userForm');
const usersTableBody = document.querySelector('#usersTable tbody');

    // 사용자 목록 불러오기
    function loadUsers() {
      fetch('/users')
        .then(res => res.json())
        .then(data => {
          usersTableBody.innerHTML = '';
          data.forEach(user => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${user.user_id}</td>
              <td><input class="table-input" type="text" value="${user.name}" data-id="${user.user_id}" /></td>
              <td><button class="update" data-id="${user.user_id}">수정</button></td>
              <td><button class="delete" data-id="${user.user_id}">삭제</button></td>
            `;
            usersTableBody.appendChild(tr);
          });
        });
    }

    // 등록 폼 제출 이벤트
    userForm.addEventListener('submit', e => {
      e.preventDefault();
      const name = userForm.userName.value.trim();
      if (!name) return alert('사용자 이름을 입력하세요.');

      fetch('/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message || '등록 완료');
        userForm.reset();
        loadUsers();
      });
    });

    // 수정, 삭제 이벤트 위임
    usersTableBody.addEventListener('click', e => {
      if (e.target.classList.contains('update')) {
        const id = e.target.dataset.id;
        const input = e.target.closest('tr').querySelector('input.table-input');
        const newName = input.value.trim();
        if (!newName) return alert('이름을 입력하세요.');

        fetch(`/users/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: newName })
        })
        .then(res => res.json())
        .then(data => {
          alert(data.message || '수정 완료');
          loadUsers();
        });
      } else if (e.target.classList.contains('delete')) {
        const id = e.target.dataset.id;
        if (!confirm('정말 삭제하시겠습니까?')) return;
        
        fetch(`/users/${id}`, { method: 'DELETE' })
          .then(res => res.json())
          .then(data => {
            alert(data.message || '삭제 완료');
            loadUsers();
          });
      }
    });

    // 초기 사용자 목록 로드
    loadUsers();